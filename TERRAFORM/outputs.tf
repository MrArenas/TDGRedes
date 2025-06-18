// Este archivo define las salidas principales del proyecto Terraform.
// Las salidas permiten acceder a información clave de los recursos creados.

output "vlan10" {
  value = module.networks.vlan10 // Devuelve el nombre de la VLAN10
}

output "vlan20" {
  value = module.networks.vlan20 // Devuelve el nombre de la VLAN20
}

output "router_name" {
  value = module.router.router_name // Devuelve el nombre del router
}

output "switch_name" {
  value = module.switch.switch_name // Devuelve el nombre del switch
}

output "client_name" {
  value = module.client.client_name // Devuelve el nombre del cliente
}