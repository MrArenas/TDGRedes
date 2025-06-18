# Este archivo define las variables necesarias para el módulo de router.
# Estas variables permiten personalizar la configuración del router virtual.

terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"  # Proveedor para gestionar recursos en libvirt
      version = "~> 0.7.0"           # Versión del proveedor
    }
  }
}

# Nombre del router virtual
variable "name" {}

# Imagen base para el router virtual
variable "image" {}

# Memoria asignada al router (en MB)
variable "memory" { 
  default = 1024  # Valor predeterminado: 1024 MB
}

# Número de vCPUs asignadas al router
variable "vcpu" { 
  default = 1  # Valor predeterminado: 1 vCPU
}

# Primera red conectada al router
variable "net1" {}

# Segunda red conectada al router
variable "net2" {}

