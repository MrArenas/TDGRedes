# Este archivo define los valores específicos para las variables del proyecto.
# Aquí se configuran las imágenes base, recursos de los nodos y nombres.

# Archivos de imágenes base
router_image  = "/var/lib/libvirt/images/{nombre imagen deseada}"
switch_image  = "/var/lib/libvirt/images/{nombre imagen deseada}"
client_image  = "/var/lib/libvirt/images/{nombre imagen deseada}"

# Recursos de los nodos
router_memory = 2024
switch_memory = 2024
client_memory = 2024

# Cantidad de CPU asignada a cada nodo
router_vcpu   = 2
switch_vcpu   = 2
client_vcpu   = 2

# Nombres (opcionalmente personalizables)
router_name = "router"
switch_name = "switch"
client_name = "client1"

# URI del proveedor libvirt
libvirt_uri = "qemu:///system"

