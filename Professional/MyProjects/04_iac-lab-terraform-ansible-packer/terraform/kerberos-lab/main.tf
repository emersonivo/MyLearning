# Terraform — Kerberos Lab on KVM
# Provisions 4 VMs: KDC + 2 clients + monitor

terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

# Isolated network
resource "libvirt_network" "kerberos_net" {
  name      = "kerberos-lab"
  mode      = "none"  # Fully isolated — no host routing
  bridge    = "br-kerberos"
  addresses = ["192.168.88.0/24"]
  dhcp { enabled = false }
  dns  { enabled = false }
}

# VM disk volumes (cloned from base image)
resource "libvirt_volume" "kerberos_disks" {
  for_each = var.vm_configs

  name           = "kerberos-${each.key}.qcow2"
  base_volume_id = var.base_image_path
  format         = "qcow2"
  size           = each.value.disk_gb * 1073741824
}

# Cloud-init disks
resource "libvirt_cloudinit_disk" "kerberos_init" {
  for_each = var.vm_configs

  name      = "kerberos-${each.key}-init.iso"
  user_data = templatefile("${path.module}/templates/user-data.tpl", {
    hostname = "kerberos-${each.key}"
    fqdn     = "kerberos-${each.key}.lab.local"
  })
  network_config = templatefile("${path.module}/templates/network-config.tpl", {
    ip_address = each.value.ip
  })
}

# VMs
resource "libvirt_domain" "kerberos_vms" {
  for_each = var.vm_configs

  name   = "kerberos-${each.key}"
  memory = each.value.memory_mb
  vcpu   = each.value.vcpus

  cloudinit = libvirt_cloudinit_disk.kerberos_init[each.key].id

  network_interface {
    network_id     = libvirt_network.kerberos_net.id
    addresses      = [each.value.ip]
    hostname       = "kerberos-${each.key}"
    wait_for_lease = true
  }

  disk {
    volume_id = libvirt_volume.kerberos_disks[each.key].id
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  graphics {
    type        = "spice"
    listen_type = "address"
    autoport    = true
  }
}
