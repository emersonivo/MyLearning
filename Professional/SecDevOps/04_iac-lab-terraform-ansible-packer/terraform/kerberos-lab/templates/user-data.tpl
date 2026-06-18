#cloud-config
hostname: ${hostname}
fqdn: ${fqdn}
manage_etc_hosts: true

users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users, admin
    shell: /bin/bash
    lock_passwd: false
    passwd: "$6$rounds=4096$saltsalt$hashed_password_here"

package_update: true
packages:
  - qemu-guest-agent
  - vim
  - curl
  - net-tools

runcmd:
  - systemctl enable qemu-guest-agent
  - systemctl start qemu-guest-agent
