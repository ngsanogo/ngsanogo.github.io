---
authors:
  - Issa Sanogo
categories:
  - Infrastructure
date: "2025-12-05"
lastmod: "2025-12-05"
description: "Ubuntu for data engineers: Why it's the best Linux distribution, how to use it, and getting started."
tags:
  - ubuntu
  - linux
  - operating-system
  - infrastructure
title: "Ubuntu: The Linux Distribution Data Engineers Choose"
draft: false
weight: 11
toc: true
---

## What is Ubuntu?

Ubuntu is a Linux distribution. Free, open-source, reliable operating system.

It's what data engineers use on their servers and often locally.

Simple: Ubuntu is Linux made easy.

## Why Ubuntu Matters for Data Engineers

**Server standard**: Most production data infrastructure runs on Ubuntu.

**Free**: Zero cost. Download and use forever.

**Reliable**: Rock-solid stability. Proven in production for 20+ years.

**Community**: Massive community. Help and documentation everywhere.

**Container-friendly**: Docker runs best on Linux. Ubuntu is perfect.

**Easy**: Easier than other Linux distributions. Good for beginners.

## Ubuntu vs Other Operating Systems

**Windows**:

- Familiar to most people
- Not standard for servers
- Harder to run data tools

**macOS**:

- Good for development
- Common in tech companies
- Expensive hardware

**Ubuntu/Linux**:

- Standard for servers and data infrastructure
- Free
- Powerful command line
- Professional

Professional data engineers use Linux. Ubuntu is the easiest entry point.

## Installing Ubuntu

**Option 1: Virtual Machine** (Easiest for Windows/Mac users)

```bash
# Download VirtualBox (free)
# Download Ubuntu ISO (free)
# Create VM
# Boot from ISO
# Follow installation wizard
# Done
```

**Option 2: Windows Subsystem for Linux (WSL)**

```powershell
# On Windows 11 (PowerShell as admin)
wsl --install -d Ubuntu

# Ubuntu runs inside Windows
# Same power as full Ubuntu
```

**Option 3: Dual Boot**

- Wipe half your disk
- Install Ubuntu
- Choose at startup which OS to boot

**Option 4: Dedicate a server**

- Buy a server
- Install Ubuntu on it
- Run 24/7

For learning: WSL or Virtual Machine. Easiest.

## First Steps in Ubuntu

**Open terminal**:

```bash
Ctrl + Alt + T
```

Terminal appears. You're in the shell.

**Know where you are**:

```bash
pwd
# /home/issa
```

**See what's here**:

```bash
ls
# Desktop Documents Downloads Music Pictures Public Templates Videos
```

**Create a folder**:

```bash
mkdir my_project
cd my_project
pwd
# /home/issa/my_project
```

That's navigation. Foundation of Linux.

## Essential Ubuntu Commands

**File operations**:

```bash
# List files
ls
ls -la  # Detailed list
ls -la *.txt  # Only .txt files

# Create file
touch myfile.txt

# View file
cat myfile.txt

# Edit file
nano myfile.txt  # Simple editor
vim myfile.txt   # Powerful editor

# Copy
cp file.txt file_copy.txt

# Move/rename
mv file.txt newname.txt

# Delete
rm file.txt

# Delete folder (careful!)
rm -r folder_name
```

**Directory operations**:

```bash
# Make directory
mkdir folder

# Go to directory
cd folder

# Go back
cd ..

# Go home
cd ~

# Go to absolute path
cd /home/issa/projects
```

**Text processing**:

```bash
# View file
cat file.txt

# First 10 lines
head file.txt

# Last 10 lines
tail file.txt

# Search
grep "pattern" file.txt

# Count lines
wc -l file.txt

# Sort
sort file.txt

# Unique lines
uniq file.txt
```

**Permissions**:

```bash
# View permissions
ls -la

# Change permissions (read, write, execute)
chmod 755 script.sh

# Make executable
chmod +x script.sh
```

**System info**:

```bash
# Who am I?
whoami

# Disk space
df -h

# Memory usage
free -h

# Running processes
ps aux

# Kill process
kill 1234
```

## Package Management (Installing Software)

Ubuntu uses `apt` to install software.

**Update package list**:

```bash
sudo apt update
```

**Install software**:

```bash
sudo apt install python3
sudo apt install postgresql
sudo apt install git
```

**Remove software**:

```bash
sudo apt remove python3
```

**Search for software**:

```bash
apt search postgresql
```

**Check version**:

```bash
python3 --version
postgresql --version
git --version
```

**Install from source** (when apt doesn't have it):

```bash
wget https://example.com/software.tar.gz
tar -xzf software.tar.gz
cd software
./configure
make
sudo make install
```

## Users and Permissions

**Current user**:

```bash
whoami
# issa
```

**Become admin (sudo)**:

```bash
sudo apt install python3
# Prompts for password
```

**Create new user**:

```bash
sudo useradd john
sudo passwd john  # Set password
```

**Change to another user**:

```bash
su john
```

**Edit sudo permissions** (advanced):

```bash
sudo visudo
# Very careful here. Can break system
```

## Scripting in Ubuntu

Write scripts to automate tasks.

**Create script**:

```bash
nano backup.sh
```

**Write script**:

```bash
#!/bin/bash
# Backup script

echo "Starting backup..."
cp -r /home/issa/data /backup/data_$(date +%Y%m%d)
echo "Backup complete"
```

**Make executable**:

```bash
chmod +x backup.sh
```

**Run it**:

```bash
./backup.sh
# Starting backup...
# Backup complete
```

**Schedule it** (run daily at 2 AM):

```bash
crontab -e

# Add this line:
0 2 * * * /home/issa/backup.sh

# Save and exit
```

Boom. Automated daily backups.

## Real Ubuntu Data Engineering Setup

```bash
# Update system
sudo apt update
sudo apt upgrade

# Install Python
sudo apt install python3 python3-pip

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Git
sudo apt install git

# Install Docker
sudo apt install docker.io

# Start services
sudo systemctl start postgresql
sudo systemctl start docker

# Create project
mkdir my_data_project
cd my_data_project

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install libraries
pip install pandas sqlalchemy requests

# Write pipeline
nano pipeline.py

# Run it
python pipeline.py
```

That's a professional data engineering setup. Free. Powerful.

## System Services

Start and stop services:

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Stop PostgreSQL
sudo systemctl stop postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check if running
sudo systemctl status postgresql

# Start on boot
sudo systemctl enable postgresql

# Disable on boot
sudo systemctl disable postgresql

# See all services
systemctl list-units --type=service
```

## File Permissions Explained

```bash
ls -la
# -rw-r--r-- 1 issa issa 1024 Dec 4 10:00 file.txt
```

Breaking it down:

- `-` = file (d = directory)
- `rw-` = owner can read and write
- `r--` = group can read
- `r--` = others can read
- `issa` = owner
- `issa` = group

```bash
# 755 = rwxr-xr-x (owner full, others read+execute)
chmod 755 script.sh

# 644 = rw-r--r-- (owner read+write, others read)
chmod 644 file.txt

# 600 = rw------- (owner only, secret files)
chmod 600 .ssh/id_rsa
```

## Networking

```bash
# Check IP address
ip addr

# Test connection
ping google.com

# DNS lookup
nslookup example.com

# View network connections
netstat -an

# Copy over network (SSH)
scp file.txt user@server:/remote/path

# Connect to server
ssh user@server
```

## File Transfer

Copy files between computers:

```bash
# Copy from local to server
scp myfile.txt user@192.168.1.100:/home/user/

# Copy from server to local
scp user@192.168.1.100:/home/user/file.txt ./

# Copy folder
scp -r folder/ user@server:/remote/path
```

## Environment Variables

Store configuration:

```bash
# View environment variables
env

# Set variable for this session
export API_KEY=secret123

# View one variable
echo $API_KEY

# Make permanent (add to ~/.bashrc)
nano ~/.bashrc

# Add this line:
export API_KEY=secret123

# Reload
source ~/.bashrc
```

## Processes and Monitoring

```bash
# See running processes
ps aux

# Find specific process
ps aux | grep python

# Monitor in real-time
top
# Press 'q' to exit

# Memory usage
free -h

# Disk usage
du -sh /home/issa/

# CPU usage
vmstat 1
```

## Ubuntu Desktop vs Server

**Desktop (GUI)**:

- Visual interface
- File manager
- Easy for learning
- Uses more resources

**Server (command line)**:

- No GUI
- Terminal only
- Lighter weight
- Standard for production

As data engineer: Learn both. Desktop for learning. Server for production.

## Real Data Engineering Workflow on Ubuntu

**Day 1: Setup**

```bash
# Install tools
sudo apt install python3 git postgresql docker.io

# Clone project
git clone https://github.com/company/data-pipeline.git
cd data-pipeline

# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test locally
python pipeline.py
```

**Day 2: Development**

```bash
# Make changes
nano pipeline.py

# Test
python pipeline.py

# Version control
git add pipeline.py
git commit -m "Fix SQL query"
git push
```

**Day 3: Deployment**

```bash
# Build Docker image
docker build -t pipeline:v2 .

# Test in Docker
docker run pipeline:v2

# Push to server
docker push registry.company.com/pipeline:v2

# Server pulls and runs it
ssh user@server
docker pull registry.company.com/pipeline:v2
docker run pipeline:v2
```

That's real Ubuntu data engineering.

## Ubuntu Tips and Tricks

**Search for files**:

```bash
find / -name "*.py" 2>/dev/null
```

**Find and replace in files**:

```bash
sed -i 's/old/new/g' file.txt
```

**Redirect output**:

```bash
python script.py > output.txt 2>&1
```

**Pipe commands**:

```bash
cat data.csv | grep "2025" | wc -l
```

**Run in background**:

```bash
python pipeline.py &
```

**Check recent commands**:

```bash
history
```

**Run last command**:

```bash
!!
```

## Ubuntu Community

**Ask for help**:

- Ask Ubuntu (askubuntu.com)
- Ubuntu Forums
- Stack Overflow
- Reddit (/r/Ubuntu, /r/linux)

Massive community. Someone's already solved your problem.

## Bottom Line

Ubuntu is the Linux distribution for data engineers.

Free. Powerful. Professional. Reliable.

Learn Ubuntu. Learn the command line. Learn basic system administration.

You'll be more effective. More professional. More valuable.

Most production data infrastructure runs on Linux. Ubuntu is your entry point.

Start today. Download. Install. Learn.
