#!/usr/bin/env python3

"""
Monitor de sistema SNMP concurrente
Proporciona estadísticas y control del sistema SNMP con soporte de simultaneidad.
"""

import sys
import os
import time
import threading
import argparse
import json
from datetime import datetime, timedelta

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath("/home/tdg2025/Escritorio/TDGRedes/ANSIBLE"))

from access_control.snmp_utils import obtener_estadisticas_cache, limpiar_cache, snmp_cache, cache_lock

def mostrar_estadisticas_cache():
    """Muestra estadísticas detalladas del cache SNMP."""
    stats = obtener_estadisticas_cache()
    
    print("📊 Estadísticas del Cache SNMP")
    print("=" * 40)
    print(f"Entradas totales: {stats['total_entries']}")
    print(f"Entradas válidas: {stats['valid_entries']}")
    print(f"Entradas expiradas: {stats['expired_entries']}")
    print(f"Tasa de aciertos: {stats['hit_ratio']}")
    
    # Mostrar contenido del cache si hay entradas
    if stats['total_entries'] > 0:
        print("\n🗂️ Contenido del Cache:")
        print("-" * 40)
        with cache_lock:
            for key, (mac, timestamp) in snmp_cache.items():
                age = time.time() - timestamp
                status = "✅ Válida" if age < 30 else "❌ Expirada"
                print(f"{key}: {mac} ({age:.1f}s) {status}")

def mostrar_logs_recientes(lineas=20):
    """Muestra las líneas más recientes de los logs."""
    log_files = [
        "/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs/snmp_utils.log",
        "/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs/snmp_traps.log"
    ]
    
    print(f"📄 Últimas {lineas} líneas de logs")
    print("=" * 50)
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📁 {os.path.basename(log_file)}:")
            print("-" * 30)
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-lineas:]:
                        print(line.strip())
            except Exception as e:
                print(f"Error leyendo {log_file}: {e}")
        else:
            print(f"\n❌ {log_file} no encontrado")

def limpiar_cache_comando():
    """Limpia el cache SNMP manualmente."""
    print("🧹 Limpiando cache SNMP...")
    before_count = len(snmp_cache)
    limpiar_cache()
    after_count = len(snmp_cache)
    removed = before_count - after_count
    print(f"✅ Cache limpiado. Eliminadas {removed} entradas expiradas.")
    print(f"📊 Entradas restantes: {after_count}")

def simular_carga_concurrente(num_requests=5):
    """Simula múltiples requests SNMP concurrentes para testing."""
    from access_control.snmp_utils import buscar_mac_concurrente
    
    print(f"🔄 Simulando {num_requests} requests SNMP concurrentes...")
    
    # Crear requests de prueba
    requests = []
    for i in range(num_requests):
        requests.append({
            'request_id': f'test-{i}',
            'switch_ip': '2001:db8::1',  # IP de ejemplo
            'ifindex': 10 + i,
            'community': 'proyectoTDG',
            'max_reintentos': 1,
            'espera_inicial': 1
        })
    
    start_time = time.time()
    results = buscar_mac_concurrente(requests)
    end_time = time.time()
    
    print(f"⏱️ Procesamiento completado en {end_time - start_time:.2f} segundos")
    print(f"✅ Resultados: {len(results)} responses")
    
    for request_id, mac in results.items():
        status = "✅ Encontrada" if mac else "❌ No encontrada"
        print(f"  {request_id}: {mac or 'N/A'} {status}")

def monitorear_tiempo_real(intervalo=5):
    """Monitorea el sistema en tiempo real."""
    print(f"👁️ Monitoreando sistema en tiempo real (cada {intervalo}s)")
    print("Presiona Ctrl+C para detener")
    print("=" * 50)
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stats = obtener_estadisticas_cache()
            
            print(f"\n[{timestamp}] Cache: {stats['valid_entries']}/{stats['total_entries']} válidas")
            
            # Verificar actividad reciente en logs
            log_file = "/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs/snmp_traps.log"
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            last_line = lines[-1].strip()
                            print(f"Último log: {last_line[:80]}...")
                except:
                    pass
            
            time.sleep(intervalo)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido")

def main():
    parser = argparse.ArgumentParser(description="Monitor del sistema SNMP concurrente")
    parser.add_argument('command', choices=[
        'stats', 'logs', 'clean-cache', 'test-concurrent', 'monitor'
    ], help='Comando a ejecutar')
    parser.add_argument('--lines', '-l', type=int, default=20, help='Número de líneas de log (default: 20)')
    parser.add_argument('--requests', '-r', type=int, default=5, help='Número de requests concurrentes (default: 5)')
    parser.add_argument('--interval', '-i', type=int, default=5, help='Intervalo de monitoreo en segundos (default: 5)')
    
    args = parser.parse_args()
    
    print("🔧 Monitor del Sistema SNMP Concurrente")
    print("=" * 40)
    
    if args.command == 'stats':
        mostrar_estadisticas_cache()
    elif args.command == 'logs':
        mostrar_logs_recientes(args.lines)
    elif args.command == 'clean-cache':
        limpiar_cache_comando()
    elif args.command == 'test-concurrent':
        simular_carga_concurrente(args.requests)
    elif args.command == 'monitor':
        monitorear_tiempo_real(args.interval)

if __name__ == "__main__":
    main()
