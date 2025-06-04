#!/usr/bin/env python3

import subprocess
import datetime
import time
import os

# Función para registrar mensajes en un archivo de log
def log(message):
    """
    Escribe un mensaje en el archivo de log `snmp_utils.log`.

    Args:
        message (str): Mensaje a registrar.
    """
    os.chdir("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("snmp_utils.log", "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

# Función para buscar la dirección MAC asociada a un puerto en un switch
def buscar_mac_por_puerto(switch_ip, ifindex, community="proyectoTDG"):
    """
    Busca la dirección MAC asociada a un puerto en un switch utilizando SNMP.

    Args:
        switch_ip (str): Dirección IP del switch.
        ifindex (int): Índice del puerto en el switch.
        community (str): Comunidad SNMP.

    Returns:
        str: Dirección MAC encontrada o None si no se encuentra.
    """
    try:
        oid_mac_to_port = "1.3.6.1.2.1.17.4.3.1.2"
        oid_port_to_ifindex = "1.3.6.1.2.1.17.1.4.1.2"

        # Obtener MAC -> portNum
        mac_to_port_output = subprocess.check_output(
            ["snmpwalk", "-v2c", "-c", community, "-On", switch_ip, oid_mac_to_port],
            text=True
        )

        mac_to_port = {}
        for line in mac_to_port_output.splitlines():
            log(f"Procesando línea de MAC->Port: {line}")
            parts = line.split(" = ")
            if len(parts) == 2:
                oid_suffix = parts[0].split(".")[-6:]  # Últimos 6 bytes = MAC
                try:
                    mac = ":".join(f"{int(x):02x}" for x in oid_suffix).upper()
                    port_num = int(parts[1].split(":")[-1].strip())
                    mac_to_port[mac] = port_num
                except ValueError as ve:
                    log(f"Error procesando MAC o port_num: {ve} | Línea: {line}")
                    continue

        log(f"Salida de snmpwalk para MAC -> portNum:\n{mac_to_port_output}")

        # Obtener portNum -> ifIndex
        port_to_ifindex_output = subprocess.check_output(
            ["snmpwalk", "-v2c", "-c", community, "-On", switch_ip, oid_port_to_ifindex],
            text=True
        )

        port_to_ifindex = {}
        for line in port_to_ifindex_output.splitlines():
            log(f"Procesando línea de Port->ifIndex: {line}")
            parts = line.split(" = ")
            if len(parts) == 2:
                try:
                    port_num_str = parts[0].split(".")[-1]
                    port_num = int(port_num_str)

                    value_parts = parts[1].split(":")
                    if len(value_parts) < 2:
                        log(f"Formato inesperado en línea: {line}")
                        continue

                    if_index_str = value_parts[-1].strip()
                    if_index = int(if_index_str)

                    port_to_ifindex[port_num] = if_index
                except ValueError as ve:
                    log(f"Error procesando ifIndex o port_num: {ve} | Línea: {line}")
                    continue

        log(f"Salida de snmpwalk para portNum -> ifIndex:\n{port_to_ifindex_output}")

        # Buscar la MAC cuyo portNum se asocia al ifIndex dado
        for mac, port_num in mac_to_port.items():
            if port_to_ifindex.get(port_num) == ifindex:
                log(f"MAC encontrada para ifIndex {ifindex}: {mac}")
                return mac

        log(f"No se encontró una MAC asociada al ifIndex {ifindex} en {switch_ip}.")
        return None

    except subprocess.CalledProcessError as e:
        log(f"ERROR ejecutando snmpwalk: {str(e)}")
        return None

def buscar_mac_por_puerto_con_reintentos(switch_ip, ifindex, community="proyectoTDG", max_reintentos=5, espera_segundos=5):
    """
    Realiza hasta `max_reintentos` intentos para obtener la dirección MAC asociada a un ifIndex.
    Espera `espera_segundos` entre cada intento.
    """
    for intento in range(1, max_reintentos + 1):
        log(f"Intento {intento} de {max_reintentos} para obtener la MAC en ifIndex {ifindex} del switch {switch_ip}.")
        mac = buscar_mac_por_puerto(switch_ip, ifindex, community)
        if mac:
            log(f"MAC encontrada en intento {intento}: {mac}")
            return mac
        log(f"Intento {intento} fallido. No se encontró MAC para ifIndex {ifindex}.")
        time.sleep(espera_segundos)
    log(f"No se pudo obtener la MAC tras {max_reintentos} intentos para ifIndex {ifindex} en {switch_ip}.")
    return None
