#!/usr/bin/env python3

import sys
import os
import time

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE"))

from access_control.snmp_utils import buscar_mac_por_puerto_con_reintentos

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
    Registra un mensaje en el archivo de log.

    Args:
        mensaje (str): Mensaje a registrar.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

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

def ejecutar_playbook(mac_address, puerto, vlan_id, playbook):
    """
    Ejecuta un playbook de Ansible con las variables proporcionadas.

    Args:
        mac_address (str): Dirección MAC del dispositivo.
        puerto (str): Nombre del puerto.
        vlan_id (str): ID de la VLAN.
        playbook (str): Ruta del playbook a ejecutar.
    """
    os.chdir("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE")
    try:
        result = subprocess.run([
            "ansible-playbook",
            f"/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/{playbook}",
            "--extra-vars", f"mac_address={mac_address} interface_name={puerto} vlan_id={vlan_id}"
        ], capture_output=True, text=True)

        log(f"Playbook ejecutado para MAC {mac_address} en puerto {puerto} con VLAN {vlan_id}. Salida:\n{result.stdout}\nErrores:\n{result.stderr}")
    except Exception as e:
        log(f"ERROR ejecutando playbook: {str(e)}")

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

def main():
    """
    Función principal que procesa traps SNMP, detecta eventos y ejecuta acciones
    como asignar VLANs o limpiar puertos según corresponda.
    """
    try:
        trap_data = sys.stdin.read()
        if not trap_data.strip():
            log("Trap vacío o ilegible recibido, terminando.")
            sys.exit(1)

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

        # Obtener dirección MAC únicamente mediante SNMP polling con reintentos
        mac_address = None
        if puerto_index.isdigit():
            log(f"Intentando obtener la dirección MAC mediante SNMP polling con reintentos para ifIndex {puerto_index}...")
            mac_address = buscar_mac_por_puerto_con_reintentos(ip_origen, int(puerto_index))
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
            ejecutar_playbook(mac_address, puerto, vlan_id, "playbooks/vlan_config.yml")
            if vlan_id:
                log(f"Configurando VLAN {vlan_id} en puerto {puerto} para MAC {mac_address}...")
                ejecutar_playbook(mac_address, puerto, vlan_id, "playbooks/asignar_vlanxmac.yml")
            else:
                log(f"No se encontró una VLAN asignada para la MAC {mac_address}.")
        elif accion == "desconectar" and puerto != "desconocido":
            log(f"Dispositivo desconectado en puerto {puerto} del {dispositivo}")
            log(f"Limpieza del puerto {puerto} tras desconexión del dispositivo en {dispositivo}.")
            limpiar_puerto(puerto)
        else:
            log("Trap recibido sin acción automática definida.")

    except Exception as e:
        log(f"ERROR general en main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()