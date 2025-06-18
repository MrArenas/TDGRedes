// Este archivo define las variables utilizadas en el proyecto.
// Las variables permiten personalizar la configuración de los nodos y la conexión al proveedor.

variable "router_name" {}
variable "router_image" {}
variable "router_memory" { default = 1024 } // Memoria asignada al router (en MB)
variable "router_vcpu"   { default = 1 }    // Número de vCPUs asignadas al router

variable "libvirt_uri" {
  description = "URI de conexión para el proveedor libvirt"
  type        = string
  default     = "qemu:///system" // Cambia esto si usas otra URI
}

variable "switch_name" {
  description = "Nombre del switch virtual"
  type        = string
  default     = "default-switch"
}

variable "switch_image" {
  description = "Imagen base para el switch virtual"
  type        = string
  default     = "ubuntu-20.04-server-cloudimg-amd64.img"
}

variable "switch_memory" {
  description = "Memoria asignada al switch (en MB)"
  type        = number
  default     = 1024
}

variable "switch_vcpu" {
  description = "Número de vCPUs asignadas al switch"
  type        = number
  default     = 1
}

variable "client_name" {
  description = "Nombre del cliente virtual"
  type        = string
  default     = "default-client"
}

variable "client_image" {
  description = "Imagen base para el cliente virtual"
  type        = string
  default     = "ubuntu-20.04-server-cloudimg-amd64.img"
}

variable "client_memory" {
  description = "Memoria asignada al cliente (en MB)"
  type        = number
  default     = 512
}

variable "client_vcpu" {
  description = "Número de vCPUs asignadas al cliente"
  type        = number
  default     = 1
}
