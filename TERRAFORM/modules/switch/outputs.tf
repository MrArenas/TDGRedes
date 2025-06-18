// Este archivo define las salidas del módulo de switch.

output "switch_name" {
  value = libvirt_domain.switch.name // Devuelve el nombre del switch creado
}
