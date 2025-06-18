// Este archivo define las salidas del módulo de redes.

output "vlan10" {
  value = libvirt_network.vlan10.name // Devuelve el nombre de la red VLAN10
}

output "vlan20" {
  value = libvirt_network.vlan20.name // Devuelve el nombre de la red VLAN20
}
