# Handlers

A Handler is exactly the same as a Task (it can do anything a Task can), but it will run when called by another Task. You can think of it as part of an Event system; A Handler will take an action when called by an event it listens for.

This is useful for "secondary" actions that might be required after running a Task, such as starting a new service after installation or reloading a service after a configuration change.

---
- hosts: local
  tasks:
   - name: Install Nginx
     apt: pkg=nginx state=installed update_cache=true
     notify:
      - Start Nginx

  handlers:
   - name: Start Nginx
     service: name=nginx state=started

# Variables

Before we look at the Tasks, let's look at variables. The vars directory contains a main.yml file which simply lists variables we'll use. This provides a convenient place for us to change configuration-wide settings.

Here's what the vars/main.yml file might look like:

---
domain: serversforhackers.com
ssl_key: /etc/ssl/sfh/sfh.key
ssl_crt: /etc/ssl/sfh/sfh.crt

These are three variables which we can use elsewhere in this Role. We saw them used in the template above, but we'll see them in our defined Tasks as well.     