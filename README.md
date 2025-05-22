# Proyecto TDGRedes - Automatización de Redes con Ansible

Este proyecto tiene como objetivo automatizar el aprovisionamiento de red utilizando **Ansible**, empleando dispositivos Cisco (router 2800 y switch C3560).

## 🌐 Topología de red

Identificador de red: 203F:A:B::/48

🏗️ Arquitectura General 
🔹 1. Nivel de Control y Automatización
Dispositivo:
    Nodo de control (Ubuntu 22.04)
    Funciones:
      Ejecuta Ansible para automatizar configuración de red.
      Funciona como servidor SNMP trap listener (recibe eventos de dispositivos).
      Tiene conexión directa al router principal.
      Aloja máquinas virtuales de laboratorio (Multipass).

🔹 2. Nivel de Infraestructura de Red (Cisco)
Dispositivo:
  Router Cisco 2800 (C2800NM-ADVENTERPRISEK9-M)
    IOS 15.1(4)M10
    Conectado directamente al nodo de control.
    Encargado de:
        Enrutamiento IPv6
        Servidor DHCPv6
        Distribuir direcciones a VLANs gestionadas por el switch
        Recibe configuraciones desde Ansible.

Switch Cisco C3560V2-24PS-E (Layer 3)
    IOS 12.2(55)SE12
    Conectado al router (subred 203F:A:10::/64)
    Encargado de:
        Crear y enrutar interfaces VLAN 
        Asignar puertos a VLANs como access.
        Reenviar solicitudes DHCPv6 hacia el router.
        Puede enviar SNMP traps cuando un dispositivo se conecta a un puerto.

🔹 3. Nivel de Acceso y Dispositivos Finales
    Equipos que se conectan a puertos del switch.
    Se asignan dinámicamente a VLANs configuradas.
    Obtienen dirección IPv6 vía DHCPv6 desde el router.
    Pueden ser:
        Equipos reales de una organización.

+---------------------+            +-----------------+            +------------------+
|     Nodo de Control |  <------>  |     Router       |  <------>  |     Switch        |
| (Ansible + SNMP mgr)|  eth0      |  Cisco 2800      |  F0/1      |  Cisco C3560 L3   |
+---------------------+            +-----------------+            +------------------+
        | eth1                                                       | VLANs (L3)
        |                                                            |  + DHCPv6 relay
        v                                                            |
  +------------------+                                               v
  | Laboratorio de   |                                    +----------------------+
  | máquinas virtuales|                                    | Equipos conectados   |
  +------------------+                                    +----------------------+

## 🧩 Estructura del Proyecto

TDGRedes/
├── ansible.cfg
├── inventory/
│ ├── inventory.yml
│ └── group_vars/
│ ├── all.yml
│ ├── switches.yml
│ └── routers.yml
├── roles/
│ ├── switch_vlan_dhcp/
│ │ └── tasks/main.yml
│ ├── router_dhcp6/
│ │ └── tasks/main.yml
├── playbooks/
│ ├── vlan_config.yml
│ ├── router_test.yml
│ └── switch_test.yml
└── README.md


## ⚙️ Funcionalidades implementadas

- Configuración automatizada de VLANs en switches Cisco.
- Asignación de puertos de acceso a VLANs.
- Ruteo entre VLANs a nivel de capa 3 en el switch.
- Configuración de DHCPv6 en el router.
- Distribución de direcciones IPv6 automáticamente a los equipos.
- Activación de servicios esenciales como SSH.

## 📦 Requisitos

- Ansible >= 2.10
- Colección `cisco.ios`:
  ```bash
  ansible-galaxy collection install cisco.ios
    Acceso por SSH a los dispositivos Cisco.
    Router Cisco 2800 con IOS 15.1(4)M10.
    Switch Cisco C3560 con IOS 12.2(55)SE12.

📘 Autor y propósito
