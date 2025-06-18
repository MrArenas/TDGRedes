// Este módulo configura las redes virtuales necesarias para la infraestructura.
module "networks" {
  source = "./modules/network"
}

// Configuración del módulo "router" (comentado actualmente).
// Este módulo crea un router virtual con dos interfaces de red conectadas a las VLANs.
module "router" {
  source = "./modules/router"
  name   = var.router_name
  image  = var.router_image
  memory = var.router_memory
  vcpu   = var.router_vcpu
  net1   = "default" // Red por defecto
  net2   = module.networks.vlan10 // Conexión a la VLAN10
}

// Configuración del módulo "switch" (comentado actualmente).
// Este módulo crea un switch virtual con dos interfaces de red conectadas a las VLANs.
module "switch" {
  source = "./modules/switch"
  name   = var.switch_name
  image  = var.switch_image
  memory = var.switch_memory
  vcpu   = var.switch_vcpu
  net1   = module.networks.vlan10 // Conexión a la VLAN10
  net2   = module.networks.vlan20 // Conexión a la VLAN20
}

// Configuración del módulo "client".
// Este módulo crea un cliente virtual conectado a la VLAN20.
module "client" {
  source = "./modules/node"
  name   = var.client_name
  image  = var.client_image
  memory = var.client_memory
  vcpu   = var.client_vcpu
  net    = module.networks.vlan20 // Conexión a la VLAN20
}
