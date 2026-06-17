# Packer HCL — Ubuntu 22.04 Base Image for KVM Lab
# Usage: packer build ubuntu-base.pkr.hcl

packer {
  required_plugins {
    qemu = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/qemu"
    }
  }
}

variable "version" {
  default = "1.0.0"
}

source "qemu" "ubuntu-base" {
  iso_url      = "https://releases.ubuntu.com/22.04/ubuntu-22.04-live-server-amd64.iso"
  iso_checksum = "sha256:10f19c5b2b8d6db711582e0e27f5116296c34fe4b313ba45f9b201a5007056cb"

  vm_name          = "ubuntu-base-${var.version}.qcow2"
  output_directory = "/var/lib/libvirt/images"
  disk_size        = "20G"
  format           = "qcow2"
  memory           = 2048
  cpus             = 2

  http_directory = "http"
  boot_command = [
    "<esc><wait>",
    "linux /casper/vmlinuz quiet autoinstall ds=nocloud-net;seedfrom=http://{{.HTTPIP}}:{{.HTTPPort}}/ ---<enter>",
    "initrd /casper/initrd<enter>",
    "boot<enter>"
  ]

  ssh_username     = "ubuntu"
  ssh_password     = "ubuntu"
  ssh_timeout      = "30m"
  shutdown_command = "echo 'ubuntu' | sudo -S shutdown -P now"
}

build {
  sources = ["source.qemu.ubuntu-base"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update -qq",
      "sudo apt-get install -y qemu-guest-agent vim curl net-tools python3 python3-pip",
      "sudo systemctl enable qemu-guest-agent",
      "sudo apt-get clean",
      "sudo dd if=/dev/zero of=/tmp/bigfile bs=1M count=1000 || true",
      "sudo rm -f /tmp/bigfile"
    ]
  }
}
