# Este archivo define los valores específicos para las variables del proyecto.
# Aquí se configuran las imágenes base, recursos de los nodos y nombres.

# Archivos de imágenes base
router_image  = "/var/lib/libvirt/images/router-base.qcow2"
switch_image  = "/var/lib/libvirt/images/switch-base.qcow2"
client_image  = "/var/lib/libvirt/images/client-base.qcow2"

# Recursos de los nodos
router_memory = 1024
switch_memory = 1024
client_memory = 512

router_vcpu   = 1
switch_vcpu   = 1
client_vcpu   = 1

# Nombres (opcionalmente personalizables)
router_name = "router"
switch_name = "switch"
client_name = "client1"

# URI del proveedor libvirt
libvirt_uri = "qemu:///system"

