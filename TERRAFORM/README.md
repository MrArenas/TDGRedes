# 📚 Índice de Documentación - Sistema Terraform TDGRedes

## 📋 Documentos Disponibles

### 📖 [DOCUMENTACION_COMPLETA.md](./DOCUMENTACION_COMPLETA.md)
**Documentación técnica completa del sistema Terraform**
- Estructura detallada del proyecto
- Configuración de cada módulo
- Variables y archivos de configuración
- Arquitectura de red virtual
- Comando y gestión de recursos

### 🚀 [GUIA_USO_PRACTICA.md](./GUIA_USO_PRACTICA.md)
**Guía práctica con ejemplos de uso**
- Configuración inicial paso a paso
- Escenarios de despliegue
- Configuraciones avanzadas
- Resolución de problemas
- Scripts de automatización

---

## 🎯 Inicio Rápido

### 1. **Revisar la documentación técnica**
```bash
# Entender la arquitectura y componentes
cat DOCUMENTACION_COMPLETA.md
```

### 2. **Seguir la guía práctica**
```bash
# Configuración y despliegue paso a paso
cat GUIA_USO_PRACTICA.md
```

### 3. **Verificar prerrequisitos**
```bash
# Verificar libvirt y permisos
systemctl status libvirtd
groups $USER | grep libvirt
```

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                Sistema Terraform TDGRedes                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🌐 Red Virtual IPv6                                       │
│  ├── default network (acceso externo)                      │
│  ├── VLAN10: 203f:a:b:10::/64                             │
│  └── VLAN20: 203f:a:b:20::/64                             │
│                                                             │
│  🖥️ Máquinas Virtuales                                    │
│  ├── Router (dual-homed: default + VLAN10)                │
│  ├── Switch (bridge: VLAN10 + VLAN20)                     │
│  └── Cliente (endpoint: VLAN20)                           │
│                                                             │
│  ⚙️ Infraestructura como Código                           │
│  ├── Módulos reutilizables                                │
│  ├── Variables configurables                              │
│  ├── Outputs informativos                                 │
│  └── Estado gestionado                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Componentes del Sistema

### 🗂️ **Estructura Modular**

| Módulo | Función | Recursos |
|--------|---------|----------|
| **network** | Gestión de VLANs | 2 redes virtuales IPv6 |
| **router** | Router virtual | VM + disco + 2 interfaces |
| **switch** | Switch virtual | VM + disco + 2 interfaces |
| **node** | Cliente virtual | VM + disco + 1 interfaz |

### ⚙️ **Archivos de Configuración**

| Archivo | Propósito | Contenido |
|---------|-----------|-----------|
| `providers.tf` | Configuración de proveedores | libvirt provider v0.7.0 |
| `variables.tf` | Definición de variables | Recursos, nombres, imágenes |
| `terraform.tfvars` | Valores de variables | Configuración específica |
| `main.tf` | Configuración principal | Integración de módulos |
| `outputs.tf` | Salidas del proyecto | Nombres de recursos creados |

### 🌐 **Topología de Red**

```
Internet
    │
┌───▼────┐     ┌─────────┐     ┌─────────┐
│ Router │◄────┤ Switch  │◄────┤ Client  │
│        │     │         │     │         │
└────────┘     └─────────┘     └─────────┘
    │               │               │
    │          ┌────▼────┐     ┌────▼────┐
    │          │ VLAN10  │     │ VLAN20  │
    │          │203f:a:b:│     │203f:a:b:│
    │          │10::/64  │     │20::/64  │
┌───▼────┐     └─────────┘     └─────────┘
│default │
│network │
└────────┘
```

---

## 🛠️ Comandos Esenciales

### Inicialización y validación
```bash
cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

terraform init                          # Inicializar Terraform
terraform validate                      # Validar configuración
terraform plan                          # Ver plan de ejecución
```

### Despliegue y gestión
```bash
terraform apply                         # Aplicar configuración completa
terraform apply -auto-approve           # Aplicar sin confirmación
terraform apply -target=module.networks # Aplicar módulo específico

terraform output                        # Ver outputs
terraform show                          # Ver estado actual
terraform state list                    # Listar recursos
```

### Destrucción y limpieza
```bash
terraform destroy                       # Destruir toda la infraestructura
terraform destroy -target=module.client # Destruir recurso específico
```

### Gestión de VMs con virsh
```bash
virsh list --all                        # Listar todas las VMs
virsh dominfo router                     # Info detallada de VM
virsh net-list --all                    # Listar redes virtuales
virsh domiflist router                  # Interfaces de red de VM
```

---

## 🚀 Flujos de Trabajo

### 1. **Despliegue Inicial**
```bash
# 1. Preparar imágenes base
wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img
sudo mv focal-server-cloudimg-amd64.img /var/lib/libvirt/images/

# 2. Configurar terraform.tfvars con rutas correctas
# 3. Inicializar y aplicar
terraform init
terraform validate
terraform plan
terraform apply
```

### 2. **Despliegue Gradual**
```bash
# Crear recursos paso a paso
terraform apply -target=module.networks  # 1. Crear redes
terraform apply -target=module.router    # 2. Crear router
terraform apply -target=module.switch    # 3. Crear switch
terraform apply -target=module.client    # 4. Crear cliente
```

### 3. **Desarrollo y Testing**
```bash
# Configuración mínima para desarrollo
# Editar terraform.tfvars con recursos reducidos
terraform apply                          # Desplegar ambiente de testing
# ... realizar pruebas ...
terraform destroy                        # Limpiar recursos
```

---

## ⚡ Características Principales

### ✅ **Beneficios del Sistema**

- **🏗️ Infraestructura como Código**: Versionable y reproducible
- **🔄 Modular**: Componentes reutilizables e independientes
- **🌐 Red IPv6 Completa**: VLANs con addressing IPv6 realista
- **⚙️ Configurable**: Variables para personalizar recursos
- **📊 Monitoreable**: Outputs y estado gestionado
- **🔧 Integrable**: Compatible con automatización Ansible

### 🎯 **Casos de Uso**

1. **Laboratorio de red IPv6**
2. **Testing de configuraciones Ansible**
3. **Desarrollo de automatización**
4. **Entrenamiento en virtualización**
5. **Simulación de topologías empresariales**

---

## 📞 Información de Contacto

**Proyecto**: TDGRedes - Infraestructura Virtual con Terraform
**Tecnologías**: Terraform + libvirt/KVM + IPv6
**Fecha**: Julio 2025
**Estado**: Funcional (requiere configuración de imágenes)

---

## 🔗 Enlaces Rápidos

- **[Configuración inicial →](./GUIA_USO_PRACTICA.md#-configuración-inicial-paso-a-paso)**
- **[Escenarios de despliegue →](./GUIA_USO_PRACTICA.md#-escenarios-de-despliegue)**
- **[Resolución de problemas →](./GUIA_USO_PRACTICA.md#-resolución-de-problemas)**
- **[Arquitectura técnica →](./DOCUMENTACION_COMPLETA.md#-estructura-del-proyecto)**
- **[Módulos →](./DOCUMENTACION_COMPLETA.md#-módulo-network-modulesnetwork)**

---

## ⚠️ Estado Actual del Proyecto

### ✅ **Funcionando**
- Configuración de Terraform completa
- Módulos bien estructurados
- Variables y outputs definidos
- Documentación completa

### ⚠️ **Requiere Atención**
- **Imágenes base**: Configurar rutas correctas en `terraform.tfvars`
- **Permisos**: Verificar permisos de usuario para libvirt
- **Red default**: Asegurar que la red default está disponible

### 🚀 **Comando de Verificación Rápida**
```bash
cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Verificar estado
terraform validate && echo "✅ Configuración válida" || echo "❌ Error en configuración"

# Verificar prerrequisitos
systemctl is-active libvirtd >/dev/null && echo "✅ libvirtd activo" || echo "❌ libvirtd inactivo"
groups $USER | grep -q libvirt && echo "✅ Permisos OK" || echo "❌ Falta grupo libvirt"
```

---

*Este sistema Terraform proporciona una plataforma completa de virtualización para desarrollo, testing y aprendizaje de tecnologías de red IPv6 con gestión automatizada de infraestructura.*
