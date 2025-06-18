# Este archivo configura un cliente virtual (node) en la infraestructura.
# El cliente se implementa como un dominio en libvirt y utiliza una imagen base para su disco.

resource "libvirt_domain" "client" {
  name   = var.name   # Nombre del cliente virtual
  memory = var.memory # Memoria asignada al cliente (en MB)
  vcpu   = var.vcpu   # Número de vCPUs asignadas al cliente

  # Configuración del disco del cliente
  disk {
    volume_id = libvirt_volume.client_disk.id # Disco asociado al cliente
  }

  # Interfaz de red conectada al cliente
  network_interface {
    network_name = var.net # Red a la que se conecta el cliente
  }
}

# Configuración del disco del cliente virtual
resource "libvirt_volume" "client_disk" {
  name   = "${var.name}-disk" # Nombre del disco
  source = var.image          # Imagen base para el disco
  format = "qcow2"            # Formato del disco
}
