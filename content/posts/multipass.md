---
authors:
  - Issa Sanogo
categories:
  - Infrastructure
date: "2025-03-21"
lastmod: "2025-12-04"
description: What is Multipass? Learn how to quickly create and manage lightweight Linux virtual machines on Windows, Mac, and Linux for development and testing.
series:
  - VM
tags:
  - multipass
  - virtualization
  - ubuntu
  - vm
title: "Multipass: Quick Virtual Machines for Developers"
draft: false
weight: 1
toc: true
---

## What is Multipass?

Multipass is a simple tool that lets you create lightweight Linux virtual machines with one command.

Instead of installing heavy virtual machine software, Multipass gives you:

- Quick VM creation (seconds, not minutes)
- Minimal resource usage
- Easy to delete when you're done
- Same interface on Windows, Mac, and Linux

## Why Use It

You might need a VM to:

- Test your code in a clean Linux environment
- Install software without cluttering your main system
- Try something risky safely
- Develop on Linux when your main machine is Windows or Mac
- Set up services (databases, web servers) for testing

## How It Works

Instead of:

1. Download VM software (VirtualBox, VMware) - 30 minutes
2. Download Ubuntu ISO - 5 minutes
3. Create new VM - 10 minutes
4. Install OS - 15 minutes
5. Configure network - 5 minutes
6. Finally start working - much later

With Multipass:

```bash
multipass launch
```

Done. You have a running Ubuntu VM. Immediately.

## Common Use Cases

**Test a deployment script**

Create a clean VM, run your script, verify it works, delete the VM.

**Try new software safely**

Install Kubernetes, Docker, whatever in the VM. Doesn't affect your machine.

**Develop in Linux on a Mac/Windows laptop**

Your app runs on Linux in production? Test it in a Linux VM on your Mac.

**Quick learning environment**

Want to learn Linux admin? Spin up a VM and experiment without risk.

## Basic Commands

```bash
# Create and start a VM
multipass launch --name my-vm

# List your VMs
multipass list

# Access the VM
multipass shell my-vm

# Run a command in the VM
multipass exec my-vm -- apt update

# Stop it
multipass stop my-vm

# Delete it
multipass delete my-vm
```

## Real Example: Test a Script

You wrote a deployment script that should work on Linux.

```bash
# Create a clean VM
multipass launch -n test

# Copy your script into the VM
multipass transfer my-deploy-script.sh test:/home/ubuntu/

# Run it
multipass exec test -- bash /home/ubuntu/my-deploy-script.sh

# Check if it worked - no problem
# Delete the VM
multipass delete test
```

Your actual system? Untouched.

## Why Data Engineers Like It

- Set up PostgreSQL or MySQL in seconds for testing
- Test data pipelines in clean Linux environments
- Try different tool versions without conflicts
- Quick CI/CD testing locally before pushing

## Multipass vs Docker

**Multipass**: Full Linux machine. Use when you need everything.

**Docker**: Single application container. Use when you want isolation and portability.

They're different tools for different jobs.

## When Not to Use It

- If you need Windows on Windows (Multipass is Linux only)
- For production deployment (that's what servers are for)
- If you need a persistent VM (it's meant for temporary environments)

## Getting Started

Multipass is free and works on Windows, Mac, and Linux. Download from <https://multipass.run/>

Once installed, one command gives you a working Linux machine.

That's powerful for testing and learning.
