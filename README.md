# Proyecto TDGRedes - Automatización de Redes con Ansible y Planificación con Terraform

Este proyecto tiene como objetivo **automatizar la infraestructura de una red basada en IPv6**, incluyendo:

- Asignación dinámica de direcciones mediante DHCPv6.
- Segmentación lógica por VLANs.
- Ruteo entre subredes en dispositivos L3.
- Supervisión de red mediante SNMP.
- Automatización de configuración con **Ansible**.
- Gestión de infraestructura virtual con **Terraform**.

---

## 🔧 Ansible

### Descripción
La parte implementada del proyecto utiliza **Ansible** para automatizar la configuración de dispositivos Cisco (routers y switches). Esto permite reducir errores manuales, mejorar la eficiencia y garantizar configuraciones consistentes en la red.

### Funcionalidades implementadas
- **Creación de VLANs** en switches Cisco.
- **Asignación de puertos** a VLANs como puertos de acceso.
- **Configuración de interfaces L3** para enrutar VLANs.
- **Reenvío de solicitudes DHCPv6** desde el switch al router.
- **Gestión de pools DHCPv6** en el router para asignar direcciones IPv6 dinámicamente.
- **Configuración de SNMP** para recibir traps en el nodo de control.
- **Limpieza de puertos** cuando un dispositivo se desconecta.

### Estructura del proyecto
El proyecto está organizado de la siguiente manera:

```
TDGRedes/
├── ansible.cfg
├── inventory/
│   ├── inventory.yml
│   └── group_vars/
│       ├── all.yml
│       ├── switches.yml
│       └── routers.yml
├── roles/
│   ├── switch_vlan_dhcp/
│   │   └── main.yml
│   ├── router_dhcp6/
│   │   └── main.yml
│   ├── limpiar_puerto/
│   │   └── main.yml
│   ├── switch_mac_control/
│       └── main.yml
├── playbooks/
│   ├── vlan_config.yml
│   ├── dhcp6_config.yml
│   ├── asignar_vlanxmac.yml
│   ├── limpiar_puerto.yml
│   ├── routertest.yml
│   └── switchtest.yml
└── README.md
```

### Ejecución de Ansible
1. **Instalar dependencias**:
   ```bash
   ansible-galaxy collection install cisco.ios
   ```

2. **Ejecutar playbooks**:
   - Configuración de VLANs:
     ```bash
     ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml
     ```
   - Configuración de DHCPv6:
     ```bash
     ansible-playbook -i inventory/inventory.yml playbooks/dhcp6_config.yml
     ```
   - Limpieza de puertos:
     ```bash
     ansible-playbook -i inventory/inventory.yml playbooks/limpiar_puerto.yml
     ```

### Por qué Ansible
Ansible es ideal para redes físicas como las basadas en Cisco IOS porque:
- No requiere agentes en los dispositivos.
- Utiliza SSH para conectarse y aplicar configuraciones.
- Permite definir configuraciones como código reutilizable y versionable.
- Facilita la integración con herramientas de monitoreo y gestión como SNMP.

---

## ☁️ Terraform

### Descripción
Terraform se utiliza para gestionar la infraestructura virtual de la red en un entorno local utilizando el proveedor `libvirt`. Esto permite crear y configurar máquinas virtuales que simulan los nodos de la red, como routers, switches y clientes.

### Funcionalidades implementadas
- **Provisión de máquinas virtuales**:
  - Router, switch y cliente.
  - Configuración de recursos como memoria, CPU y discos.
- **Configuración de redes virtuales**:
  - Creación de VLANs y conexiones entre nodos.
- **Declaración de infraestructura como código**:
  - Uso de módulos para organizar y reutilizar configuraciones.

### Estructura del proyecto Terraform
El proyecto está organizado de la siguiente manera:

```
TERRAFORM/
├── main.tf
├── variables.tf
├── terraform.tfvars
├── outputs.tf
├── providers.tf
├── modules/
│   ├── network/
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── node/
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── router/
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   └── switch/
│       ├── main.tf
│       ├── outputs.tf
│       └── variables.tf
```

### Ejecución de Terraform
1. **Inicializar el proyecto**:
   ```bash
   terraform init
   ```

2. **Planificar la infraestructura**:
   ```bash
   terraform plan
   ```

3. **Aplicar la configuración**:
   ```bash
   terraform apply
   ```

4. **Destruir la infraestructura** (cuando ya no sea necesaria):
   ```bash
   terraform destroy
   ```

### Características principales
- **Uso de módulos**:
  - Organización modular para separar la lógica de cada componente (red, nodos, router, switch).
- **Proveedor `libvirt`**:
  - Gestión de máquinas virtuales en un entorno local (hipervisor QEMU/KVM).
- **Configuración flexible**:
  - Personalización de recursos mediante variables.
- **Automatización**:
  - Creación, configuración y destrucción de recursos de manera declarativa.

---

## 🎯 Enfoque del proyecto

Este proyecto tiene como objetivo:
1. **Automatizar la administración de redes tradicionales** (Cisco IOS) con herramientas modernas.
2. **Desarrollar infraestructura reproducible y bien documentada**.
3. **Modernizar la gestión de redes** mediante la transición hacia Infraestructura como Código.
4. **Facilitar la integración de herramientas** como Ansible y Terraform para cubrir todo el ciclo de vida de la infraestructura.
5. **Simular entornos virtuales** para pruebas y desarrollo utilizando Terraform y `libvirt`.

---

¡Este proyecto es un paso hacia la modernización de la administración de redes, combinando automatización, reproducibilidad y escalabilidad!