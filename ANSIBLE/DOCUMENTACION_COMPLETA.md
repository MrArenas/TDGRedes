# 📚 Documentación Completa del Sistema Ansible - TDGRedes

## 📁 Estructura del Proyecto

```
ANSIBLE/
├── ansible.cfg                          # Configuración principal de Ansible
├── inventory/                           # Inventario y variables
│   ├── inventory.yml                    # Hosts y conexiones
│   └── group_vars/                      # Variables por grupos
│       ├── all.yml                      # Variables globales (comentado)
│       ├── switches.yml                 # Variables específicas de switches
│       └── routers.yml                  # Variables específicas de routers
├── playbooks/                           # Playbooks principales
│   ├── vlan_config.yml                  # Configuración de VLANs
│   ├── asignar_vlanxmac.yml            # Asignación de VLAN por MAC
│   ├── dhcp6_config.yml                # Configuración de DHCPv6
│   ├── limpiar_puerto.yml              # Limpieza de puertos
│   ├── routertest.yml                  # Pruebas de router
│   └── switchtest.yml                  # Pruebas de switch
├── roles/                               # Roles reutilizables
│   ├── switch_vlan_dhcp/               # Configuración VLAN+DHCP en switch
│   ├── router_dhcp6/                   # Configuración DHCPv6 en router
│   ├── switch_mac_control/             # Control de MAC en puerto
│   └── limpiar_puerto/                 # Limpieza de configuración
└── access_control/                     # Sistema SNMP y control de acceso
    ├── snmp_utils.py                   # Utilidades SNMP concurrentes
    ├── snmptrap_handler.py             # Manejador de traps SNMP
    ├── snmp_monitor.py                 # Monitor del sistema SNMP
    ├── config/dispositivos.json        # Configuración de dispositivos
    └── logs/                           # Archivos de log
```

---

## ⚙️ Archivos de Configuración

### 📄 `ansible.cfg`
**Función**: Configuración principal de Ansible
```properties
[defaults]
inventory = inventory/inventory.yml     # Inventario por defecto
roles_path = ./roles                   # Ruta de roles
host_key_checking = False              # Desactiva verificación de host keys
retry_files_enabled = False            # Desactiva archivos de reintentos
stdout_callback = yaml                 # Formato de salida YAML
gathering = smart                      # Recolección inteligente de facts
```

**Ejecución**: No se ejecuta directamente. Ansible lo usa automáticamente.

---

## 📋 Inventario y Variables

### 📄 `inventory/inventory.yml`
**Función**: Define hosts, grupos y configuraciones de conexión
- **Switch1**: `203F:A:b:10::2` (usuario: admin)
- **Router1**: `203F:A:b:1::1` (usuario: admin)
- **Conexión**: `network_cli` para dispositivos Cisco IOS

**Rutas relativas desde ANSIBLE/**:
```bash
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml
```

### 📄 `inventory/group_vars/switches.yml`
**Función**: Variables específicas para switches
- **VLANs configuradas**: 20 (Usuarios), 30 (Administración), 40 (Pruebas)
- **Interfaz por defecto**: FastEthernet0/1
- **IP del router**: 203F:A:b:0001::1

### 📄 `inventory/group_vars/routers.yml`
**Función**: Variables específicas para routers
- **Pools DHCPv6**: VLAN20-POOL, VLAN30-POOL
- **Prefijos**: 203F:A:b:0020::/64, 203F:A:b:0030::/64
- **DNS**: 2001:4860:4860::8888
- **Dominio**: red.local

### 📄 `inventory/group_vars/all.yml`
**Función**: Variables globales (actualmente comentado)
- Plantilla para configuración común de VLANs

---

## 🚀 Playbooks Principales

### 📄 `playbooks/vlan_config.yml`
**Función**: Configura VLANs dinámicamente en switches
- **Hosts**: switch1
- **Variables requeridas**: `vlan_id` (desde variable de entorno)
- **Proceso**: Filtra VLAN por ID y ejecuta el role switch_vlan_dhcp

**Ejecución**:
```bash
# Desde directorio ANSIBLE/
export VLAN_ID=20
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml
```

### 📄 `playbooks/asignar_vlanxmac.yml`
**Función**: Asigna VLAN y port-security basado en dirección MAC
- **Hosts**: switches
- **Variables requeridas**: `mac_address`, `vlan_id`, `interface_name`
- **Role**: switch_mac_control

**Ejecución**:
```bash
# Desde directorio ANSIBLE/
export MAC_ADDRESS="30:13:8B:F1:00:BE"
export VLAN_ID=20
export PUERTO="FastEthernet0/1"
ansible-playbook -i inventory/inventory.yml playbooks/asignar_vlanxmac.yml
```

### 📄 `playbooks/dhcp6_config.yml`
**Función**: Configura pools DHCPv6 en router
- **Hosts**: router1
- **Variables**: Usa `vlans_router` del group_vars
- **Role**: router_dhcp6 (en loop para cada VLAN)

**Ejecución**:
```bash
# Desde directorio ANSIBLE/
ansible-playbook -i inventory/inventory.yml playbooks/dhcp6_config.yml
```

### 📄 `playbooks/limpiar_puerto.yml`
**Función**: Limpia configuración de puerto cuando se desconecta dispositivo
- **Hosts**: switches
- **Variables requeridas**: `interface_name`
- **Role**: limpiar_puerto

**Ejecución**:
```bash
# Desde directorio ANSIBLE/
export PUERTO="FastEthernet0/1"
ansible-playbook -i inventory/inventory.yml playbooks/limpiar_puerto.yml
```

### 📄 `playbooks/routertest.yml`
**Función**: Playbook de prueba para configuración DHCPv6 en router
- **Hosts**: routers
- **Configuración**: Pool DHCPv6 para VLAN 20
- **Uso**: Testing y desarrollo

**Ejecución**:
```bash
# Desde directorio ANSIBLE/playbooks/
ansible-playbook -i ../inventory/inventory.yml routertest.yml
```

### 📄 `playbooks/switchtest.yml`
**Función**: Playbook de prueba para configuración completa de switch
- **Hosts**: switches
- **Configuración**: VLAN 20, puertos de acceso, DHCPv6 relay
- **Uso**: Testing y desarrollo

**Ejecución**:
```bash
# Desde directorio ANSIBLE/playbooks/
ansible-playbook -i ../inventory/inventory.yml switchtest.yml
```

---

## 🎭 Roles Reutilizables

### 📁 `roles/switch_vlan_dhcp/`
**Archivo**: `tasks/main.yml`
**Función**: Configura VLAN y DHCPv6 relay en switch
- Crea la VLAN con nombre
- Configura interfaz VLAN (SVI) con IPv6
- Establece relay DHCPv6 hacia el router

**Variables esperadas**:
- `vlan.id`: ID de la VLAN
- `vlan.name`: Nombre de la VLAN
- `vlan.vlan_ipv6_address`: IP IPv6 del SVI
- `router_ipv6`: IP del router para relay

### 📁 `roles/router_dhcp6/`
**Archivo**: `tasks/main.yml`
**Función**: Configura pool DHCPv6 en router Cisco
- Crea pool DHCPv6 con prefijo de red
- Configura servidor DNS
- Establece nombre de dominio

**Variables esperadas**:
- `vlan.dhcp_prefix`: Prefijo de red (ej: 203F:A:b:0020::/64)
- `vlan.dhcp_pool`: Nombre del pool
- `dns_server`: Servidor DNS
- `domain_name`: Nombre del dominio

### 📁 `roles/switch_mac_control/`
**Archivo**: `tasks/main.yml`
**Función**: Configura port-security basado en MAC
- Configura puerto como acceso
- Asigna puerto a VLAN específica
- Habilita port-security con MAC específica
- Limita a 1 MAC máximo
- Configura violación como restrict

**Variables esperadas**:
- `mac_address`: Dirección MAC permitida
- `vlan_id`: ID de la VLAN
- `interface_name`: Nombre del puerto

### 📁 `roles/limpiar_puerto/`
**Archivo**: `tasks/main.yml`
**Función**: Limpia configuración de puerto
1. Apaga el puerto (shutdown)
2. Elimina asignación de VLAN
3. Elimina port-security
4. Enciende el puerto (no shutdown)

**Variables esperadas**:
- `interface_name`: Nombre del puerto a limpiar

---

## 🖥️ Sistema SNMP y Control de Acceso

### 📄 `access_control/snmp_utils.py`
**Función**: Utilidades SNMP con soporte de concurrencia
- **Cache inteligente** con TTL de 30 segundos
- **Operaciones thread-safe** con locks
- **Timeouts** en consultas SNMP (10s)
- **Procesamiento concurrente** de múltiples requests
- **Logging detallado** con información de threads

**Funciones principales**:
- `buscar_mac_por_puerto()`: Busca MAC en puerto específico
- `buscar_mac_por_puerto_con_reintentos()`: Con reintentos progresivos
- `buscar_mac_concurrente()`: Procesa múltiples requests en paralelo
- `execute_snmp_command_with_timeout()`: SNMP con timeout
- Cache functions: get/set/clean cache

**Ejecución**: Se importa desde otros scripts, no se ejecuta directamente.

### 📄 `access_control/snmptrap_handler.py`
**Función**: Manejador principal de traps SNMP
- **Procesamiento concurrente** de traps
- **Control de concurrencia** para playbooks
- **Detección automática** de eventos (conectar/desconectar)
- **Ejecución automática** de playbooks según evento
- **Logging thread-safe** con información detallada

**Proceso**:
1. Recibe trap SNMP por stdin
2. Detecta IP origen y puerto
3. Busca MAC via SNMP polling
4. Ejecuta playbook correspondiente en thread separado

**Ejecución**:
```bash
# Desde directorio ANSIBLE/access_control/
echo "trap_data" | python3 snmptrap_handler.py
```

### 📄 `access_control/snmp_monitor.py`
**Función**: Monitor y herramientas de gestión del sistema SNMP
- **Estadísticas del cache**: Entradas válidas/expiradas
- **Visualización de logs**: Archivos recientes
- **Limpieza manual**: Cache y logs
- **Testing**: Simulación de carga concurrente
- **Monitoreo en tiempo real**: Estado del sistema

**Comandos disponibles**:
```bash
# Desde directorio ANSIBLE/access_control/
./snmp_monitor.py stats                    # Estadísticas del cache
./snmp_monitor.py logs --lines 50          # Ver logs recientes
./snmp_monitor.py clean-cache              # Limpiar cache
./snmp_monitor.py test-concurrent --requests 5  # Simular carga
./snmp_monitor.py monitor --interval 3     # Monitoreo en tiempo real
```

### 📄 `access_control/config/dispositivos.json`
**Función**: Configuración central del sistema SNMP
- **Mapeo IP-Dispositivo**: Router y Switch por IPv6
- **Mapeo ifIndex-Interface**: Puertos físicos mapeados
- **Acciones SNMP**: linkUp → conectar, linkDown → desconectar
- **VLAN por MAC**: Asignación automática de VLANs

**Estructura**:
```json
{
    "dispositivos_por_ip": {
        "203f:a:b:1::1": "ROUTER",
        "203f:a:b:10::2": "SWITCH"
    },
    "ifindex_to_interface": {
        "10001": "FastEthernet0/1",
        ...
    },
    "acciones": {
        "linkUp": ["ENLACE UP", "conectar"],
        "linkDown": ["ENLACE DOWN", "desconectar"]
    },
    "vlan_por_mac": {
        "30:13:8B:F1:00:BE": 20,
        "00:E0:4C:68:01:40": 30
    }
}
```

---

## 🔄 Flujo de Trabajo Automatizado

### 1. **Inicialización del Sistema**
```bash
# Desde directorio ANSIBLE/
# Configurar pools DHCPv6 en router
ansible-playbook -i inventory/inventory.yml playbooks/dhcp6_config.yml
```

### 2. **Monitoreo SNMP Activo**
```bash
# Desde directorio ANSIBLE/access_control/
# Iniciar monitoreo del sistema
./snmp_monitor.py monitor
```

### 3. **Proceso Automático por Evento**
Cuando un dispositivo se conecta:
1. **Switch envía trap SNMP** → `snmptrap_handler.py`
2. **Detecta MAC via SNMP** → `snmp_utils.py`
3. **Busca VLAN en config** → `dispositivos.json`
4. **Ejecuta playbooks**:
   - `vlan_config.yml` (crear VLAN)
   - `asignar_vlanxmac.yml` (asignar puerto)

Cuando un dispositivo se desconecta:
1. **Switch envía trap SNMP** → `snmptrap_handler.py`
2. **Ejecuta playbook**: `limpiar_puerto.yml`

### 4. **Gestión Manual**
```bash
# Limpiar cache SNMP
./snmp_monitor.py clean-cache

# Ver estadísticas
./snmp_monitor.py stats

# Configuración manual de VLAN
export VLAN_ID=20
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml
```

---

## 📊 Variables de Entorno Utilizadas

| Variable | Descripción | Usado en |
|----------|-------------|----------|
| `VLAN_ID` | ID de la VLAN a configurar | vlan_config.yml, asignar_vlanxmac.yml |
| `MAC_ADDRESS` | Dirección MAC del dispositivo | asignar_vlanxmac.yml |
| `PUERTO` | Nombre del puerto (ej: FastEthernet0/1) | asignar_vlanxmac.yml, limpiar_puerto.yml |

---

## 🛠️ Comandos de Ejecución por Contexto

### Desde directorio raíz ANSIBLE/:
```bash
# Configuraciones principales
ansible-playbook -i inventory/inventory.yml playbooks/dhcp6_config.yml
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml
ansible-playbook -i inventory/inventory.yml playbooks/asignar_vlanxmac.yml
ansible-playbook -i inventory/inventory.yml playbooks/limpiar_puerto.yml
```

### Desde directorio ANSIBLE/playbooks/:
```bash
# Playbooks de prueba
ansible-playbook -i ../inventory/inventory.yml routertest.yml
ansible-playbook -i ../inventory/inventory.yml switchtest.yml
```

### Desde directorio ANSIBLE/access_control/:
```bash
# Sistema SNMP
./snmp_monitor.py [comando]
python3 snmptrap_handler.py < trap_data
python3 -c "import snmp_utils; print('OK')"
```

---

## 🔧 Características de Simultaneidad

- **Thread-safe**: Todos los archivos compartidos protegidos con locks
- **Cache inteligente**: Reduce consultas SNMP duplicadas
- **Procesamiento concurrente**: Múltiples traps en paralelo
- **Control de concurrencia**: Evita ejecuciones duplicadas de playbooks
- **Timeouts**: Previene bloqueos indefinidos
- **Monitoreo**: Herramientas para supervisar el estado del sistema

El sistema está diseñado para **alta disponibilidad** y **procesamiento eficiente** de eventos SNMP en tiempo real.
