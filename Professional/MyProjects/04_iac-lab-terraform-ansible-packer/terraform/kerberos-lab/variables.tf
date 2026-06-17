variable "base_image_path" {
  description = "Path to base qcow2 image built by Packer"
  default     = "/var/lib/libvirt/images/ubuntu-base-1.0.0.qcow2"
}

variable "vm_configs" {
  description = "Map of VM configurations"
  default = {
    kdc = {
      memory_mb = 2048
      vcpus     = 2
      disk_gb   = 20
      ip        = "192.168.88.20"
    }
    client1 = {
      memory_mb = 1024
      vcpus     = 1
      disk_gb   = 10
      ip        = "192.168.88.30"
    }
    client2 = {
      memory_mb = 1024
      vcpus     = 1
      disk_gb   = 10
      ip        = "192.168.88.31"
    }
    monitor = {
      memory_mb = 1024
      vcpus     = 1
      disk_gb   = 20
      ip        = "192.168.88.254"
    }
  }
}
