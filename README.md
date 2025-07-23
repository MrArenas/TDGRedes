# Proyecto TDGRedes - Automatización de Redes con Ansible y Planificación con Terraform

Este proyecto automatiza la infraestructura de una **red basada en IPv6** utilizando herramientas modernas de DevOps aplicadas a la administración de redes.

## 🎯 Objetivos Generales

- **Automatización de configuración** de dispositivos Cisco con Ansible
- **Gestión de infraestructura virtual** con Terraform
- **Asignación dinámica de direcciones** mediante DHCPv6
- **Segmentación lógica** por VLANs
- **Supervisión de red** mediante SNMP
- **Infraestructura como Código** (IaC)

## ⚠️ Disclaimer de Versión

**IMPORTANTE**: La versión actual del proyecto integra funciones de simultaneidad y nuevas características experimentales. Si experimenta problemas de estabilidad o funcionamiento, se recomienda volver a la versión anterior estable del proyecto (Los manuales igualmente funcionan).

## 📚 Documentación Detallada

Para obtener información completa sobre la configuración, uso y guías prácticas:

### Ansible
- **Manual completo**: [`ANSIBLE/DOCUMENTACION_COMPLETA.md`](ANSIBLE/DOCUMENTACION_COMPLETA.md)
- **Guía práctica**: [`ANSIBLE/GUIA_USO_PRACTICA.md`](ANSIBLE/GUIA_USO_PRACTICA.md)

### Terraform
- **Manual completo**: [`TERRAFORM/DOCUMENTACION_COMPLETA.md`](TERRAFORM/DOCUMENTACION_COMPLETA.md)  
- **Guía práctica**: [`TERRAFORM/GUIA_USO_PRACTICA.md`](TERRAFORM/GUIA_USO_PRACTICA.md)

## 🚀 Inicio Rápido

### Ansible - Configuración de dispositivos
```bash
# Instalar dependencias
ansible-galaxy collection install cisco.ios

# Ejecutar configuración básica
ansible-playbook -i inventory/inventory.yml playbooks/vlan_config.yml
```

### Terraform - Infraestructura virtual
```bash
# Inicializar y aplicar
terraform init
terraform plan

terraform apply
```

## 🏗️ Estructura del Proyecto

```
TDGRedes/
├── README.md
├── ANSIBLE/                    # Automatización de dispositivos Cisco
│   ├── DOCUMENTACION_COMPLETA.md
│   ├── GUIA_USO_PRACTICA.md
│   ├── inventory/
│   ├── playbooks/
│   ├── roles/
│   └── access_control/         # Monitoreo SNMP
└── TERRAFORM/                  # Infraestructura virtual
    ├── DOCUMENTACION_COMPLETA.md
    ├── GUIA_USO_PRACTICA.md
    ├── modules/
    └── *.tf
```

## 🔧 Tecnologías Utilizadas

- **Ansible**: Automatización de configuración de dispositivos Cisco IOS
- **Terraform**: Gestión de infraestructura virtual con libvirt/QEMU
- **SNMP**: Monitoreo y gestión de red
- **IPv6**: Protocolo de red principal con DHCPv6
- **VLANs**: Segmentación lógica de la red

## 🎯 Beneficios del Proyecto

1. **Automatización**: Reducción de errores manuales y configuraciones consistentes
2. **Reproducibilidad**: Infraestructura como código versionable y reutilizable  
3. **Escalabilidad**: Arquitectura modular para crecimiento futuro
4. **Modernización**: Transición hacia DevOps en administración de redes
5. **Simulación**: Entorno virtual para pruebas y desarrollo

---

**Nota**: Para detalles técnicos, configuración avanzada y resolución de problemas, consulte los manuales específicos en cada directorio.

¡Este proyecto representa un paso hacia la modernización de la administración de redes mediante automatización !