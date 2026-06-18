# 🏗️ Infrastructure as Code Lab: Terraform + Ansible + Packer

> Fast, repeatable cybersecurity lab deployments on KVM/QEMU using IaC

[![Terraform](https://img.shields.io/badge/Terraform-1.x-purple.svg)](https://www.terraform.io/)
[![Ansible](https://img.shields.io/badge/Ansible-2.15+-red.svg)](https://www.ansible.com/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Author:** Emerson | **Target:** Ubuntu Desktop with KVM/QEMU

---

## Tool Relationships

```
PACKER   → Build base VM images (once)
    ↓
TERRAFORM → Provision VMs + networks (minutes)
    ↓
ANSIBLE   → Configure services (Kerberos, tools)
    ↓
TEST      → Validate lab functionality
    ↓
DESTROY & REBUILD → terraform destroy && terraform apply
```

## 15-Minute Setup

```bash
# 1. Install tools
sudo apt install -y terraform packer ansible libvirt-dev

# 2. Build base image
cd packer && packer build ubuntu-base.pkr.hcl

# 3. Deploy VMs
cd ../terraform/kerberos-lab
terraform init && terraform apply

# 4. Configure services
cd ../../ansible
terraform -chdir=../terraform/kerberos-lab output -raw ansible_inventory > inventory/kerberos
ansible-playbook -i inventory/kerberos playbooks/kerberos/site.yml

# 5. Verify
ansible -i inventory/kerberos all -m ping
```

## Lab Lifecycle

```bash
# Daily start
for vm in $(virsh list --all --name | grep kerberos); do virsh start $vm; done

# Rebuild after failed test (< 10 minutes)
cd terraform/kerberos-lab
terraform destroy -auto-approve && terraform apply -auto-approve
cd ../../ansible && ansible-playbook -i inventory/kerberos playbooks/kerberos/site.yml
```
