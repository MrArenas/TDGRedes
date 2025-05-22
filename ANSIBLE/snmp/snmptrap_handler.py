#!/usr/bin/env python3
import sys
import os
import datetime
import json
import subprocess
import re

# Rutas
BASE_DIR = "/home/tdg2025/Escritorio/TDGRedes"
LOG_FILE = os.path.join(BASE_DIR, "snmp/logs/snmp_traps.log")
CONFIG_FILE = os.path.join(BASE_DIR, "snmp/config/dispositivos.json")

# Asegurar existencia del directorio de logs
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def cargar_configuracion():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR cargando configuración: {str(e)}")
        sys.exit(1)

def log(mensaje):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

def obtener_dispositivo(ip, dispositivos_por_ip):
    return dispositivos_por_ip.get(ip, "DESCONOCIDO")

def obtener_puerto(trap_data, ifindex_to_interface):
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

def validar_puerto(puerto):
    return re.sub(r'[^A-Za-z0-9/]', '', puerto)

def determinar_evento(trap_data, acciones):
    evento = "TRAP DESCONOCIDO"
    accion = None
    for palabra_clave, (evento_detectado, accion_detectada) in acciones.items():
        if palabra_clave in trap_data:
            evento = evento_detectado
            accion = accion_detectada
            break
    return evento, accion

def ejecutar_playbook(puerto):
    os.chdir("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE")
    try:
        result = subprocess.run([
            "ansible-playbook",
            "playbooks/vlan_config.yml",
            "--extra-vars", f"puerto={puerto}"
        ], capture_output=True, text=True)

        log(f"Playbook ejecutado para puerto {puerto}. Salida:\n{result.stdout}\nErrores:\n{result.stderr}")
    except Exception as e:
        log(f"ERROR ejecutando playbook: {str(e)}")

def main():
    try:
        trap_data = sys.stdin.read()
        if not trap_data.strip():
            log("Trap vacío o ilegible recibido, terminando.")
            sys.exit(1)

        config = cargar_configuracion()
        dispositivos_por_ip = config.get("dispositivos_por_ip", {})
        ifindex_to_interface = config.get("ifindex_to_interface", {})
        acciones = config.get("acciones", {})

        
        ip_origen_aux = re.search(r'UDP/IPv6:\s+\[([0-9a-fA-F:]+)\]',trap_data)
        if ip_origen_aux:
            ip_origen=ip_origen_aux.group(1)
        else:
            ip_origen = "desconocido"
        dispositivo = obtener_dispositivo(ip_origen, dispositivos_por_ip)
        evento, accion = determinar_evento(trap_data, acciones)
        puerto, puerto_index = obtener_puerto(trap_data, ifindex_to_interface)

        log_entry = (
            f"Evento: {evento}\n"
            f"Dispositivo: {dispositivo} IP origen: {ip_origen}\n"
            f"Puerto detectado: {puerto} (Index {puerto_index})\n"
            f"{trap_data}\n{'-'*60}\n"
        )
        log(log_entry)

        puerto = validar_puerto(puerto)

        if accion == "conectar" and puerto != "desconocido":
            log(f"Nuevo dispositivo conectado en puerto {puerto}, ejecutando playbook...")
            ejecutar_playbook(puerto)
        elif accion == "desconectar":
            log(f"Dispositivo desconectado en puerto {puerto} del {dispositivo}")
        else:
            log("Trap recibido sin acción automática definida.")

    except Exception as e:
        log(f"ERROR general en main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()