#!/usr/bin/env python3

import subprocess
import datetime
import time
import os
import threading
import queue
import concurrent.futures
from typing import Optional, Dict, List

# Locks globales para thread-safety
log_lock = threading.Lock()
snmp_operation_lock = threading.Lock()

# Cola para operaciones SNMP concurrentes
snmp_queue = queue.Queue()

# Cache de resultados SNMP para evitar consultas duplicadas
snmp_cache = {}
cache_lock = threading.Lock()
CACHE_TTL = 30  # segundos

# Función para limpiar logs antiguos y rotar archivos
def rotar_logs_si_necesario(max_lines=1000):
    """
    Rota el archivo de log si supera el número máximo de líneas.
    
    Args:
        max_lines (int): Número máximo de líneas antes de rotar.
    """
    log_path = "/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs/snmp_utils.log"
    
    if not os.path.exists(log_path):
        return
        
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            
        if len(lines) > max_lines:
            # Mantener solo las últimas max_lines/2 líneas
            keep_lines = lines[-(max_lines//2):]
            with open(log_path, 'w') as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Log rotado - manteniendo últimas {len(keep_lines)} líneas\n")
                f.writelines(keep_lines)
    except Exception as e:
        print(f"Error rotando logs: {e}")

# Función para registrar mensajes en un archivo de log
def log(message, level="INFO"):
    """
    Escribe un mensaje en el archivo de log `snmp_utils.log` de forma thread-safe.

    Args:
        message (str): Mensaje a registrar.
        level (str): Nivel de log (INFO, DEBUG, ERROR, etc.)
    """
    with log_lock:  # Thread-safe logging
        os.chdir("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs")
        
        # Rotar logs si es necesario antes de escribir
        if level in ["INFO", "ERROR"]:  # Solo rotar en logs importantes
            rotar_logs_si_necesario()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        thread_id = threading.current_thread().name
        with open("snmp_utils.log", "a") as log_file:
            log_file.write(f"[{timestamp}] [{level}] [Thread:{thread_id}] {message}\n")

def get_cache_key(switch_ip: str, ifindex: int, community: str) -> str:
    """Genera una clave única para el cache de operaciones SNMP."""
    return f"{switch_ip}:{ifindex}:{community}"

def is_cache_valid(timestamp: float) -> bool:
    """Verifica si el resultado en cache aún es válido."""
    return (time.time() - timestamp) < CACHE_TTL

def get_from_cache(cache_key: str) -> Optional[str]:
    """Obtiene un resultado del cache si es válido."""
    with cache_lock:
        if cache_key in snmp_cache:
            mac, timestamp = snmp_cache[cache_key]
            if is_cache_valid(timestamp):
                log(f"Cache hit para {cache_key}: {mac}", "DEBUG")
                return mac
            else:
                # Cache expirado, eliminarlo
                del snmp_cache[cache_key]
                log(f"Cache expirado para {cache_key}", "DEBUG")
    return None

def set_cache(cache_key: str, mac: str) -> None:
    """Almacena un resultado en el cache."""
    with cache_lock:
        snmp_cache[cache_key] = (mac, time.time())
        log(f"Cache actualizado para {cache_key}: {mac}", "DEBUG")

def execute_snmp_command_with_timeout(command: List[str], timeout: int = 10) -> Optional[str]:
    """
    Ejecuta un comando SNMP con timeout para evitar bloqueos.
    
    Args:
        command: Lista con el comando a ejecutar
        timeout: Timeout en segundos
    
    Returns:
        Salida del comando o None si falla
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"Error en comando SNMP: {result.stderr}", "ERROR")
            return None
    except subprocess.TimeoutExpired:
        log(f"Timeout ejecutando comando SNMP: {' '.join(command)}", "ERROR")
        return None
    except Exception as e:
        log(f"Error ejecutando comando SNMP: {str(e)}", "ERROR")
        return None

# Función para buscar la dirección MAC asociada a un puerto en un switch
def buscar_mac_por_puerto(switch_ip, ifindex, community="proyectoTDG", ifindex_validos=None):
    """
    Busca la dirección MAC asociada a un puerto en un switch utilizando SNMP de forma thread-safe.

    Args:
        switch_ip (str): Dirección IP del switch.
        ifindex (int): Índice del puerto en el switch.
        community (str): Comunidad SNMP.
        ifindex_validos (dict): Diccionario de ifIndex válidos (puertos físicos mapeados).

    Returns:
        str: Dirección MAC encontrada o None si no se encuentra.
    """
    # Verificar cache primero
    cache_key = get_cache_key(switch_ip, ifindex, community)
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result
    
    try:
        # Validar que el ifIndex corresponde a un puerto físico mapeado
        if ifindex_validos and str(ifindex) not in ifindex_validos:
            log(f"ifIndex {ifindex} no está en la lista de puertos físicos mapeados. Ignorando.", "DEBUG")
            return None
            
        oid_mac_to_port = "1.3.6.1.2.1.17.4.3.1.2"
        oid_port_to_ifindex = "1.3.6.1.2.1.17.1.4.1.2"

        # Usar lock para operaciones SNMP críticas (evitar saturar el dispositivo)
        with snmp_operation_lock:
            # Obtener MAC -> portNum con timeout
            mac_to_port_output = execute_snmp_command_with_timeout([
                "snmpwalk", "-v2c", "-c", community, "-On", switch_ip, oid_mac_to_port
            ])
            
            if not mac_to_port_output:
                log(f"Error obteniendo tabla MAC para {switch_ip}", "ERROR")
                return None

        mac_to_port = {}
        for line in mac_to_port_output.splitlines():
            if "No Such Instance" in line:
                log(f"No hay MACs disponibles en la tabla de forwarding", "DEBUG")
                continue
                
            parts = line.split(" = ")
            if len(parts) == 2:
                oid_suffix = parts[0].split(".")[-6:]  # Últimos 6 bytes = MAC
                try:
                    mac = ":".join(f"{int(x):02x}" for x in oid_suffix).upper()
                    port_num = int(parts[1].split(":")[-1].strip())
                    mac_to_port[mac] = port_num
                except ValueError as ve:
                    log(f"Error procesando MAC: {ve}", "DEBUG")
                    continue

        # Solo mostrar el número de MACs encontradas en lugar de toda la salida
        log(f"Encontradas {len(mac_to_port)} MACs en la tabla de forwarding", "DEBUG")

        # Obtener portNum -> ifIndex con timeout
        with snmp_operation_lock:
            port_to_ifindex_output = execute_snmp_command_with_timeout([
                "snmpwalk", "-v2c", "-c", community, "-On", switch_ip, oid_port_to_ifindex
            ])
            
            if not port_to_ifindex_output:
                log(f"Error obteniendo mapeo puerto->ifIndex para {switch_ip}", "ERROR")
                return None

        port_to_ifindex = {}
        for line in port_to_ifindex_output.splitlines():
            parts = line.split(" = ")
            if len(parts) == 2:
                try:
                    port_num_str = parts[0].split(".")[-1]
                    port_num = int(port_num_str)

                    value_parts = parts[1].split(":")
                    if len(value_parts) < 2:
                        continue

                    if_index_str = value_parts[-1].strip()
                    if_index = int(if_index_str)

                    port_to_ifindex[port_num] = if_index
                except ValueError:
                    continue

        log(f"Mapeados {len(port_to_ifindex)} puertos a ifIndex", "DEBUG")

        # Buscar la MAC cuyo portNum se asocia al ifIndex dado
        for mac, port_num in mac_to_port.items():
            if port_to_ifindex.get(port_num) == ifindex:
                log(f"MAC encontrada para ifIndex {ifindex}: {mac}", "INFO")
                # Guardar en cache antes de devolver
                set_cache(cache_key, mac)
                return mac

        log(f"No se encontró MAC para ifIndex {ifindex}", "DEBUG")
        return None

    except Exception as e:
        log(f"ERROR en buscar_mac_por_puerto: {str(e)}", "ERROR")
        return None

def buscar_mac_por_puerto_con_reintentos(switch_ip, ifindex, community="proyectoTDG", ifindex_validos=None, max_reintentos=3, espera_inicial=5):
    """
    Realiza hasta `max_reintentos` intentos para obtener la dirección MAC asociada a un ifIndex.
    Espera progresivamente más tiempo entre cada intento para dar tiempo a que las interfaces y VLANs se estabilicen.
    """
    # Validar que el ifIndex corresponde a un puerto físico mapeado
    if ifindex_validos and str(ifindex) not in ifindex_validos:
        log(f"ifIndex {ifindex} no está en la lista de puertos físicos configurados. No se realizarán intentos.", "INFO")
        return None
        
    log(f"Iniciando búsqueda de MAC para puerto físico ifIndex {ifindex} en {switch_ip}", "INFO")
    
    for intento in range(1, max_reintentos + 1):
        # Tiempo de espera progresivo: 10s, 15s, 20s
        espera_actual = espera_inicial + (intento - 1) * 5
        
        if intento > 1:
            log(f"Esperando {espera_actual}s antes del intento {intento} para permitir estabilización...", "INFO")
            time.sleep(espera_actual)
            
        log(f"Intento {intento}/{max_reintentos} para obtener MAC en ifIndex {ifindex}", "INFO")
        mac = buscar_mac_por_puerto(switch_ip, ifindex, community, ifindex_validos)
        if mac:
            log(f"MAC encontrada exitosamente en intento {intento}: {mac}", "INFO")
            return mac
        log(f"Intento {intento} sin éxito. MAC no encontrada para ifIndex {ifindex}.", "DEBUG")
    
    log(f"Búsqueda finalizada sin éxito tras {max_reintentos} intentos para ifIndex {ifindex}", "INFO")
    return None

def buscar_mac_concurrente(requests: List[Dict]) -> Dict[str, Optional[str]]:
    """
    Procesa múltiples solicitudes de búsqueda de MAC de forma concurrente.
    
    Args:
        requests: Lista de diccionarios con 'switch_ip', 'ifindex', 'community', 'ifindex_validos'
    
    Returns:
        Dict con las MACs encontradas por request_id
    """
    def proceso_individual(request):
        request_id = request.get('request_id', f"{request['switch_ip']}:{request['ifindex']}")
        mac = buscar_mac_por_puerto_con_reintentos(
            request['switch_ip'],
            request['ifindex'],
            request.get('community', 'proyectoTDG'),
            request.get('ifindex_validos'),
            request.get('max_reintentos', 3),
            request.get('espera_inicial', 5)
        )
        return request_id, mac
    
    log(f"Iniciando procesamiento concurrente de {len(requests)} solicitudes SNMP", "INFO")
    
    results = {}
    # Usar ThreadPoolExecutor para procesar en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(requests), 5)) as executor:
        # Enviar todas las tareas
        future_to_request = {
            executor.submit(proceso_individual, request): request 
            for request in requests
        }
        
        # Recoger resultados conforme se completan
        for future in concurrent.futures.as_completed(future_to_request):
            request = future_to_request[future]
            try:
                request_id, mac = future.result()
                results[request_id] = mac
                log(f"Solicitud completada para {request_id}: {mac or 'No encontrada'}", "INFO")
            except Exception as exc:
                request_id = request.get('request_id', f"{request['switch_ip']}:{request['ifindex']}")
                log(f"Error procesando solicitud {request_id}: {exc}", "ERROR")
                results[request_id] = None
    
    log(f"Procesamiento concurrente completado. {len([r for r in results.values() if r])} éxitos de {len(requests)}", "INFO")
    return results

def limpiar_cache() -> None:
    """Limpia entradas expiradas del cache SNMP."""
    with cache_lock:
        keys_to_remove = []
        for key, (mac, timestamp) in snmp_cache.items():
            if not is_cache_valid(timestamp):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del snmp_cache[key]
        
        if keys_to_remove:
            log(f"Cache limpiado: {len(keys_to_remove)} entradas expiradas eliminadas", "DEBUG")

def obtener_estadisticas_cache() -> Dict:
    """Obtiene estadísticas del cache SNMP."""
    with cache_lock:
        total_entries = len(snmp_cache)
        valid_entries = sum(1 for _, timestamp in snmp_cache.values() if is_cache_valid(timestamp))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'hit_ratio': 'N/A'  # Se podría implementar contadores de hits/misses
        }
