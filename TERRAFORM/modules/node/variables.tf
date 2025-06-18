# Este archivo define las variables necesarias para el módulo de cliente (node).
# Estas variables permiten personalizar la configuración del cliente virtual.

terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"  # Proveedor para gestionar recursos en libvirt
      version = "~> 0.7.0"           # Versión del proveedor
    }
  }
}

# Nombre del cliente virtual
variable "name" {}

# Imagen base para el cliente virtual
variable "image" {}

# Memoria asignada al cliente (en MB)
variable "memory" { 
  default = 512  # Valor predeterminado: 512 MB
}

# Número de vCPUs asignadas al cliente
variable "vcpu" { 
  default = 1  # Valor predeterminado: 1 vCPU
}

# Red a la que se conecta el cliente
variable "net" {}