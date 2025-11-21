# Claude Code Parallel Agent Execution Guide

## Overview
Use Claude Code's Task tool to spawn multiple parallel agents for simultaneous execution of refactoring tasks.

---

## 🚀 Quick Start: Parallel Execution with Claude Code

### **Session 1: Launch 3 Parallel Agents (Non-Destructive Tasks)**

In Claude Code, execute this in a single message:

```
Please spawn 3 parallel agents to execute these tasks simultaneously:

Agent 1: Read and execute phase-01-branding/task_001.txt (Database Backup)
Agent 2: Read and execute phase-01-branding/task_003.txt (Git Tag Creation)
Agent 3: Read and execute phase-01-branding/task_005.txt (Rollback Documentation)

Each agent should:
1. Read the task file from /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/
2. Follow all steps in the task
3. Check off acceptance criteria
4. Report completion status
5. Update task file status from 'pending' to 'done'

Execute all 3 agents in parallel using the Task tool.
```

**Result:** 3 tasks complete in ~1-2 hours (vs 2-3 hours sequential)

---

## 📋 **Recommended Parallel Execution Batches**

### **Batch 1: Pre-Implementation Safety (3 parallel agents)**

```markdown
Spawn 3 parallel agents:

**Agent A (DevOps):**
- Task: phase-01-branding/task_001.txt
- Goal: Create full database backup
- Model: haiku (fast for infrastructure tasks)

**Agent B (DevOps):**
- Task: phase-01-branding/task_003.txt
- Goal: Create git tag v1.0-pre-tarbiyyah
- Model: haiku

**Agent C (Documentation):**
- Task: phase-01-branding/task_005.txt
- Goal: Create ROLLBACK_PLAN.md
- Model: haiku

Execute in parallel and report when all complete.
```

---

### **Batch 2: Phase 1 Branding - Backend (2 parallel agents)**

```markdown
After Batch 1 completes, spawn 2 parallel agents:

**Agent A (Backend):**
- Task: phase-01-branding/task_007.txt
- Goal: Create context processor with MADRASAH_LABEL, STUDENT_LABEL
- Files: src/config/context_processors.py, src/config/settings/base.py
- Model: sonnet (needs code quality)

**Agent B (Media Backup):**
- Task: phase-01-branding/task_002.txt
- Goal: Backup media files while Agent A works on code
- Model: haiku

Execute in parallel.
```

---

### **Batch 3: Phase 1 Branding - Frontend (4 parallel agents)**

```markdown
After Batch 2 completes, spawn 4 parallel agents:

**Agent A (Static Assets):**
- Tasks: phase-01-branding/task_008.txt, phase-01-branding/task_009.txt
- Goal: Update PWA manifest, logos
- Files: src/static/manifest.json, src/static/images/
- Model: haiku

**Agent B (Navigation):**
- Task: phase-01-branding/task_010.txt
- Goal: Implement role-based navigation structure
- Files: src/templates/base.html, src/templates/navbars/*.html
- Model: sonnet

**Agent C (Content):**
- Task: phase-01-branding/task_012.txt, phase-01-branding/task_013.txt
- Goal: Update announcements and home page
- Files: src/templates/announcements/, src/templates/home.html
- Model: sonnet

**Agent D (Page Titles):**
- Task: phase-01-branding/task_014.txt
- Goal: Update page titles
- Files: Multiple template files
- Model: haiku

Execute all 4 in parallel.
```

---

### **Batch 4: Phase 2 Roles - Sequential Then Parallel**

```markdown
**Step 1 - Sequential (MUST complete first):**

Spawn 1 agent:
- Tasks: phase-02-roles/task_016.txt, phase-02-roles/task_017.txt, phase-02-roles/task_018.txt
- Goal: Add role choices, create migration, run migration
- Files: src/apps/users/models.py
- Model: sonnet
- Note: Database migration - cannot parallelize

Wait for completion before Step 2.

**Step 2 - Parallel (4 agents):**

After Step 1 complete, spawn 4 parallel agents:

**Agent A:** phase-02-roles/task_019.txt, phase-02-roles/task_020.txt (Permission mappings)
**Agent B:** phase-02-roles/task_021.txt, phase-02-roles/task_022.txt (Template updates)
**Agent C:** phase-02-roles/task_023.txt (Role-based tests)
**Agent D:** phase-02-roles/task_024.txt (User fixtures)

Execute in parallel.
```

---

### **Batch 5: Phase 3 Model Renaming - Branch-Based Parallelization**

```markdown
**Important:** Use git branches for conflict-free parallel execution

**Step 1 - Create branches:**
Spawn 1 agent to create branches:
- Create feature/madrasah-model
- Create feature/enrollment-model
- Create feature/activity-model

**Step 2 - Parallel model renaming (3 agents on separate branches):**

**Agent A (Branch: feature/madrasah-model):**
- Tasks: phase-03-madaris/task_026.txt through phase-03-madaris/task_036.txt
- Goal: Rename Chapter → Madrasah, add all fields
- Model: sonnet

**Agent B (Branch: feature/enrollment-model):**
- Tasks: phase-03-madaris/task_037.txt through phase-03-madaris/task_039.txt
- Goal: Rename ChapterMembership → MadrasahEnrollment
- Model: sonnet

**Agent C (Branch: feature/activity-model):**
- Tasks: phase-03-madaris/task_040.txt through phase-03-madaris/task_042.txt
- Goal: Rename ChapterActivity → MadrasahActivity
- Model: sonnet

**Step 3 - Merge branches:**
After all 3 agents complete, spawn 1 agent to:
- Merge feature/madrasah-model → main
- Merge feature/enrollment-model → main
- Merge feature/activity-model → main
- Resolve any conflicts

**Step 4 - Integration (1 agent):**
- Tasks: phase-03-madaris/task_043.txt, phase-03-madaris/task_044.txt, phase-03-madaris/task_045.txt
- Goal: Update URLs, views, admin
- Model: sonnet
```

---

### **Batch 6: Phase 4-9 Maximum Parallelization (6 agents!)**

```markdown
**MAXIMUM PARALLELIZATION** - 6 new apps built simultaneously

Spawn 6 parallel agents, each on separate git branch:

**Agent A (Branch: feature/teachers-app):**
- Tasks: phase-04-teachers/task_046.txt through phase-04-teachers/task_050.txt
- Goal: Create complete teachers app
- Model: sonnet

**Agent B (Branch: feature/curriculum-app):**
- Tasks: phase-05-curriculum/task_051.txt through phase-05-curriculum/task_060.txt (to be created)
- Goal: Create curriculum management app
- Model: sonnet

**Agent C (Branch: feature/student-model):**
- Tasks: phase-06-student/task_061.txt through phase-06-student/task_080.txt (to be created)
- Goal: Rename BMParliamentMember → Student
- Model: sonnet

**Agent D (Branch: feature/academic-records):**
- Tasks: phase-07-academic/task_081.txt through phase-07-academic/task_095.txt (to be created)
- Goal: Create academic records system
- Model: sonnet

**Agent E (Branch: feature/programs-update):**
- Tasks: phase-08-programs/task_096.txt through phase-08-programs/task_105.txt (to be created)
- Goal: Adapt programs for education
- Model: sonnet

**Agent F (Branch: feature/parent-portal):**
- Tasks: phase-09-parent/task_106.txt through phase-09-parent/task_115.txt (to be created)
- Goal: Create parent portal
- Model: sonnet

After all complete, merge all 6 branches to main.
```

---

## 📝 **Example Claude Code Prompt for Parallel Execution**

### **Batch 1 Example (Copy-Paste Ready):**

```
I need you to spawn 3 parallel agents using the Task tool to execute refactoring tasks simultaneously.

AGENT 1 - Database Backup:
- Read /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/phase-01-branding/task_001.txt
- Execute all steps in the task
- Create database backup: pg_dump madaris_dev > backup_$(date +%Y%m%d_%H%M%S).sql
- Compress: gzip backup_*.sql
- Verify backup can be restored
- Update task status to 'done'
- Report completion

AGENT 2 - Git Tag:
- Read /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/phase-01-branding/task_003.txt
- Execute all steps
- Create tag: git tag -a v1.0-pre-tarbiyyah -m "Pre-refactoring state"
- Push tag: git push origin v1.0-pre-tarbiyyah
- Update task status to 'done'
- Report completion

AGENT 3 - Rollback Documentation:
- Read /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/phase-01-branding/task_005.txt
- Create docs/ROLLBACK_PLAN.md
- Document database restore procedure
- Document git rollback procedure
- Update task status to 'done'
- Report completion

Spawn all 3 agents in a SINGLE message using multiple Task tool calls. Execute them in parallel, not sequentially.
```

---

## 🎯 **Agent Selection Strategy**

### **Use Haiku for:**
- Infrastructure tasks (backups, git operations)
- Static file updates (images, CSS)
- Simple documentation
- File copying/moving

### **Use Sonnet for:**
- Model changes and migrations
- Complex form creation
- View and URL pattern updates
- Code refactoring
- Test writing

### **Use Opus for:**
- Architecture decisions
- Complex debugging
- Multi-file refactoring with dependencies

---

## ⚡ **Pro Tips for Parallel Execution**

### **1. Check Agent Status**
After spawning agents, you can check their status:
```
Show me the status of all running agents and their progress
```

### **2. Resume Failed Agents**
If an agent fails, resume it:
```
Resume agent [agent-id] from where it failed
```

### **3. Coordinate Agents**
For tasks that need coordination:
```
Spawn 2 agents:
- Agent A: Wait for Agent B to complete task_007 before starting task_011
- Agent B: Execute task_007 immediately
```

### **4. Merge Coordination**
After parallel branches:
```
Spawn 1 agent to:
1. Merge all feature branches to main
2. Resolve conflicts prioritizing newest changes
3. Run tests after each merge
4. Report any merge conflicts for manual resolution
```

---

## 📊 **Expected Timeline with Parallel Agents**

### **Traditional Sequential:**
- Pre-Implementation: 6-8 hours
- Phase 1: 8-12 hours
- Phase 2: 10-15 hours
- Phase 3: 20-30 hours
- Phase 4-9: 70-100 hours
**TOTAL: ~126-183 hours (16-23 days)**

### **With Parallel Claude Code Agents:**
- Batch 1 (3 agents): 1-2 hours
- Batch 2 (2 agents): 1 hour
- Batch 3 (4 agents): 2-3 hours
- Batch 4 (1+4 agents): 4-5 hours
- Batch 5 (3+1 agents): 6-8 hours
- Batch 6 (6 agents): 8-10 hours
**TOTAL: ~24-32 hours (3-4 days)**

**TIME SAVED: 75-84%**

---

## 🚨 **Important Notes**

### **Git Branch Management:**
When using parallel agents on different branches:
1. Each agent creates its own feature branch
2. Agents work independently
3. Merge all branches at designated merge points
4. Resolve conflicts if any

### **Database Migrations:**
- Only ONE agent can run migrations at a time
- Sequence migration tasks (task_016-018)
- Other agents wait for migration to complete

### **File Locking:**
Claude Code agents automatically handle file conflicts:
- Agents working on different files: No conflict
- Agents working on same file: Last write wins (be careful!)
- Solution: Assign different files to different agents

---

## ✅ **Ready to Execute?**

Start with this command:

```
Spawn 3 parallel agents to execute phase-01-branding/task_001.txt, phase-01-branding/task_003.txt, and phase-01-branding/task_005.txt simultaneously.

Use the Task tool with subagent_type='general-purpose' for each agent.

Each agent should read its task file from /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/, execute all steps, and report completion.

Execute all agents in a single message using parallel Task tool calls.
```

🚀 **Let's begin!**
