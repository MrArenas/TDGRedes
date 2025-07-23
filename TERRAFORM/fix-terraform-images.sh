#!/bin/bash
# fix-terraform-images.sh - Script de solución automática

set -e

echo "🔧 TDGRedes - Solucionador automático de imágenes"
echo "================================================"

cd /home/tdg2025/Escritorio/TDGRedes/TERRAFORM

# Verificar prerrequisitos
echo "🔍 Verificando prerrequisitos..."
systemctl is-active libvirtd >/dev/null || {
    echo "❌ libvirtd no está activo. Iniciando..."
    sudo systemctl start libvirtd
}

# Verificar permisos
if ! groups $USER | grep -q libvirt; then
    echo "⚠️ Usuario no está en grupo libvirt. Agregando..."
    sudo usermod -a -G libvirt $USER
    echo "⚠️ Reinicia la sesión para aplicar cambios de grupo"
fi

# Opción de imagen
echo ""
echo "📥 Selecciona una opción de imagen:"
echo "1) Descargar Ubuntu 20.04 Cloud (Recomendado)"
echo "2) Usar imagen existente en el sistema"
echo "3) Crear archivos dummy para testing"
echo ""
read -p "Opción (1-3): " option

case $option in
    1)
        echo "📥 Descargando Ubuntu Cloud Image..."
        if [ ! -f "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img" ]; then
            wget -O /tmp/focal-server-cloudimg-amd64.img \
                https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img
            sudo mv /tmp/focal-server-cloudimg-amd64.img /var/lib/libvirt/images/
            sudo chown root:libvirt /var/lib/libvirt/images/focal-server-cloudimg-amd64.img
            sudo chmod 644 /var/lib/libvirt/images/focal-server-cloudimg-amd64.img
        fi
        
        # Configurar terraform.tfvars
        cat > terraform.tfvars << 'EOF'
router_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
switch_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
client_image  = "/var/lib/libvirt/images/focal-server-cloudimg-amd64.img"
router_memory = 2024
switch_memory = 2024
client_memory = 1024
router_vcpu   = 2
switch_vcpu   = 2
client_vcpu   = 1
router_name = "router"
switch_name = "switch"
client_name = "client1"
libvirt_uri = "qemu:///system"
EOF
        ;;
    2)
        EXISTING_IMAGE=$(sudo ls /var/lib/libvirt/images/ | grep -E '\.(img|qcow2)$' | head -1)
        if [ -n "$EXISTING_IMAGE" ]; then
            echo "✅ Usando imagen existente: $EXISTING_IMAGE"
            cat > terraform.tfvars << EOF
router_image  = "/var/lib/libvirt/images/$EXISTING_IMAGE"
switch_image  = "/var/lib/libvirt/images/$EXISTING_IMAGE"
client_image  = "/var/lib/libvirt/images/$EXISTING_IMAGE"
router_memory = 1024
switch_memory = 1024
client_memory = 512
router_vcpu   = 1
switch_vcpu   = 1
client_vcpu   = 1
router_name = "router"
switch_name = "switch"
client_name = "client1"
libvirt_uri = "qemu:///system"
EOF
        else
            echo "❌ No se encontraron imágenes existentes"
            exit 1
        fi
        ;;
    3)
        echo "🧪 Creando archivos dummy para testing..."
        sudo touch /var/lib/libvirt/images/{router,switch,client}-test.qcow2
        sudo chown root:libvirt /var/lib/libvirt/images/*-test.qcow2
        sudo chmod 644 /var/lib/libvirt/images/*-test.qcow2
        
        cat > terraform.tfvars << 'EOF'
router_image  = "/var/lib/libvirt/images/router-test.qcow2"
switch_image  = "/var/lib/libvirt/images/switch-test.qcow2"
client_image  = "/var/lib/libvirt/images/client-test.qcow2"
router_memory = 256
switch_memory = 256
client_memory = 128
router_vcpu   = 1
switch_vcpu   = 1
client_vcpu   = 1
router_name = "test-router"
switch_name = "test-switch"
client_name = "test-client"
libvirt_uri = "qemu:///system"
EOF
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

# Verificar y aplicar
echo "✅ Configuración actualizada"
echo "🔧 Validando configuración de Terraform..."
terraform validate

echo "📋 Mostrando plan de ejecución..."
terraform plan

echo ""
read -p "🚀 ¿Aplicar configuración ahora? (y/N): " apply_now
if [[ "$apply_now" =~ ^[Yy]$ ]]; then
    terraform apply -auto-approve
    echo ""
    echo "📊 Recursos creados:"
    terraform output
    echo ""
    echo "✅ ¡Configuración aplicada exitosamente!"
else
    echo "⏸️ Configuración lista pero no aplicada"
    echo "💡 Ejecuta 'terraform apply' cuando estés listo"
fi

echo ""
echo "🎉 Problema resuelto!"
