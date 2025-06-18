// Este archivo configura las redes virtuales (VLANs) necesarias para la infraestructura.

resource "libvirt_network" "vlan10" {
  name       = "vlan10" // Nombre de la red
  mode       = "nat"    // Modo NAT para permitir acceso externo
  domain     = "tdgredes.local" // Dominio asociado a la red
  addresses  = ["203f:a:b:10::/64"] // Rango de direcciones IPv6
  autostart  = true // Inicia automáticamente la red al arrancar el hipervisor
}

resource "libvirt_network" "vlan20" {
  name       = "vlan20"
  mode       = "nat"
  domain     = "tdgredes.local"
  addresses  = ["203f:a:b:20::/64"]
  autostart  = true
}
