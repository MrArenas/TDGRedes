terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7.0" // Versión del proveedor libvirt
    }
  }
}

// Configuración del proveedor libvirt.
// La URI especifica cómo conectarse al hipervisor (por defecto, QEMU/KVM local).
provider "libvirt" {
  uri = var.libvirt_uri // Variable que define la URI de conexión
}
