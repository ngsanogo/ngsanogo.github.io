---
authors:
  - Issa Sanogo
categories:
  - Infrastructure
date: "2025-11-24"
lastmod: "2025-11-24"
description: "Linux fundamentals for data engineers: How it works, why it matters, and essential concepts explained."
tags:
  - linux
  - operating-system
  - unix
  - command-line
  - infrastructure
title: "Linux Fundamentals: How It Works and Why Data Engineers Use It"
draft: false
weight: 12
toc: true
---

## What is Linux?

Linux is an operating system kernel. Free and open-source.

The operating system is the bridge between you and the computer hardware.

Linux powers:

- 99% of data centers
- Most servers in the world
- Cloud infrastructure
- Data engineering pipelines

If you work with data professionally, Linux is everywhere.

## Unix Philosophy

Linux is based on Unix. Unix has a philosophy:

**Do one thing well**:

```bash
ls      # List files
grep    # Search text
cat     # Show content
```

Each tool does one job. Combine them:

```bash
cat data.csv | grep "2025" | wc -l
# Show file, search for 2025, count matches
```

Simple. Powerful. Composable.

## Linux vs Windows vs macOS

**Linux**:

- Free
- Open-source
- Powerful command line
- Industry standard for servers
- No GUI by default
- Steep learning curve (initially)

**Windows**:

- Familiar to most people
- Good GUI
- Expensive
- Closed source
- Weak command line historically
- Not standard for servers

**macOS**:

- Built on Unix (similar to Linux)
- Good for development
- Expensive hardware
- Closed source
- Easier command line than Windows
- But not standard for servers

Professional servers run Linux. That's a fact.

## The Linux Filesystem

Linux organizes files in a tree:

```
/
├── bin/        # Essential commands
├── home/       # User home directories
│   ├── alice/
│   ├── bob/
│   └── issa/
├── etc/        # Configuration files
├── var/        # Variable data (logs, databases)
├── tmp/        # Temporary files
├── usr/        # User programs
├── opt/        # Optional software
└── root/       # Root user's home
```

**Key paths**:

```bash
/home/issa       # My home directory (~)
/home/issa/.ssh  # SSH keys
/home/issa/.bashrc # Shell configuration
/etc/postgresql  # PostgreSQL config
/var/log         # System logs
/tmp             # Temporary files
```

## Users and Permissions

**Root**: Administrator. Can do anything. Dangerous.

**Regular user**: Limited permissions. Safe.

**Groups**: Users belong to groups with shared permissions.

```bash
# I am user 'issa' in groups 'issa' and 'docker'
id
# uid=1000(issa) gid=1000(issa) groups=1000(issa),999(docker)
```

**Permission format**:

```bash
ls -la myfile.txt
-rw-r--r-- 1 issa issa 1024 Dec 4 10:00 myfile.txt
```

Breaking it down:

- `-` = file
- `rw-` = owner (me) can read and write
- `r--` = group can read
- `r--` = others can read

**Change permissions**:

```bash
# Owner only
chmod 600 secret.txt

# Owner read+write+execute, others read+execute
chmod 755 script.sh

# Make executable
chmod +x script.sh
```

## The Shell (Command Line)

The shell is how you talk to Linux.

**Bash**: The most common shell.

**Prompts**:

```bash
# Regular user
issa@ubuntu:~$

# Root user
root@ubuntu:~#
```

**Commands**:

```bash
# Syntax
command [options] [arguments]

# Examples
ls -la /home/issa
grep "error" logfile.txt
python3 script.py --verbose
```

**Pipes** (connect commands):

```bash
cat data.csv | grep "2025" | sort | uniq
# Show file, filter, sort, remove duplicates
```

**Redirection** (redirect output):

```bash
# Save to file
python script.py > output.txt

# Append to file
echo "log" >> log.txt

# Redirect error
python script.py 2> errors.txt

# Both output and error
python script.py > output.txt 2>&1
```

## File Operations

**Navigate**:

```bash
pwd                    # Where am I?
cd /home/issa          # Go to directory
cd ..                  # Go up
cd ~                   # Go home
ls -la                 # List with details
```

**Create and view**:

```bash
touch file.txt         # Create empty file
cat file.txt           # View content
head -20 file.txt      # First 20 lines
tail -20 file.txt      # Last 20 lines
wc -l file.txt         # Line count
```

**Edit**:

```bash
nano file.txt          # Simple editor
vim file.txt           # Powerful editor
sed -i 's/old/new/g' file.txt  # Find and replace
```

**Copy, move, delete**:

```bash
cp file.txt copy.txt       # Copy
cp -r folder/ copy_folder/ # Copy folder
mv file.txt newname.txt    # Move/rename
rm file.txt                # Delete
rm -r folder/              # Delete folder (careful!)
```

## Permissions in Detail

**rwx** = read, write, execute

```bash
# 755 in binary: 111 101 101
# Owner: 111 = 7 = read+write+execute
# Group: 101 = 5 = read+execute
# Other: 101 = 5 = read+execute
chmod 755 script.sh

# 644 in binary: 110 100 100
# Owner: 110 = 6 = read+write
# Group: 100 = 4 = read
# Other: 100 = 4 = read
chmod 644 file.txt

# 600 in binary: 110 000 000
# Owner: 110 = 6 = read+write
# Group: 000 = 0 = no access
# Other: 000 = 0 = no access
chmod 600 secret.txt
```

## Environment and Variables

The environment stores configuration.

```bash
# View all variables
env

# View specific variable
echo $HOME
echo $PATH

# Set variable (this session only)
export API_KEY=secret123

# Use variable
curl -H "Authorization: $API_KEY" api.example.com

# Make permanent (add to ~/.bashrc)
nano ~/.bashrc
# Add: export API_KEY=secret123
source ~/.bashrc
```

## Package Management

Different distributions use different package managers:

**Ubuntu/Debian** (apt):

```bash
sudo apt update              # Update package list
sudo apt install python3     # Install
sudo apt remove python3      # Remove
sudo apt upgrade             # Upgrade all
sudo apt search python       # Search
```

**RedHat/CentOS** (yum):

```bash
sudo yum install python3
sudo yum remove python3
sudo yum update
```

Same concepts. Different syntax.

## System Administration

**Check disk space**:

```bash
df -h              # Disk free
du -sh /home/issa/ # Folder size
```

**View logs**:

```bash
tail -f /var/log/syslog    # System log
tail -f /var/log/auth.log  # Auth log
journalctl -xe             # Journal
```

**Monitor processes**:

```bash
ps aux                     # All processes
ps aux | grep python       # Find process
top                        # Monitor live
kill 1234                  # Kill process
```

**Manage services**:

```bash
sudo systemctl start postgresql    # Start
sudo systemctl stop postgresql     # Stop
sudo systemctl restart postgresql  # Restart
sudo systemctl status postgresql   # Status
sudo systemctl enable postgresql   # Start on boot
```

## Networking

**Check connectivity**:

```bash
ping google.com             # Test connection
curl https://api.example.com  # Make HTTP request
wget https://example.com/file.zip  # Download
```

**Network info**:

```bash
ip addr                    # IP address
ip route                   # Routing
netstat -an                # Connections
nslookup example.com       # DNS lookup
```

**Secure shell (SSH)**:

```bash
ssh user@example.com          # Connect
ssh -i key.pem user@server    # With private key
scp file.txt user@server:~/   # Copy file
```

## Text Processing

**Search**:

```bash
grep "pattern" file.txt         # Find pattern
grep -i "pattern" file.txt      # Case insensitive
grep -r "pattern" /folder/      # Recursive
grep -E "regex.*pattern" file   # Regex
```

**Process text**:

```bash
cat file.txt          # Show
head -10 file.txt     # First 10 lines
tail -10 file.txt     # Last 10 lines
wc -l file.txt        # Count lines
sort file.txt         # Sort
uniq file.txt         # Unique lines
cut -d, -f1 file.csv  # Extract column 1
```

**Find and replace**:

```bash
sed 's/old/new/' file.txt       # Replace first
sed 's/old/new/g' file.txt      # Replace all
sed -i 's/old/new/g' file.txt   # In-place edit
```

## Scripting

Write reusable scripts:

```bash
#!/bin/bash
# Comment

# Variables
NAME="issa"
AGE=30

# Echo output
echo "Hello $NAME"

# Conditionals
if [ "$AGE" -gt 18 ]; then
    echo "Adult"
else
    echo "Minor"
fi

# Loops
for i in 1 2 3; do
    echo "Number $i"
done

# Functions
backup() {
    echo "Backing up..."
    cp -r /data /backup/data_$(date +%Y%m%d)
}

backup
```

Make executable and run:

```bash
chmod +x script.sh
./script.sh
```

## Cron Jobs (Scheduling)

Run scripts automatically on schedule:

```bash
# Edit cron
crontab -e

# Add jobs:
0 2 * * * /home/issa/backup.sh          # Daily at 2 AM
0 */6 * * * /home/issa/clean.sh         # Every 6 hours
0 0 * * 0 /home/issa/weekly_report.sh  # Weekly Sunday midnight
```

Format:

```
minute hour day month weekday command
0      2    *   *     *       /script.sh
```

## Data Engineer Workflow on Linux

**Extract data**:

```bash
psql -U user -d database -c "SELECT * FROM orders;" > data.csv
```

**Transform data** (using tools):

```bash
cat data.csv | cut -d, -f1,2 | grep "2025" > filtered.csv
```

**Transform data** (using Python):

```bash
python3 transform.py < raw.csv > processed.csv
```

**Load data**:

```bash
psql -U user -d database -c "\COPY processed FROM 'data.csv' WITH CSV"
```

**Schedule pipeline**:

```bash
# Add to crontab
0 2 * * * /home/issa/data_pipeline.sh
```

All coordinated through Linux.

## Linux File Ownership

```bash
# View owner
ls -la myfile.txt
# -rw-r--r-- 1 issa issa 1024 Dec 4 10:00 myfile.txt
#              owner group

# Change owner
sudo chown alice:alice myfile.txt

# Change group
sudo chgrp developers myfile.txt

# Both
sudo chown alice:developers myfile.txt
```

## The Power of Linux

**Composability**: Combine simple tools.

```bash
find . -name "*.log" | xargs wc -l | sort -rn | head -5
# Find log files, count lines, sort by size, show top 5
```

**Automation**: Scripts run unattended.

```bash
# Backup runs at 2 AM every day automatically
0 2 * * * /backup.sh
```

**Remote work**: SSH into servers from anywhere.

```bash
ssh user@data.company.com
# You're on the server. Run commands. Work remotely.
```

**Scripting**: Automate everything.

```bash
# One script extracts, transforms, loads, monitors
# Runs daily automatically
```

## Linux Learning Path

**Week 1**: Navigation and basic commands

```bash
cd, ls, cat, nano, cp, mv, rm
```

**Week 2**: Permissions and users

```bash
chmod, chown, sudo, useradd
```

**Week 3**: Pipes and redirection

```bash
|, >, >>, 2>, grep, sed
```

**Week 4**: Scripting and automation

```bash
Bash scripts, cron jobs
```

**Week 5+**: System administration

```bash
Services, logs, networking
```

## Bottom Line

Linux is the foundation of data infrastructure.

Understanding Linux means:

- You can work on servers
- You can automate tasks
- You understand how systems work
- You're more valuable

Master the fundamentals. The rest builds on that.

Start with Ubuntu. Learn the command line. You'll become a better engineer.

Linux is not optional for data engineers. It's essential.
