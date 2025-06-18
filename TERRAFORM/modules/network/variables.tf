// Este archivo define las variables necesarias para el módulo de redes.
// Actualmente, no se utilizan variables específicas en este módulo.

terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7.0" // Versión del proveedor libvirt
    }
  }
}