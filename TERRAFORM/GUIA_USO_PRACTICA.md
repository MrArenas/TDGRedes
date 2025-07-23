# 🚀 Guía de Uso Práctica - Sistema Terraform TDGRedes

## 📝 Configuración Inicial Paso a Paso

### 🔧 1. Preparación del Entorno

#### Verificar libvirt
```bash
# Verificar que libvirt esté funcionando
sudo systemctl status libvirtd
sudo systemctl start libvirtd  # Si no está iniciado

# Verificar permisos de usuario
groups $USER | grep libvirt
# Si no aparece libvirt:
sudo usermod -a -G libvirt $USER
newgrp libvirt  # O reiniciar sesión
```

#### Verificar conectividad de red
```bash
# Listar redes virtuales existentes
virsh net-list --all

# Si no existe la red 'default':
sudo virsh net-define /etc/libvirt/qemu/networks/default.xml
sudo virsh net-start default
sudo virsh net-autostart default
```

### 🖼️ 2. Preparar Imágenes Base

#### Opción A: Usar imágenes Ubuntu Cloud
```bash
cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Descargar imagen Ubuntu 20.04 LTS
wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img

# Mover a directorio de libvirt
sudo mv focal-server-cloudimg-amd64.img /var/lib/libvirt/images/

# Actualizar terraform.tfvars
cat > terraform.tfvars << 'EOF'
# Archivos de imágenes base
router_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
switch_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
client_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"

# Recursos de los nodos
router_memory = 2024
switch_memory = 2024
client_memory = 1024

# Cantidad de CPU asignada
router_vcpu   = 2
switch_vcpu   = 2
client_vcpu   = 1

# Nombres
router_name = "router"
switch_name = "switch"
client_name = "client1"

# URI del proveedor libvirt
libvirt_uri = "qemu:///system"
EOF
```

#### Opción B: Usar imágenes existentes
```bash
# Listar imágenes disponibles
sudo ls -la /var/lib/libvirt/images/

# Actualizar terraform.tfvars con las rutas correctas
# Ejemplo si tienes una imagen Debian:
router_image = "/var/lib/libvirt/images/debian-12-generic-amd64.qcow2"
switch_image = "/var/lib/libvirt/images/debian-12-generic-amd64.qcow2"
client_image = "/var/lib/libvirt/images/debian-12-generic-amd64.qcow2"
```

### 🏗️ 3. Inicialización de Terraform

```bash
cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Inicializar Terraform (descargar proveedores)
terraform init

# Verificar configuración
terraform validate

# Ver plan de ejecución sin aplicar cambios
terraform plan
```

**Salida esperada**:
```
Plan: 8 to add, 0 to change, 0 to destroy.
```

---

## 🚀 Escenarios de Despliegue

### 📋 Escenario 1: Despliegue Completo

#### Desplegar toda la infraestructura
```bash
cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Aplicar toda la configuración
terraform apply

# O con auto-aprobación (para automatización)
terraform apply -auto-approve
```

**Recursos creados**:
- 2 redes virtuales (vlan10, vlan20)
- 1 router virtual con 2 interfaces
- 1 switch virtual con 2 interfaces  
- 1 cliente virtual con 1 interfaz
- 3 discos virtuales (qcow2)

#### Verificar resultado
```bash
# Listar VMs creadas
virsh list --all

# Verificar redes
virsh net-list --all

# Ver outputs de Terraform
terraform output
```

### 📋 Escenario 2: Despliegue Gradual

#### Paso 1: Crear solo las redes
```bash
# Crear únicamente las VLANs
terraform apply -target=module.networks

# Verificar redes creadas
virsh net-list --all
virsh net-dumpxml vlan10
virsh net-dumpxml vlan20
```

#### Paso 2: Crear router
```bash
# Crear router conectado a default y vlan10
terraform apply -target=module.router

# Verificar router
virsh list --all
virsh dominfo router
```

#### Paso 3: Crear switch
```bash
# Crear switch como bridge entre vlan10 y vlan20
terraform apply -target=module.switch

# Verificar switch
virsh dominfo switch
```

#### Paso 4: Crear cliente
```bash
# Crear cliente en vlan20
terraform apply -target=module.client

# Verificar cliente
virsh dominfo client1
```

### 📋 Escenario 3: Ambiente de Testing

#### Configuración mínima para pruebas
```bash
# Editar terraform.tfvars para recursos mínimos
cat > terraform.tfvars << 'EOF'
router_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
switch_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
client_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"

# Recursos mínimos para testing
router_memory = 512
switch_memory = 512
client_memory = 256

router_vcpu   = 1
switch_vcpu   = 1
client_vcpu   = 1

router_name = "test-router"
switch_name = "test-switch"
client_name = "test-client"

libvirt_uri = "qemu:///system"
EOF

# Aplicar configuración de testing
terraform apply
```

---

## 🔧 Configuraciones Avanzadas

### 🌐 Personalizar Redes

#### Modificar rangos IPv6
```bash
# Editar modules/network/main.tf
vim modules/network/main.tf

# Cambiar rangos de red:
resource "libvirt_network" "vlan10" {
  name       = "vlan10"
  mode       = "nat"
  domain     = "tdgredes.local"
  addresses  = ["203f:a:b:30::/64"]  # Nuevo rango
  autostart  = true
}

resource "libvirt_network" "vlan20" {
  name       = "vlan20"
  mode       = "nat"
  domain     = "tdgredes.local"
  addresses  = ["203f:a:b:40::/64"]  # Nuevo rango
  autostart  = true
}

# Aplicar cambios
terraform apply
```

#### Agregar nueva VLAN
```bash
# Editar modules/network/main.tf
vim modules/network/main.tf

# Agregar nueva red:
resource "libvirt_network" "vlan30" {
  name       = "vlan30"
  mode       = "nat"
  domain     = "tdgredes.local"
  addresses  = ["203f:a:b:50::/64"]
  autostart  = true
}

# Agregar output en modules/network/outputs.tf
echo 'output "vlan30" {
  value = libvirt_network.vlan30.name
}' >> modules/network/outputs.tf

# Aplicar cambios
terraform apply
```

### 💻 Agregar Más Clientes

#### Crear múltiples clientes
```bash
# Editar main.tf para agregar cliente adicional
vim main.tf

# Agregar segundo cliente:
module "client2" {
  source = "./modules/node"
  name   = "client2"
  image  = var.client_image
  memory = var.client_memory
  vcpu   = var.client_vcpu
  net    = module.networks.vlan10  # Conectar a vlan10
}

# Agregar output para el nuevo cliente
echo 'output "client2_name" {
  value = module.client2.client_name
}' >> outputs.tf

# Aplicar cambios
terraform apply
```

### 🔀 Configurar Router con Más Interfaces

#### Router multi-homed
```bash
# Crear nueva variable en variables.tf
echo 'variable "router_net3" {
  description = "Tercera red para el router"
  type        = string
  default     = "vlan30"
}' >> variables.tf

# Modificar modules/router/main.tf para agregar tercera interfaz
vim modules/router/main.tf

# Agregar tercera interfaz:
resource "libvirt_domain" "router" {
  name   = var.name
  memory = var.memory
  vcpu   = var.vcpu

  disk {
    volume_id = libvirt_volume.router_disk.id
  }

  network_interface {
    network_name = var.net1  # default
  }

  network_interface {
    network_name = var.net2  # vlan10
  }

  network_interface {
    network_name = var.net3  # nueva interfaz
  }
}

# Actualizar variables del módulo router
echo 'variable "net3" {}' >> modules/router/variables.tf

# Actualizar main.tf para pasar la nueva red
vim main.tf
# En module "router" agregar:
# net3 = module.networks.vlan30

terraform apply
```

---

## 🛠️ Gestión y Mantenimiento

### 📊 Monitoreo de Recursos

#### Verificar estado de VMs
```bash
# Listar todas las VMs
virsh list --all

# Ver detalles de una VM específica
virsh dominfo router
virsh dominfo switch
virsh dominfo client1

# Ver configuración de red de una VM
virsh domiflist router
virsh domiflist switch
```

#### Verificar uso de recursos
```bash
# Ver uso de CPU y memoria
virsh domstats router
virsh domstats switch
virsh domstats client1

# Ver información de disco
virsh domblklist router
virsh vol-list default
```

#### Verificar conectividad de red
```bash
# Listar redes y sus estados
virsh net-list --all

# Ver configuración detallada de red
virsh net-dumpxml vlan10
virsh net-dumpxml vlan20

# Ver interfaces de red del host
ip link show | grep virbr
```

### 🔄 Operaciones de Mantenimiento

#### Reiniciar VMs
```bash
# Reiniciar VM específica
virsh reboot router

# Apagar VM
virsh shutdown switch

# Encender VM
virsh start switch

# Forzar apagado
virsh destroy client1  # ¡Solo en emergencias!
```

#### Gestión de snapshots
```bash
# Crear snapshot de VM
virsh snapshot-create-as router snapshot1 "Snapshot antes de cambios"

# Listar snapshots
virsh snapshot-list router

# Restaurar snapshot
virsh snapshot-revert router snapshot1

# Eliminar snapshot
virsh snapshot-delete router snapshot1
```

#### Backup de discos
```bash
# Hacer backup de disco de VM
virsh vol-download router-disk /backup/router-disk-backup.qcow2 --pool default

# Restaurar desde backup
virsh vol-upload router-disk /backup/router-disk-backup.qcow2 --pool default
```

---

## 🔍 Resolución de Problemas

### ⚠️ Problema: Error de permisos
**Error**: `Permission denied`

**Diagnóstico**:
```bash
# Verificar permisos del usuario
groups $USER
ls -la /var/lib/libvirt/images/
```

**Solución**:
```bash
# Agregar usuario al grupo libvirt
sudo usermod -a -G libvirt $USER
newgrp libvirt

# Verificar permisos de archivos
sudo chmod 644 /var/lib/libvirt/images/*.img
sudo chown root:libvirt /var/lib/libvirt/images/*.img
```

### ⚠️ Problema: Red default no disponible
**Error**: `Network 'default' not found`

**Diagnóstico**:
```bash
virsh net-list --all
```

**Solución**:
```bash
# Crear y activar red default
sudo virsh net-define /etc/libvirt/qemu/networks/default.xml
sudo virsh net-start default
sudo virsh net-autostart default
```

### ⚠️ Problema: Imagen no encontrada
**Error**: `error while opening image: no such file or directory`

**Diagnóstico**:
```bash
ls -la /var/lib/libvirt/images/
cat terraform.tfvars | grep image
```

**Solución**:
```bash
# Verificar y corregir rutas en terraform.tfvars
# Descargar imagen si es necesaria
wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img
sudo mv focal-server-cloudimg-amd64.img /var/lib/libvirt/images/
```

### ⚠️ Problema: Puerto ocupado o conflicto de red
**Error**: `Address already in use`

**Diagnóstico**:
```bash
# Ver puertos en uso
ss -tulpn | grep :53
netstat -tulpn | grep :53

# Ver redes conflictivas
ip route show
```

**Solución**:
```bash
# Cambiar rango de red en modules/network/main.tf
addresses = ["203f:a:b:100::/64"]  # Usar rango diferente

# O detener servicios conflictivos temporalmente
sudo systemctl stop dnsmasq  # Si está usando el puerto 53
```

### ⚠️ Problema: VM no arranca
**Error**: VM queda en estado "shut off"

**Diagnóstico**:
```bash
# Ver logs de la VM
virsh dominfo router
cat /var/log/libvirt/qemu/router.log

# Verificar configuración
virsh dumpxml router
```

**Solución**:
```bash
# Intentar inicio manual
virsh start router

# Si falla, reducir recursos y probar
# Editar terraform.tfvars:
router_memory = 512
router_vcpu = 1

terraform apply
```

---

## 📈 Optimización de Rendimiento

### 💡 Configuración Recomendada por Uso

#### Para desarrollo ligero
```terraform
# terraform.tfvars para desarrollo
router_memory = 1024   # 1GB
switch_memory = 1024   # 1GB  
client_memory = 512    # 512MB

router_vcpu = 1
switch_vcpu = 1
client_vcpu = 1
```

#### Para testing intensivo
```terraform
# terraform.tfvars para testing
router_memory = 2048   # 2GB
switch_memory = 2048   # 2GB
client_memory = 1024   # 1GB

router_vcpu = 2
switch_vcpu = 2
client_vcpu = 1
```

#### Para laboratorio completo
```terraform
# terraform.tfvars para laboratorio
router_memory = 4096   # 4GB
switch_memory = 4096   # 4GB
client_memory = 2048   # 2GB

router_vcpu = 4
switch_vcpu = 4
client_vcpu = 2
```

### 🚀 Mejoras de Red

#### Configurar modo bridge (para mayor realismo)
```terraform
# En modules/network/main.tf cambiar mode
resource "libvirt_network" "vlan10" {
  name       = "vlan10"
  mode       = "bridge"      # Cambiar de "nat" a "bridge"
  bridge     = "virbr10"     # Bridge específico
  addresses  = ["203f:a:b:10::/64"]
  autostart  = true
}
```

#### Configurar modelo de interfaz de red más eficiente
```terraform
# En modules/router/main.tf
network_interface {
  network_name = var.net1
  model        = "virtio"    # Modelo más eficiente
}
```

---

## 🔄 Automatización y Scripts

### 📜 Script de despliegue completo
```bash
#!/bin/bash
# deploy.sh - Script de despliegue automatizado

set -e

echo "🚀 Iniciando despliegue de TDGRedes..."

cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Verificar prerrequisitos
echo "🔍 Verificando prerrequisitos..."
systemctl is-active libvirtd >/dev/null || {
    echo "❌ libvirtd no está activo"
    exit 1
}

# Verificar imágenes
if [ ! -f "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img" ]; then
    echo "📥 Descargando imagen Ubuntu..."
    wget -O /tmp/focal-server-cloudimg-amd64.img \
        https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img
    sudo mv /tmp/focal-server-cloudimg-amd64.img /var/lib/libvirt/images/
fi

# Inicializar Terraform
echo "🔧 Inicializando Terraform..."
terraform init

# Validar configuración
echo "✅ Validando configuración..."
terraform validate

# Mostrar plan
echo "📋 Plan de ejecución:"
terraform plan

# Aplicar configuración
echo "🚀 Aplicando configuración..."
terraform apply -auto-approve

# Mostrar resultados
echo "📊 Recursos creados:"
terraform output

echo "✅ Despliegue completado exitosamente!"
```

### 📜 Script de limpieza
```bash
#!/bin/bash
# cleanup.sh - Script de limpieza

set -e

echo "🧹 Iniciando limpieza de TDGRedes..."

cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Destruir recursos
echo "💥 Destruyendo recursos..."
terraform destroy -auto-approve

# Limpiar archivos temporales
echo "🗑️ Limpiando archivos temporales..."
rm -f terraform.tfstate.backup
rm -f .terraform.lock.hcl

echo "✅ Limpieza completada!"
```

### 📜 Script de monitoreo
```bash
#!/bin/bash
# monitor.sh - Script de monitoreo

echo "📊 Estado de la infraestructura TDGRedes"
echo "========================================"

echo ""
echo "🖥️ VMs activas:"
virsh list --all

echo ""
echo "🌐 Redes disponibles:"
virsh net-list --all

echo ""
echo "💾 Uso de almacenamiento:"
virsh vol-list default

echo ""
echo "📈 Outputs de Terraform:"
cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM
terraform output 2>/dev/null || echo "No hay outputs disponibles"
```

### Hacer scripts ejecutables
```bash
chmod +x deploy.sh cleanup.sh monitor.sh

# Ejecutar scripts
./deploy.sh    # Desplegar infraestructura
./monitor.sh   # Monitorear estado
./cleanup.sh   # Limpiar recursos
```

---

## 🎯 Casos de Uso Prácticos

### 1. **Laboratorio de IPv6**
- Practicar configuración de redes IPv6
- Testing de DHCPv6 y autoconfiguración
- Pruebas de routing entre VLANs

### 2. **Desarrollo de automatización**
- Testing de playbooks Ansible
- Validación de configuraciones de red
- Desarrollo de scripts de gestión

### 3. **Simulación de red empresarial**
- Topología router-switch-cliente
- Segmentación por VLANs
- Testing de políticas de seguridad

### 4. **Entrenamiento técnico**
- Aprendizaje de Terraform
- Práctica con libvirt/KVM
- Conceptos de virtualización de red

Este sistema Terraform proporciona una **plataforma completa de virtualización** para desarrollo, testing y aprendizaje de tecnologías de red IPv6 con automatización completa.
