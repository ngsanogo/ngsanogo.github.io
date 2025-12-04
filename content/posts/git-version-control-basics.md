---
authors:
  - Issa Sanogo
categories:
  - Application
date: "2025-12-01"
lastmod: "2025-12-01"
description: "Why data engineers need Git. Learn version control, why it matters, and how to use it daily."
tags:
  - git
  - version-control
  - collaboration
title: "Git: Version Control Every Data Engineer Needs"
draft: false
weight: 4
toc: true
---

## What is Git?

Git is version control. It saves every change you make to your code or data scripts.

Think of it like a backup system that remembers everything.

## The Problem It Solves

You're working on a data pipeline. You make changes:

- Day 1: Add new feature. Code still works.
- Day 2: Optimize performance. Code still works.
- Day 3: Fix a bug. Now something else breaks.

You want to go back to Day 2. Without Git, you're stuck.

With Git, you saved your work at each step. You go back to Day 2 in seconds.

## How Git Works

**Repository**: A folder containing your project and its history.

**Commit**: A snapshot of your code at a moment in time. Like a save point in a game.

**Branch**: A separate version of your project where you work independently.

**Merge**: Combine changes from one branch into another.

That's it. These concepts cover 90% of what you do.

## Real Example: You and a Colleague

You both work on the same data pipeline.

Without Git:

- You send files back and forth via email
- "Is this the latest version?"
- Somebody overwrites somebody's changes
- Nobody knows what changed
- Disaster

With Git:

- You both work on the same repository
- Git tracks who changed what
- If there's a conflict, Git helps resolve it
- Complete history of everything
- Easy to review before accepting changes

## Simple Git Workflow

```bash
# 1. Get the latest version
git pull

# 2. Make your changes to your code

# 3. See what you changed
git status
git diff

# 4. Save your changes with a message
git add .
git commit -m "Fix SQL query for monthly totals"

# 5. Send your changes to the team
git push
```

That's a normal day with Git.

## Why Data Engineers Need It

**Code is production**: Your SQL scripts, Python pipelines, configurations - they're as important as application code.

**Collaboration**: You work with other engineers. You need to coordinate changes.

**History**: Why did we change this query 3 months ago? Git shows you. Git shows the old version. Git shows who changed it.

**Rollback**: Something broke? Go back to the last working version instantly.

**Branching**: Test new ideas without affecting main code.

## Key Git Commands

```bash
# Initialize a repository
git init

# See history
git log

# See changes
git status
git diff

# Save changes
git add .
git commit -m "describe what you changed"

# Share your changes
git push

# Get others' changes
git pull

# Create a branch
git branch feature-name
git checkout feature-name

# Switch between branches
git checkout main
git checkout feature-name

# Merge a branch
git merge feature-name
```

That's it. You don't need more for daily work.

## Real Example: Data Pipeline

You're building a monthly revenue report.

```bash
# Start fresh
git pull

# Create your own branch (so you don't break the main code)
git checkout -b revenue-report

# Write your SQL pipeline
# Make sure it works locally
# Commit your work
git add revenue_pipeline.sql
git commit -m "Add monthly revenue aggregation query"

# Send it to the team
git push

# Colleague reviews it and says "looks good"
# Merge it into main
git checkout main
git pull
git merge revenue-report

# Now everyone has your code
```

Everybody on the team can use the report. If there's a problem later, Git shows exactly what changed.

## Why Git Prevents Disasters

**Scenario 1: You break something**

```bash
# Oh no, my changes broke the pipeline
git revert abc123
# Back to the previous working version
```

**Scenario 2: You need old code**

```bash
# Show me the version from last month
git checkout abc123 -- file.sql
```

**Scenario 3: You need to see who changed something**

```bash
# Show all changes to this file
git log file.sql

# Show exactly what changed
git blame file.sql
```

**Scenario 4: Multiple people edited the same file**

```bash
# Git merges the changes intelligently
# If there's a conflict, you resolve it
# Then commit the merge
```

## GitHub and GitLab

Git is the tool. GitHub and GitLab are hosting services.

They let you:

- Store your code online
- Share with your team
- Review changes before accepting them
- Track issues and tasks

Most companies use GitHub or GitLab.

## Getting Started

```bash
# Create a folder for your project
mkdir my-data-project
cd my-data-project

# Initialize Git
git init

# Create your first file
echo "SELECT * FROM customers;" > query.sql

# Save it
git add query.sql
git commit -m "Initial commit: basic customer query"

# You've created your first Git repository
```

Now you can:

- Make changes
- Commit them
- See history
- Go back if needed

## Why This Matters

Git is not optional for data engineers.

- Your company needs to know what changed
- Your team needs to collaborate safely
- You need to be able to recover from mistakes
- You need version control of your scripts

Without Git, you're working blindly. Dangerous.

## Bottom Line

Learn Git now. Use it daily. It becomes automatic.

Git is as important as knowing SQL for a data engineer.

Spend 2-3 hours learning it properly. Practice daily. Worth it.
