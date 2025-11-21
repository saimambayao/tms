# Task Format Conversion to taskmaster-ai MCP

## Overview

This directory contains **130 task files** for the Tarbiyyah Management System refactoring project. All task files are currently in a **custom markdown format** and need to be converted to the **taskmaster-ai MCP specification**.

**Status**: Analysis & planning complete ✓
**Next Step**: Execute conversion using provided guides and tools

---

## What is taskmaster-ai?

taskmaster-ai is a Model Control Protocol (MCP) server that integrates AI task management into development workflows. It provides:

- Structured task format for better AI agent collaboration
- Dependency tracking and management
- Priority-based task sequencing
- MCP integration with VS Code, Cursor, Windsurf, and other editors

**Why Migrate?**: Using taskmaster-ai format enables:
- Better integration with Claude Code and AI agents
- Automated task dependency resolution
- Improved task tracking and progress visibility
- Standard format compatibility across tools

---

## Documentation Structure

### For Quick Understanding (Start Here)
1. **QUICK_REFERENCE.md** (This guide at a glance)
   - Format comparison
   - Priority assignment guide
   - Conversion workflow options
   - Commands and validation

### For Detailed Information
2. **TASKMASTER_REFACTOR_GUIDE.md** (Comprehensive spec)
   - Full format comparison table
   - Detailed migration steps
   - Critical considerations
   - Success criteria

3. **SAMPLE_CONVERSIONS.md** (Real examples)
   - 3 complete before/after examples
   - Simple task (no dependencies)
   - Complex task (multiple dependencies)
   - Conversion checklist

4. **CONVERSION_ACTION_PLAN.md** (Step-by-step guide)
   - Three conversion approaches (A, B, C)
   - Detailed execution steps
   - Timeline and validation
   - Rollback plan

### Tools
5. **convert_to_taskmaster.py** (Automation script)
   - Python script for batch/single file conversion
   - Auto-detects priority based on keywords
   - Generates Test Strategy sections
   - Supports batch and individual conversion

---

## Quick Decision Matrix

### Which documentation should I read?

| Need | Read |
|------|------|
| Quick overview | QUICK_REFERENCE.md |
| Before/after examples | SAMPLE_CONVERSIONS.md |
| Full specification | TASKMASTER_REFACTOR_GUIDE.md |
| Step-by-step instructions | CONVERSION_ACTION_PLAN.md |
| Tool help | convert_to_taskmaster.py --help |

### Which conversion approach should I use?

| Approach | Time | Effort | Best For |
|----------|------|--------|----------|
| **A: Fully Automated** | 5-6 hrs | Low | If you trust automation |
| **B: Fully Manual** | 20-25 hrs | High | If you want complete control |
| **C: Hybrid** (Recommended) | 10-12 hrs | Medium | Balance of speed & safety |

---

## Current Task Statistics

```
📊 Task Distribution:

phase-01-branding       → 14 tasks (Branding & Configuration)
phase-02-roles          → 10 tasks (User Roles)
phase-03-madaris        → 20 tasks (Madaris Management)
phase-04-teachers       → 5 tasks (Teachers/Asatidz)
phase-05-curriculum     → 10 tasks (Curriculum)
phase-06-student        → 12 tasks (Student Model)
phase-07-academic       → 10 tasks (Academic Records)
phase-08-programs       → 10 tasks (Programs)
phase-09-parent         → 10 tasks (Parent/Guardian)
phase-10-adapt          → 8 tasks (Adaptations)
phase-11-forms          → 6 tasks (Forms)
phase-12-templates      → 5 tasks (Templates)
phase-13-database       → 8 tasks (Database)
phase-14-frontend       → 2 tasks (Frontend)

TOTAL: 130 task files (130 × convert_to_taskmaster.py)
```

---

## Format Comparison At a Glance

### Current Format
```markdown
# Task 001: Create Full Database Backup
## Phase: Pre-Implementation
## Status: pending
## Dependencies:
- task_015.txt
## Description: ...
## Acceptance Criteria:
- [ ] Criteria
## Steps:
1. Step
## Files Affected:
- file.txt
## Notes: ...
```

### New Format
```markdown
# Task ID: 001
# Title: Create Full Database Backup
# Status: pending
# Priority: high
# Dependencies: 015
# Description: One-sentence summary

# Details:
[Consolidated steps, criteria, files, notes]

# Test Strategy:
[Verification approach]
```

**Main Changes**:
- Separate Task ID from Title
- Add Priority field
- Consolidate implementation sections
- Add Test Strategy section
- Remove Phase field (archive elsewhere if needed)

---

## Getting Started

### Step 1: Choose Your Approach
Read **QUICK_REFERENCE.md** to decide: Automated (A), Manual (B), or Hybrid (C)

### Step 2: Review Examples
Check **SAMPLE_CONVERSIONS.md** to see what converted files look like

### Step 3: Execute Conversion
Follow **CONVERSION_ACTION_PLAN.md** for step-by-step instructions

### Step 4: Validate Results
Run provided validation commands to ensure all 51 files are properly converted

---

## Three Conversion Approaches

### 🚀 Approach A: Fully Automated (Fastest)
**Time**: 2-3 hours | **Effort**: Low | **Risk**: Medium

```bash
python convert_to_taskmaster.py --batch \
  --input-dir phase-01-branding \
  --output-dir phase-01-branding-converted
```

Best for: Tight timeline, trust in automation

---

### 👨‍💻 Approach B: Fully Manual (Thorough)
**Time**: 8-12 hours | **Effort**: High | **Risk**: Low

Edit each of 51 files manually using new format specification

Best for: Quality assurance, detailed review

---

### 🎯 Approach C: Hybrid (RECOMMENDED)
**Time**: 4-5 hours | **Effort**: Medium | **Risk**: Low

1. Run automated conversion
2. Review sample files
3. Apply to production if verified
4. Spot-check results

Best for: Balance of speed, effort, and safety

---

## Key Files by Purpose

| File | Purpose | When to Use |
|------|---------|------------|
| QUICK_REFERENCE.md | At-a-glance guide | Quick lookup |
| TASKMASTER_REFACTOR_GUIDE.md | Complete spec | Full understanding |
| SAMPLE_CONVERSIONS.md | Real examples | Learn by example |
| CONVERSION_ACTION_PLAN.md | Execution steps | Ready to implement |
| convert_to_taskmaster.py | Automation | Run conversion |

---

## Validation Checklist

After converting all 130 tasks, verify:

- [ ] All files follow new format (Task ID, Title, Status, etc.)
- [ ] No information lost from original files
- [ ] Dependencies converted to comma-separated format
- [ ] Priority field added to every task
- [ ] Test Strategy section present in all tasks
- [ ] No duplicate or missing files
- [ ] Changes committed to git branch

```bash
# Quick validation
find phase-*/ -name "task_*.txt" | wc -l  # Should show 130

# Check all have required headers
grep -l "^# Task ID:" phase-*/task_*.txt | wc -l  # Should show 130
grep -l "^# Test Strategy:" phase-*/task_*.txt | wc -l  # Should show 130
```

---

## Next Steps

### Option 1: Quick Start (5 min)
```bash
cd /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor
cat QUICK_REFERENCE.md
```

### Option 2: Learn by Example (10 min)
```bash
cat SAMPLE_CONVERSIONS.md  # See 3 detailed examples
```

### Option 3: Full Guide (20 min)
```bash
cat TASKMASTER_REFACTOR_GUIDE.md  # Complete specification
```

### Option 4: Execute Now (Read plan first, then follow)
```bash
cat CONVERSION_ACTION_PLAN.md  # Step-by-step instructions
# Then run: python convert_to_taskmaster.py --batch ...
```

---

## Important Decisions to Make

Before starting, clarify:

1. **Conversion Method**: A, B, or C (recommended: C)
2. **Phase Field**: Remove, archive, or keep in Details?
3. **Timeline**: Start immediately or schedule for later?
4. **Review**: Who approves before merging?
5. **Tools Affected**: Any tools parsing old format?

---

## Timeline Estimate (Hybrid Approach)

| Phase | Time |
|-------|------|
| Preparation | 10 min |
| Test Phase 1 | 30 min |
| Review | 45 min |
| Apply Phase 1 | 10 min |
| Phases 2-14 | 240 min |
| Validation | 30 min |
| Commit | 15 min |
| **Total** | **~9-10 hours** |

---

## Support & Help

### If you need to understand the format:
→ Read **TASKMASTER_REFACTOR_GUIDE.md**

### If you need to see examples:
→ Check **SAMPLE_CONVERSIONS.md**

### If you need to execute the conversion:
→ Follow **CONVERSION_ACTION_PLAN.md**

### If you need quick info:
→ Use **QUICK_REFERENCE.md**

### If you want to automate:
→ Run **convert_to_taskmaster.py**

---

## Common Questions

**Q: Will I lose any information during conversion?**
A: No. The new format consolidates sections but preserves all information.

**Q: Can I automate the conversion?**
A: Yes! Use `convert_to_taskmaster.py` for full or partial batch conversion.

**Q: What if the automated conversion has errors?**
A: Catch them during spot-check phase (Step 3 of hybrid approach).

**Q: Can I rollback if something goes wrong?**
A: Yes. Use git to rollback. See CONVERSION_ACTION_PLAN.md for rollback steps.

**Q: How do I assign priorities?**
A: Use guidelines in QUICK_REFERENCE.md or TASKMASTER_REFACTOR_GUIDE.md

**Q: What happens to the Phase field?**
A: It's removed. Consider archiving to separate document if important.

---

## Success Criteria

✅ All 130 task files converted to taskmaster-ai format
✅ All required fields present (ID, Title, Status, Priority, Dependencies, Description, Details, Test Strategy)
✅ No data loss from original files
✅ Dependencies correctly mapped to comma-separated format
✅ Priority levels logically assigned
✅ Test Strategy sections added to all tasks
✅ Files committed to git with clear message
✅ PR reviewed and merged

---

## Technical Details

### Task File Location
```
/Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/
```

### Phases to Convert
- phase-01-branding/ (14 files)
- phase-02-roles/ (10 files)
- phase-03-madaris/ (20 files)
- phase-04-teachers/ (5 files)
- phase-05-curriculum/ (10 files)
- phase-06-student/ (12 files)
- phase-07-academic/ (10 files)
- phase-08-programs/ (10 files)
- phase-09-parent/ (10 files)
- phase-10-adapt/ (8 files)
- phase-11-forms/ (6 files)
- phase-12-templates/ (5 files)
- phase-13-database/ (8 files)
- phase-14-frontend/ (2 files)

### Required Python Version
Python 3.6+ for convert_to_taskmaster.py

---

## Before You Start

Make sure you have:

- [ ] Git repository access
- [ ] Write access to the tasks-refactor directory
- [ ] Python 3.6+ (if using automation)
- [ ] Time to complete (10-12 hours for hybrid approach)
- [ ] Understanding of task format (read at least QUICK_REFERENCE.md)

---

## Contact & Support

For questions or issues:
1. Check the FAQ section in TASKMASTER_REFACTOR_GUIDE.md
2. Review examples in SAMPLE_CONVERSIONS.md
3. Follow step-by-step guide in CONVERSION_ACTION_PLAN.md
4. Check git history for previous conversions

---

## Summary

You have:
- ✅ 130 task files to convert
- ✅ Complete documentation & guides
- ✅ Automation script ready
- ✅ Real examples to follow
- ✅ Step-by-step plan

You need to:
1. Choose conversion approach (recommended: Hybrid/C)
2. Read relevant documentation
3. Execute conversion
4. Validate results
5. Commit and PR

**Estimated time**: 10-12 hours for hybrid approach

**Ready to start?** Begin with **QUICK_REFERENCE.md**

---

**Last Updated**: November 20, 2025
**Status**: Ready to implement
**Questions?** See documentation files above
