// Este archivo define las salidas del módulo router.

output "router_name" {
  value = libvirt_domain.router.name // Devuelve el nombre del router creado
}
