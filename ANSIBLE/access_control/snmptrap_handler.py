#!/usr/bin/env python3

import sys
import os
import time
import threading
import queue
import concurrent.futures
from typing import Dict, List, Optional

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE"))

from access_control.snmp_utils import buscar_mac_por_puerto_con_reintentos, limpiar_cache

import datetime
import json
import subprocess
import re

# Rutas
BASE_DIR = "/home/tdg2025/Escritorio/TDGRedes/ANSIBLE"
LOG_FILE = os.path.join(BASE_DIR, "access_control/logs/snmp_traps.log")
CONFIG_FILE = os.path.join(BASE_DIR, "access_control/config/dispositivos.json")

# Asegurar existencia del directorio de logs
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Variables globales para control de concurrencia
log_lock = threading.Lock()
playbook_execution_lock = threading.Lock()
trap_queue = queue.Queue()
active_playbooks = {}  # Puerto -> timestamp de ejecución activa
active_playbooks_lock = threading.Lock()

# Pool de threads para procesamiento de traps
MAX_CONCURRENT_TRAPS = 3
trap_executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TRAPS)

def cargar_configuracion():
    """
    Carga la configuración desde el archivo JSON especificado en CONFIG_FILE.

    Returns:
        dict: Diccionario con la configuración cargada.
    """
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR cargando configuración: {str(e)}")
        sys.exit(1)

def log(mensaje):
    """
    Registra un mensaje en el archivo de log de forma thread-safe.

    Args:
        mensaje (str): Mensaje a registrar.
    """
    with log_lock:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        thread_id = threading.current_thread().name
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] [Thread:{thread_id}] {mensaje}\n")

def obtener_dispositivo(ip, dispositivos_por_ip):
    """
    Obtiene el nombre del dispositivo asociado a una IP.

    Args:
        ip (str): Dirección IP del dispositivo.
        dispositivos_por_ip (dict): Diccionario de dispositivos por IP.

    Returns:
        str: Nombre del dispositivo o "DESCONOCIDO" si no se encuentra.
    """
    return dispositivos_por_ip.get(ip, "DESCONOCIDO")

def obtener_puerto(trap_data, ifindex_to_interface):
    """
    Extrae el puerto y su índice del trap SNMP recibido.

    Args:
        trap_data (str): Datos del trap SNMP.
        ifindex_to_interface (dict): Mapeo de índices a nombres de interfaces.

    Returns:
        tuple: Nombre del puerto y su índice.
    """
    puerto = "desconocido"
    puerto_index = "desconocido"
    for linea in trap_data.splitlines():
        if "ifDescr" in linea and "FastEthernet" in linea:
            partes = linea.strip().split(" = ")
            if len(partes) == 2 and "FastEthernet" in partes[1]:
                puerto = partes[1].replace("STRING: ", "").strip()
        elif "ifIndex" in linea and puerto == "desconocido":
            partes = linea.strip().split()
            for parte in partes:
                if parte.isdigit():
                    puerto_index = parte
                    puerto = ifindex_to_interface.get(puerto_index, "desconocido")
                    break
    return puerto, puerto_index

def detectar_mac(trap_data):
    """
    Extrae la dirección MAC del trap SNMP recibido.

    Args:
        trap_data (str): Datos del trap SNMP.

    Returns:
        str: Dirección MAC encontrada o None si no se encuentra.
    """
    mac_match = re.search(r"(([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})", trap_data)
    if mac_match:
        return mac_match.group(1)
    return None

def validar_puerto(puerto):
    """
    Valida y limpia el nombre del puerto.

    Args:
        puerto (str): Nombre del puerto.

    Returns:
        str: Nombre del puerto limpio.
    """
    return re.sub(r'[^A-Za-z0-9/]', '', puerto)

def determinar_evento(trap_data, acciones):
    """
    Determina el evento y la acción asociada al trap SNMP.

    Args:
        trap_data (str): Datos del trap SNMP.
        acciones (dict): Diccionario de acciones por palabra clave.

    Returns:
        tuple: Evento detectado y acción asociada.
    """
    evento = "TRAP DESCONOCIDO"
    accion = None
    for palabra_clave, (evento_detectado, accion_detectada) in acciones.items():
        if palabra_clave in trap_data:
            evento = evento_detectado
            accion = accion_detectada
            break
    return evento, accion

def puede_ejecutar_playbook(puerto: str) -> bool:
    """
    Verifica si se puede ejecutar un playbook en el puerto dado.
    Evita ejecuciones concurrentes en el mismo puerto.
    """
    with active_playbooks_lock:
        if puerto in active_playbooks:
            # Verificar si la ejecución anterior sigue activa (timeout de 5 minutos)
            tiempo_transcurrido = time.time() - active_playbooks[puerto]
            if tiempo_transcurrido < 300:  # 5 minutos
                log(f"Playbook ya ejecutándose en puerto {puerto} (hace {tiempo_transcurrido:.1f}s)")
                return False
            else:
                # Timeout alcanzado, permitir nueva ejecución
                log(f"Timeout de playbook anterior en puerto {puerto}, permitiendo nueva ejecución")
                del active_playbooks[puerto]
        
        # Marcar puerto como en uso
        active_playbooks[puerto] = time.time()
        return True

def marcar_playbook_completado(puerto: str) -> None:
    """Marca que la ejecución del playbook en el puerto ha completado."""
    with active_playbooks_lock:
        if puerto in active_playbooks:
            del active_playbooks[puerto]
            log(f"Playbook completado en puerto {puerto}")

def ejecutar_playbook(mac_address, puerto, vlan_id, playbook):
    """
    Ejecuta un playbook de Ansible con control de concurrencia.

    Args:
        mac_address (str): Dirección MAC del dispositivo.
        puerto (str): Puerto en el que se encuentra el dispositivo.
        vlan_id (str): ID de la VLAN a configurar.
        playbook (str): Ruta del playbook a ejecutar.
    """
    if not puede_ejecutar_playbook(puerto):
        log(f"Ejecución de playbook cancelada para puerto {puerto} - ya hay una ejecución activa")
        return
    
    try:
        with playbook_execution_lock:  # Serializar ejecuciones de Ansible
            os.chdir("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE")
            
            env = os.environ.copy()
            env["MAC_ADDRESS"] = mac_address
            env["PUERTO"] = puerto
            if vlan_id:
                env["VLAN_ID"] = str(vlan_id)
            
            log(f"Ejecutando playbook {playbook} para MAC {mac_address} en puerto {puerto}")
            
            result = subprocess.run(
                ["ansible-playbook", playbook],
                env=env,
                capture_output=True,
                text=True,
                timeout=120  # Timeout de 2 minutos
            )
            
            if result.returncode == 0:
                log(f"Playbook {playbook} ejecutado exitosamente")
            else:
                log(f"Error ejecutando playbook {playbook}: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        log(f"Timeout ejecutando playbook {playbook} para puerto {puerto}")
    except Exception as e:
        log(f"ERROR ejecutando playbook: {str(e)}")
    finally:
        marcar_playbook_completado(puerto)

def limpiar_puerto(puerto):
    """
    Limpia la configuración de un puerto en el switch.

    Args:
        puerto (str): Nombre del puerto a limpiar.
    """
    os.chdir("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE")
    try:
        result = subprocess.run([
            "ansible-playbook",
            "playbooks/limpiar_puerto.yml",
            "--extra-vars", f"interface_name={puerto}"
        ], capture_output=True, text=True)

        log(f"Playbook de limpieza ejecutado para el puerto {puerto}. Salida:\n{result.stdout}\nErrores:\n{result.stderr}")
    except Exception as e:
        log(f"ERROR ejecutando playbook de limpieza: {str(e)}")

def procesar_trap_async(trap_data: str) -> None:
    """
    Procesa un trap SNMP de forma asíncrona.
    
    Args:
        trap_data: Datos del trap SNMP recibido
    """
    try:
        log(f"Iniciando procesamiento asíncrono de trap")
        
        config = cargar_configuracion()
        dispositivos_por_ip = config.get("dispositivos_por_ip", {})
        ifindex_to_interface = config.get("ifindex_to_interface", {})
        acciones = config.get("acciones", {})

        # Detectar IP de origen
        ip_origen_aux = re.search(r'UDP/IPv6:\s+\[([0-9a-fA-F:]+)\]', trap_data)
        if ip_origen_aux:
            ip_origen = ip_origen_aux.group(1)
        else:
            ip_origen = "desconocido"
        dispositivo = obtener_dispositivo(ip_origen, dispositivos_por_ip)

        # Detectar evento y acción
        evento, accion = determinar_evento(trap_data, acciones)

        # Detectar puerto
        puerto, puerto_index = obtener_puerto(trap_data, ifindex_to_interface)
        
        # Filtrar eventos usando la lista de puertos físicos configurados
        if puerto_index.isdigit():
            if puerto_index not in ifindex_to_interface:
                log(f"Evento ignorado: ifIndex {puerto_index} no está configurado como puerto físico")
                return
        else:
            log(f"Evento ignorado: puerto_index no válido ({puerto_index})")
            return

        # Obtener dirección MAC mediante SNMP polling con reintentos
        mac_address = None
        log(f"Procesando evento para puerto físico configurado ifIndex {puerto_index}...")
        mac_address = buscar_mac_por_puerto_con_reintentos(
            ip_origen, int(puerto_index), ifindex_validos=ifindex_to_interface
        )

        if not mac_address:
            log("No se pudo obtener la dirección MAC mediante SNMP polling con reintentos.")
            mac_address = "desconocida"

        log_entry = (
            f"Evento: {evento}\n"
            f"Dispositivo: {dispositivo} IP origen: {ip_origen}\n"
            f"Puerto detectado: {puerto} (Index {puerto_index})\n"
            f"MAC detectada: {mac_address}\n"
            f"{trap_data}\n{'-'*60}\n"
        )
        log(log_entry)

        puerto = validar_puerto(puerto)

        if accion == "conectar" and puerto != "desconocido" and mac_address != "desconocida":
            vlan_id = config.get("vlan_por_mac", {}).get(mac_address)
            log(f"Creando o actualizando VLAN {vlan_id} para MAC {mac_address}")
            
            # Ejecutar playbook en thread separado para no bloquear
            def ejecutar_vlan_config():
                ejecutar_playbook(mac_address, puerto, vlan_id, "playbooks/vlan_config.yml")
                time.sleep(15)
                if vlan_id:
                    log(f"Esperando para que la VLAN {vlan_id} se estabilice...")
                    time.sleep(5)
                    log(f"Configurando VLAN {vlan_id} en puerto {puerto} para MAC {mac_address}...")
                    ejecutar_playbook(mac_address, puerto, vlan_id, "playbooks/asignar_vlanxmac.yml")
                else:
                    log(f"No se encontró una VLAN asignada para la MAC {mac_address}.")
            
            # Ejecutar en thread separado
            config_thread = threading.Thread(target=ejecutar_vlan_config, name=f"VLANConfig-{puerto}")
            config_thread.start()
            
        elif accion == "desconectar" and puerto != "desconocido":
            log(f"Dispositivo desconectado en puerto {puerto} del {dispositivo}")
            log(f"Limpieza del puerto {puerto} tras desconexión del dispositivo en {dispositivo}.")
            
            # Ejecutar limpieza en thread separado
            def ejecutar_limpieza():
                limpiar_puerto(puerto)
            
            cleanup_thread = threading.Thread(target=ejecutar_limpieza, name=f"Cleanup-{puerto}")
            cleanup_thread.start()
        else:
            log("Trap recibido sin acción automática definida.")
            
    except Exception as e:
        log(f"ERROR en procesamiento asíncrono de trap: {str(e)}")

def main():
    """
    Función principal que procesa traps SNMP de forma concurrente.
    """
    try:
        trap_data = sys.stdin.read()
        if not trap_data.strip():
            log("Trap vacío o ilegible recibido, terminando.")
            sys.exit(1)

        log("Trap SNMP recibido, iniciando procesamiento concurrente...")
        
        # Limpiar cache periódicamente
        limpiar_cache()
        
        # Procesar el trap de forma asíncrona
        future = trap_executor.submit(procesar_trap_async, trap_data)
        
        # Opcional: esperar a que termine o continuar
        # Para debugging, esperamos el resultado
        try:
            future.result(timeout=30)  # Timeout de 30 segundos
            log("Procesamiento de trap completado exitosamente")
        except concurrent.futures.TimeoutError:
            log("Timeout procesando trap - continuando en background")
        except Exception as e:
            log(f"Error en procesamiento de trap: {str(e)}")
            
    except KeyboardInterrupt:
        log("Interrupción recibida, cerrando executor...")
        trap_executor.shutdown(wait=True)
        sys.exit(0)
    except Exception as e:
        log(f"ERROR general en main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()