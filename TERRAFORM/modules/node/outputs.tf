// Este archivo define las salidas del módulo de cliente.

output "client_name" {
  value = libvirt_domain.client.name // Devuelve el nombre del cliente creado
}
