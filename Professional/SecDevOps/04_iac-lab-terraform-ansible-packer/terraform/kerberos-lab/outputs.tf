output "vm_ips" {
  value = {
    for vm_name, vm in libvirt_domain.kerberos_vms :
    vm_name => vm.network_interface[0].addresses[0]
  }
  description = "IP addresses of all Kerberos lab VMs"
}

output "kdc_ip" {
  value       = libvirt_domain.kerberos_vms["kdc"].network_interface[0].addresses[0]
  description = "KDC IP address"
}

output "ansible_inventory" {
  value = templatefile("${path.module}/templates/inventory.tpl", {
    vms = libvirt_domain.kerberos_vms
  })
  description = "Ansible inventory file content"
}
