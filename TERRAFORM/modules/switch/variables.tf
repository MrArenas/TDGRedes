terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7.0"
    }
  }
}

variable "name" {
  description = "Nombre del switch virtual"
  type        = string
}

variable "image" {
  description = "Imagen base para el switch virtual"
  type        = string
}

variable "memory" {
  description = "Memoria asignada al switch (en MB)"
  type        = number
  default     = 1024
}

variable "vcpu" {
  description = "Número de vCPUs asignadas al switch"
  type        = number
  default     = 1
}

variable "net1" {
  description = "Primera red conectada al switch"
  type        = string
}

variable "net2" {
  description = "Segunda red conectada al switch"
  type        = string
}