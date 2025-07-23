# 🚀 Guía de Uso Práctica - Sistema Ansible TDGRedes

## 📝 Ejemplos de Ejecución Paso a Paso

### 🔧 Configuración Inicial

#### 1. Preparar el sistema DHCPv6 en el router
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE

# Configurar todos los pools DHCPv6
ansible-playbook -i inventory/inventory.yml playbooks/dhcp6_config.yml
```

**Resultado esperado**:
- Pool VLAN20-POOL creado con prefijo 203F:A:b:0020::/64
- Pool VLAN30-POOL creado con prefijo 203F:A:b:0030::/64
- DNS configurado: 2001:4860:4860::8888
- Dominio configurado: red.local

#### 2. Iniciar monitoreo del sistema SNMP
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control

# Ver estado inicial
./snmp_monitor.py stats

# Iniciar monitoreo en tiempo real
./snmp_monitor.py monitor --interval 5
```

---

### 🔌 Escenarios de Conexión de Dispositivos

#### Escenario 1: Dispositivo conocido se conecta
**Situación**: MAC `30:13:8B:F1:00:BE` se conecta al puerto FastEthernet0/1

**Proceso automático**:
1. Switch detecta conexión y envía trap SNMP
2. Sistema busca la MAC en dispositivos.json → VLAN 20
3. Se ejecutan automáticamente:
```bash
# Configurar VLAN 20 en el switch
export VLAN_ID=20
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml

# Asignar puerto a VLAN con port-security
export MAC_ADDRESS="30:13:8B:F1:00:BE"
export VLAN_ID=20
export PUERTO="FastEthernet0/1"
ansible-playbook -i inventory/inventory.yml playbooks/asignar_vlanxmac.yml
```

**Verificación**:
```bash
# Ver logs del sistema
./snmp_monitor.py logs --lines 20

# Ver estadísticas del cache
./snmp_monitor.py stats
```

#### Escenario 2: Dispositivo desconocido se conecta
**Situación**: MAC no registrada se conecta

**Proceso**:
1. Sistema detecta MAC pero no encuentra VLAN asignada
2. Solo se crea la VLAN por defecto (si está configurada)
3. Se requiere configuración manual

**Configuración manual**:
```bash
# Agregar MAC al archivo de configuración
# Editar: access_control/config/dispositivos.json
# Añadir: "AA:BB:CC:DD:EE:FF": 30

# Ejecutar configuración manual
export MAC_ADDRESS="AA:BB:CC:DD:EE:FF"
export VLAN_ID=30
export PUERTO="FastEthernet0/2"
ansible-playbook -i inventory/inventory.yml playbooks/asignar_vlanxmac.yml
```

#### Escenario 3: Dispositivo se desconecta
**Situación**: Dispositivo se desconecta del puerto

**Proceso automático**:
1. Switch detecta desconexión y envía trap SNMP
2. Se ejecuta automáticamente:
```bash
export PUERTO="FastEthernet0/1"
ansible-playbook -i inventory/inventory.yml playbooks/limpiar_puerto.yml
```

**Resultado**:
- Puerto se apaga temporalmente
- Se elimina asignación de VLAN
- Se elimina port-security
- Puerto se enciende limpio

---

### 🧪 Pruebas y Testing

#### Prueba 1: Configuración básica de switch
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/playbooks

# Ejecutar playbook de prueba
ansible-playbook -i ../inventory/inventory.yml switchtest.yml
```

**Lo que hace**:
- Crea VLAN 20 "Usuarios"
- Asigna puertos FastEthernet0/1-3 como acceso
- Configura interfaz VLAN con IPv6
- Establece relay DHCPv6

#### Prueba 2: Configuración básica de router
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/playbooks

# Ejecutar playbook de prueba
ansible-playbook -i ../inventory/inventory.yml routertest.yml
```

**Lo que hace**:
- Crea pool DHCPv6 para VLAN 20
- Configura prefijo de red
- Establece DNS y dominio

#### Prueba 3: Simulación de carga concurrente
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control

# Simular 10 requests SNMP concurrentes
./snmp_monitor.py test-concurrent --requests 10
```

**Lo que hace**:
- Crea 10 solicitudes SNMP simultáneas
- Muestra tiempo de procesamiento
- Verifica funcionamiento del cache
- Demuestra capacidades concurrentes

---

### 🔧 Configuraciones Avanzadas

#### Configurar nueva VLAN dinámicamente
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE

# 1. Editar group_vars/switches.yml y añadir VLAN 50
# 2. Editar group_vars/routers.yml y añadir pool DHCPv6
# 3. Configurar VLAN en switch
export VLAN_ID=50
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml

# 4. Configurar pool en router
ansible-playbook -i inventory/inventory.yml playbooks/dhcp6_config.yml
```

#### Agregar nuevo dispositivo MAC
```bash
# 1. Editar access_control/config/dispositivos.json
# Añadir en "vlan_por_mac": "XX:XX:XX:XX:XX:XX": 40

# 2. Verificar configuración
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control
python3 -c "
import json
with open('config/dispositivos.json') as f:
    config = json.load(f)
    print('VLANs por MAC configuradas:')
    for mac, vlan in config['vlan_por_mac'].items():
        print(f'  {mac} → VLAN {vlan}')
"
```

#### Configurar puerto específico manualmente
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE

# Configurar MAC específica en puerto específico
export MAC_ADDRESS="11:22:33:44:55:66"
export VLAN_ID=20
export PUERTO="FastEthernet0/5"
ansible-playbook -i inventory/inventory.yml playbooks/asignar_vlanxmac.yml

# Verificar en el switch:
# show mac address-table interface FastEthernet0/5
# show interfaces FastEthernet0/5 switchport
```

---

### 📊 Monitoreo y Mantenimiento

#### Monitoreo diario
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control

# Ver estadísticas del cache
./snmp_monitor.py stats

# Ver logs recientes
./snmp_monitor.py logs --lines 100

# Limpiar cache si es necesario
./snmp_monitor.py clean-cache
```

#### Verificación de conectividad
```bash
# Verificar conectividad con dispositivos
ansible all -i inventory/inventory.yml -m ping

# Verificar conectividad específica
ansible switches -i inventory/inventory.yml -m ping
ansible routers -i inventory/inventory.yml -m ping
```

#### Ejecución de comandos ad-hoc
```bash
# Verificar VLANs en switch
ansible switches -i inventory/inventory.yml -m ios_command -a "commands='show vlan brief'"

# Verificar pools DHCPv6 en router
ansible routers -i inventory/inventory.yml -m ios_command -a "commands='show ipv6 dhcp pool'"

# Verificar interfaces en switch
ansible switches -i inventory/inventory.yml -m ios_command -a "commands='show interfaces status'"
```

---

### 🚨 Resolución de Problemas

#### Problema: Trap SNMP no se procesa
```bash
# 1. Verificar logs
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control
tail -f logs/snmp_traps.log

# 2. Verificar configuración de dispositivos
cat config/dispositivos.json | python3 -m json.tool

# 3. Probar conectividad SNMP manualmente
snmpwalk -v2c -c proyectoTDG 203F:A:b:10::2 1.3.6.1.2.1.1.1.0
```

#### Problema: Playbook falla
```bash
# Ejecutar en modo verbose
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml -vvv

# Verificar sintaxis
ansible-playbook --syntax-check playbooks/vlan_config.yml

# Verificar conectividad
ansible switches -i inventory/inventory.yml -m ping
```

#### Problema: Cache SNMP lleno
```bash
cd /home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control

# Ver estadísticas
./snmp_monitor.py stats

# Limpiar cache
./snmp_monitor.py clean-cache

# Verificar espacio en logs
du -sh logs/
```

---

### 📈 Optimización de Rendimiento

#### Configurar cache óptimo
```python
# En snmp_utils.py, ajustar TTL del cache:
CACHE_TTL = 60  # Aumentar a 60 segundos para redes estables
```

#### Configurar concurrencia
```python
# En snmptrap_handler.py, ajustar workers:
MAX_CONCURRENT_TRAPS = 5  # Aumentar para más concurrencia
```

#### Configurar timeouts SNMP
```python
# En snmp_utils.py, ajustar timeout:
execute_snmp_command_with_timeout(command, timeout=15)  # Aumentar timeout
```

---

### 📝 Logs y Auditoría

#### Ubicación de logs importantes
```bash
# Logs del sistema SNMP
/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs/snmp_traps.log
/home/tdg2025/Escritorio/TDGRedes/ANSIBLE/access_control/logs/snmp_utils.log

# Ver logs en tiempo real
tail -f access_control/logs/snmp_traps.log
tail -f access_control/logs/snmp_utils.log
```

#### Formato de logs
```
[2025-07-23 14:30:15] [INFO] [Thread:ThreadPoolExecutor-0_0] Trap SNMP recibido, iniciando procesamiento concurrente...
[2025-07-23 14:30:15] [INFO] [Thread:ThreadPoolExecutor-0_0] Procesando evento para puerto físico configurado ifIndex 10001...
[2025-07-23 14:30:16] [INFO] [Thread:ThreadPoolExecutor-0_0] MAC encontrada exitosamente en intento 1: 30:13:8B:F1:00:BE
```

Este sistema proporciona **automatización completa** del control de acceso de red basado en IPv6, VLANs dinámicas y DHCPv6, con **soporte total para simultaneidad** y **monitoreo en tiempo real**.
