// Este archivo configura un router virtual con dos interfaces de red.

resource "libvirt_domain" "router" {
  name   = var.name // Nombre del router
  memory = var.memory // Memoria asignada
  vcpu   = var.vcpu // Número de vCPUs

  disk {
    volume_id = libvirt_volume.router_disk.id // Disco asociado al router
  }

  network_interface {
    network_name = var.net1 // Primera interfaz de red
  }

  network_interface {
    network_name = var.net2 // Segunda interfaz de red
  }
}

resource "libvirt_volume" "router_disk" {
  name   = "${var.name}-disk" // Nombre del disco
  source = var.image // Imagen base para el disco
  format = "qcow2" // Formato del disco
}
