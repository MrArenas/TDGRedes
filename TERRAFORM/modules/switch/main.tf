# Este archivo configura un switch virtual con dos interfaces de red.
# El switch se implementa como un dominio en libvirt y utiliza una imagen base para su disco.

resource "libvirt_domain" "switch" {
  name   = var.name   # Nombre del switch virtual
  memory = var.memory # Memoria asignada al switch (en MB)
  vcpu   = var.vcpu   # Número de vCPUs asignadas al switch

  # Configuración del disco del switch
  disk {
    volume_id = libvirt_volume.switch_disk.id # Disco asociado al switch
  }

  # Primera interfaz de red conectada al switch
  network_interface {
    network_name = var.net1
  }

  # Segunda interfaz de red conectada al switch
  network_interface {
    network_name = var.net2
  }
}

# Configuración del disco del switch virtual
resource "libvirt_volume" "switch_disk" {
  name   = "${var.name}-disk" # Nombre del disco
  source = var.image          # Imagen base para el disco
  format = "qcow2"            # Formato del disco
}
