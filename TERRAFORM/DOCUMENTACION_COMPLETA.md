# 📚 Documentación Completa del Sistema Terraform - TDGRedes

## 📁 Estructura del Proyecto

```
TERRAFORM/
├── providers.tf                         # Configuración de proveedores
├── variables.tf                         # Variables principales del proyecto
├── terraform.tfvars                     # Valores de las variables
├── main.tf                              # Configuración principal - módulos
├── outputs.tf                           # Salidas del proyecto
├── terraform.tfstate                    # Estado de Terraform (generado)
└── modules/                             # Módulos reutilizables
    ├── network/                         # Módulo de redes (VLANs)
    │   ├── main.tf                      # Configuración de redes virtuales
    │   ├── variables.tf                 # Variables del módulo network
    │   └── outputs.tf                   # Salidas del módulo network
    ├── router/                          # Módulo del router virtual
    │   ├── main.tf                      # Configuración del router
    │   ├── variables.tf                 # Variables del módulo router
    │   └── outputs.tf                   # Salidas del módulo router
    ├── switch/                          # Módulo del switch virtual
    │   ├── main.tf                      # Configuración del switch
    │   ├── variables.tf                 # Variables del módulo switch
    │   └── outputs.tf                   # Salidas del módulo switch
    └── node/                            # Módulo de cliente/nodo
        ├── main.tf                      # Configuración del cliente
        ├── variables.tf                 # Variables del módulo node
        └── outputs.tf                   # Salidas del módulo node
```

---

## ⚙️ Archivos de Configuración Principal

### 📄 `providers.tf`
**Función**: Configuración de proveedores necesarios para el proyecto
```terraform
terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7.0"              # Versión específica del proveedor
    }
  }
}

provider "libvirt" {
  uri = var.libvirt_uri                  # URI de conexión a libvirt
}
```

**Características**:
- **Proveedor**: dmacvicar/libvirt para gestión de VMs en KVM/QEMU
- **Versión**: ~> 0.7.0 (compatible con versiones 0.7.x)
- **URI**: Configurable via variable (por defecto: qemu:///system)

### 📄 `variables.tf`
**Función**: Definición de variables principales del proyecto
```terraform
# Variables del router
variable "router_name" {}                # Nombre del router
variable "router_image" {}               # Imagen base del router
variable "router_memory" { default = 1024 } # Memoria en MB
variable "router_vcpu" { default = 1 }   # Número de vCPUs

# Variables del switch
variable "switch_name" {}                # Nombre del switch
variable "switch_image" {}               # Imagen base del switch
variable "switch_memory" { default = 1024 } # Memoria en MB
variable "switch_vcpu" { default = 1 }   # Número de vCPUs

# Variables del cliente
variable "client_name" {}                # Nombre del cliente
variable "client_image" {}               # Imagen base del cliente
variable "client_memory" { default = 512 } # Memoria en MB
variable "client_vcpu" { default = 1 }   # Número de vCPUs

# Configuración de libvirt
variable "libvirt_uri" {
  default = "qemu:///system"             # URI de conexión por defecto
}
```

**Tipos de variables**:
- **Obligatorias**: router_name, router_image, switch_name, etc.
- **Opcionales**: Con valores por defecto (memory, vcpu)
- **Configurables**: URI de libvirt, recursos de hardware

### 📄 `terraform.tfvars`
**Función**: Valores específicos para las variables del proyecto
```terraform-vars
# Archivos de imágenes base
router_image  = "/var/lib/libvirt/images/{nombre imagen deseada}"
switch_image  = "/var/lib/libvirt/images/{nombre imagen deseada}"
client_image  = "/var/lib/libvirt/images/{nombre imagen deseada}"

# Recursos de los nodos
router_memory = 2024    # 2GB RAM para router
switch_memory = 2024    # 2GB RAM para switch
client_memory = 2024    # 2GB RAM para cliente

# Cantidad de CPU asignada
router_vcpu   = 2       # 2 vCPUs para router
switch_vcpu   = 2       # 2 vCPUs para switch
client_vcpu   = 2       # 2 vCPUs para cliente

# Nombres de los nodos
router_name = "router"
switch_name = "switch"
client_name = "client1"

# URI del proveedor libvirt
libvirt_uri = "qemu:///system"
```

**⚠️ Nota importante**: Las rutas de imágenes están configuradas como plantillas y necesitan ser actualizadas con imágenes reales.

### 📄 `main.tf`
**Función**: Configuración principal que integra todos los módulos
```terraform
# Módulo de redes - Crea VLANs virtuales
module "networks" {
  source = "./modules/network"
}

# Módulo de router - Router virtual con 2 interfaces
module "router" {
  source = "./modules/router"
  name   = var.router_name
  image  = var.router_image
  memory = var.router_memory
  vcpu   = var.router_vcpu
  net1   = "default"                     # Red por defecto
  net2   = module.networks.vlan10        # VLAN10
}

# Módulo de switch - Switch virtual con 2 interfaces
module "switch" {
  source = "./modules/switch"
  name   = var.switch_name
  image  = var.switch_image
  memory = var.switch_memory
  vcpu   = var.switch_vcpu
  net1   = module.networks.vlan10        # VLAN10
  net2   = module.networks.vlan20        # VLAN20
}

# Módulo de cliente - Cliente conectado a VLAN20
module "client" {
  source = "./modules/node"
  name   = var.client_name
  image  = var.client_image
  memory = var.client_memory
  vcpu   = var.client_vcpu
  net    = module.networks.vlan20        # VLAN20
}
```

**Arquitectura de red**:
- **Router**: Conectado a red "default" + VLAN10
- **Switch**: Conectado a VLAN10 + VLAN20
- **Cliente**: Conectado a VLAN20

### 📄 `outputs.tf`
**Función**: Definición de salidas del proyecto
```terraform
output "vlan10" {
  value = module.networks.vlan10          # Nombre de VLAN10
}

output "vlan20" {
  value = module.networks.vlan20          # Nombre de VLAN20
}

output "router_name" {
  value = module.router.router_name       # Nombre del router
}

output "switch_name" {
  value = module.switch.switch_name       # Nombre del switch
}

output "client_name" {
  value = module.client.client_name       # Nombre del cliente
}
```

---

## 🌐 Módulo Network (`modules/network/`)

### 📄 `modules/network/main.tf`
**Función**: Configuración de redes virtuales (VLANs)
```terraform
resource "libvirt_network" "vlan10" {
  name       = "vlan10"                  # Nombre de la red
  mode       = "nat"                     # Modo NAT para acceso externo
  domain     = "tdgredes.local"          # Dominio asociado
  addresses  = ["203f:a:b:10::/64"]      # Rango IPv6
  autostart  = true                      # Inicio automático
}

resource "libvirt_network" "vlan20" {
  name       = "vlan20"
  mode       = "nat"
  domain     = "tdgredes.local"
  addresses  = ["203f:a:b:20::/64"]
  autostart  = true
}
```

**Características**:
- **2 VLANs**: vlan10 y vlan20
- **Modo NAT**: Permite conectividad externa
- **IPv6**: Rangos 203f:a:b:10::/64 y 203f:a:b:20::/64
- **Autostart**: Las redes se inician automáticamente
- **Dominio**: tdgredes.local para resolución DNS

### 📄 `modules/network/variables.tf`
**Función**: Variables del módulo de red
```terraform
terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7.0"
    }
  }
}
```

**Nota**: Actualmente no define variables específicas, solo la configuración del proveedor.

### 📄 `modules/network/outputs.tf`
**Función**: Salidas del módulo de red
```terraform
output "vlan10" {
  value = libvirt_network.vlan10.name    # Nombre de VLAN10
}

output "vlan20" {
  value = libvirt_network.vlan20.name    # Nombre de VLAN20
}
```

---

## 🔀 Módulo Router (`modules/router/`)

### 📄 `modules/router/main.tf`
**Función**: Configuración del router virtual
```terraform
resource "libvirt_domain" "router" {
  name   = var.name                      # Nombre del router
  memory = var.memory                    # Memoria asignada
  vcpu   = var.vcpu                      # Número de vCPUs

  disk {
    volume_id = libvirt_volume.router_disk.id  # Disco del router
  }

  network_interface {
    network_name = var.net1              # Primera interfaz (default)
  }

  network_interface {
    network_name = var.net2              # Segunda interfaz (VLAN10)
  }
}

resource "libvirt_volume" "router_disk" {
  name   = "${var.name}-disk"            # Nombre del disco
  source = var.image                     # Imagen base
  format = "qcow2"                       # Formato de disco
}
```

**Características**:
- **Dual-homed**: 2 interfaces de red
- **Disco QCOW2**: Eficiente en almacenamiento
- **Recursos configurables**: Memoria y vCPUs variables

### 📄 `modules/router/variables.tf`
**Función**: Variables del módulo router
```terraform
variable "name" {}                       # Nombre del router
variable "image" {}                      # Imagen base
variable "memory" { default = 1024 }     # Memoria por defecto: 1GB
variable "vcpu" { default = 1 }          # vCPUs por defecto: 1
variable "net1" {}                       # Primera red
variable "net2" {}                       # Segunda red
```

### 📄 `modules/router/outputs.tf`
**Función**: Salidas del módulo router
```terraform
output "router_name" {
  value = libvirt_domain.router.name     # Nombre del router creado
}
```

---

## 🔄 Módulo Switch (`modules/switch/`)

### 📄 `modules/switch/main.tf`
**Función**: Configuración del switch virtual
```terraform
resource "libvirt_domain" "switch" {
  name   = var.name                      # Nombre del switch
  memory = var.memory                    # Memoria asignada
  vcpu   = var.vcpu                      # Número de vCPUs

  disk {
    volume_id = libvirt_volume.switch_disk.id  # Disco del switch
  }

  network_interface {
    network_name = var.net1              # Primera interfaz (VLAN10)
  }

  network_interface {
    network_name = var.net2              # Segunda interfaz (VLAN20)
  }
}

resource "libvirt_volume" "switch_disk" {
  name   = "${var.name}-disk"            # Nombre del disco
  source = var.image                     # Imagen base
  format = "qcow2"                       # Formato de disco
}
```

**Características**:
- **Bridge entre VLANs**: Conecta VLAN10 y VLAN20
- **Funcionalidad de switching**: Manejo de tráfico L2
- **Configuración similar al router**: Mismo patrón de recursos

### 📄 `modules/switch/variables.tf`
**Función**: Variables del módulo switch
```terraform
variable "name" {}                       # Nombre del switch
variable "image" {}                      # Imagen base
variable "memory" { default = 1024 }     # Memoria por defecto: 1GB
variable "vcpu" { default = 1 }          # vCPUs por defecto: 1
variable "net1" {}                       # Primera red (VLAN10)
variable "net2" {}                       # Segunda red (VLAN20)
```

### 📄 `modules/switch/outputs.tf`
**Función**: Salidas del módulo switch
```terraform
output "switch_name" {
  value = libvirt_domain.switch.name     # Nombre del switch creado
}
```

---

## 💻 Módulo Node/Client (`modules/node/`)

### 📄 `modules/node/main.tf`
**Función**: Configuración del cliente virtual
```terraform
resource "libvirt_domain" "client" {
  name   = var.name                      # Nombre del cliente
  memory = var.memory                    # Memoria asignada
  vcpu   = var.vcpu                      # Número de vCPUs

  disk {
    volume_id = libvirt_volume.client_disk.id  # Disco del cliente
  }

  network_interface {
    network_name = var.net               # Red conectada (VLAN20)
  }
}

resource "libvirt_volume" "client_disk" {
  name   = "${var.name}-disk"            # Nombre del disco
  source = var.image                     # Imagen base
  format = "qcow2"                       # Formato de disco
}
```

**Características**:
- **Single-homed**: 1 interfaz de red
- **Cliente final**: Conectado a VLAN20
- **Recursos reducidos**: Por defecto menos memoria (512MB)

### 📄 `modules/node/variables.tf`
**Función**: Variables del módulo node
```terraform
variable "name" {}                       # Nombre del cliente
variable "image" {}                      # Imagen base
variable "memory" { default = 512 }      # Memoria por defecto: 512MB
variable "vcpu" { default = 1 }          # vCPUs por defecto: 1
variable "net" {}                        # Red conectada
```

### 📄 `modules/node/outputs.tf`
**Función**: Salidas del módulo node
```terraform
output "client_name" {
  value = libvirt_domain.client.name     # Nombre del cliente creado
}
```

---

## 🚀 Comandos de Ejecución

### Preparación inicial
```bash
cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Inicializar Terraform (descargar proveedores)
terraform init

# Validar configuración
terraform validate

# Ver plan de ejecución
terraform plan
```

### Despliegue de infraestructura
```bash
# Aplicar configuración (crear recursos)
terraform apply

# Aplicar con auto-aprobación
terraform apply -auto-approve

# Aplicar solo un módulo específico
terraform apply -target=module.networks
terraform apply -target=module.router
terraform apply -target=module.switch
terraform apply -target=module.client
```

### Gestión de estado
```bash
# Ver estado actual
terraform show

# Listar recursos
terraform state list

# Ver outputs
terraform output

# Ver output específico
terraform output vlan10
terraform output router_name
```

### Destrucción de recursos
```bash
# Destruir toda la infraestructura
terraform destroy

# Destruir recurso específico
terraform destroy -target=module.client
terraform destroy -target=module.switch
```

---

## 🔧 Configuración y Personalización

### Modificar recursos de hardware
```bash
# Editar terraform.tfvars
router_memory = 4096    # 4GB para router
switch_memory = 2048    # 2GB para switch
client_memory = 1024    # 1GB para cliente

router_vcpu = 4         # 4 vCPUs para router
switch_vcpu = 2         # 2 vCPUs para switch
client_vcpu = 1         # 1 vCPU para cliente
```

### Configurar imágenes base
```bash
# Actualizar rutas de imágenes en terraform.tfvars
router_image = "/var/lib/libvirt/images/router-cisco.qcow2"
switch_image = "/var/lib/libvirt/images/switch-cisco.qcow2"
client_image = "/var/lib/libvirt/images/ubuntu-20.04.qcow2"
```

### Cambiar configuración de red
```bash
# Modificar modules/network/main.tf para diferentes rangos
addresses = ["203f:a:b:30::/64"]  # Nueva VLAN30
addresses = ["203f:a:b:40::/64"]  # Nueva VLAN40
```

---

## 🌐 Arquitectura de Red Virtual

```
┌─────────────────────────────────────────────────────────────┐
│                    Red Virtual TDGRedes                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🌐 default network                                        │
│  │                                                         │
│  ├── 🔀 Router ────┐                                       │
│  │    (dual-homed) │                                       │
│  │                 │                                       │
│  │  🌐 VLAN10 ─────┴─── 🔄 Switch ─────┐                  │
│  │  203f:a:b:10::/64    (bridge)       │                  │
│  │                                      │                  │
│  │                   🌐 VLAN20 ─────────┴─── 💻 Client    │
│  │                   203f:a:b:20::/64                      │
│  │                                                         │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de tráfico:
1. **Router**: Conectado a red externa (default) y VLAN10
2. **Switch**: Bridge entre VLAN10 y VLAN20
3. **Cliente**: Endpoint en VLAN20

---

## 📊 Recursos Creados

| Recurso | Tipo | Descripción |
|---------|------|-------------|
| **vlan10** | libvirt_network | Red virtual 203f:a:b:10::/64 |
| **vlan20** | libvirt_network | Red virtual 203f:a:b:20::/64 |
| **router** | libvirt_domain | Router virtual con 2 interfaces |
| **router-disk** | libvirt_volume | Disco del router (QCOW2) |
| **switch** | libvirt_domain | Switch virtual con 2 interfaces |
| **switch-disk** | libvirt_volume | Disco del switch (QCOW2) |
| **client1** | libvirt_domain | Cliente virtual con 1 interfaz |
| **client1-disk** | libvirt_volume | Disco del cliente (QCOW2) |

---

## ⚠️ Problemas Conocidos

### 1. **Imágenes base faltantes**
**Error**: `error while opening /var/lib/libvirt/images/router-base.qcow2: no such file or directory`

**Solución**:
```bash
# Descargar imágenes apropiadas
wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img
sudo mv focal-server-cloudimg-amd64.img /var/lib/libvirt/images/

# Actualizar terraform.tfvars con rutas correctas
router_image = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
switch_image = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
client_image = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
```

### 2. **Permisos de libvirt**
**Error**: Permission denied al crear VMs

**Solución**:
```bash
# Agregar usuario al grupo libvirt
sudo usermod -a -G libvirt $USER

# Reiniciar sesión o usar newgrp
newgrp libvirt
```

### 3. **Red default no disponible**
**Error**: Network 'default' not found

**Solución**:
```bash
# Crear red default si no existe
sudo virsh net-define /etc/libvirt/qemu/networks/default.xml
sudo virsh net-start default
sudo virsh net-autostart default
```

---

## 🔄 Flujo de Trabajo Recomendado

### 1. **Preparación**
```bash
# Verificar que libvirt esté funcionando
sudo systemctl status libvirtd
virsh list --all

# Verificar redes disponibles
virsh net-list --all
```

### 2. **Configurar imágenes**
```bash
# Descargar imágenes necesarias
# Actualizar terraform.tfvars con rutas correctas
```

### 3. **Despliegue gradual**
```bash
# 1. Crear solo las redes
terraform apply -target=module.networks

# 2. Crear router
terraform apply -target=module.router

# 3. Crear switch
terraform apply -target=module.switch

# 4. Crear cliente
terraform apply -target=module.client
```

### 4. **Verificación**
```bash
# Verificar VMs creadas
virsh list --all

# Verificar redes
virsh net-list --all

# Ver información detallada
virsh dominfo router
virsh dominfo switch
virsh dominfo client1
```

Este sistema Terraform proporciona una **infraestructura de red virtual completa** para testing y desarrollo de configuraciones de red IPv6 con VLANs.
