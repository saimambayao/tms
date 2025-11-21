# Tarbiyyah Management System - Refactoring Tasks

## Overview
This directory contains granular, actionable tasks for adapting and refactoring the existing BM Parliament codebase into a comprehensive Tarbiyyah Management System (Islamic Education Management System for BARMM).

**Important:** This is a refactoring project that transitions the existing parliamentary management system into an education management system while preserving the proven architecture and infrastructure.

## Directory Structure

Tasks are organized into phase subdirectories for better organization:

```
tasks-refactor/
├── phase-01-branding/      # Pre-Implementation + Phase 1 (Tasks 001-015)
├── phase-02-roles/          # Phase 2 - User Roles (Tasks 016-025)
├── phase-03-madaris/        # Phase 3 - Madaris Management (Tasks 026-045)
├── phase-04-teachers/       # Phase 4 - Asatidz/Teachers (Tasks 046-050)
├── phase-05-curriculum/     # Phase 5 - Curriculum (Tasks to be created)
├── phase-06-student/        # Phase 6 - Student Model (Tasks to be created)
├── phase-07-academic/       # Phase 7 - Academic Records (Tasks to be created)
├── phase-08-programs/       # Phase 8 - Programs Adaptation (Tasks to be created)
├── phase-09-parent/         # Phase 9 - Parent Portal (Tasks to be created)
├── phase-10-adapt/          # Phase 10 - Adaptation (Tasks to be created)
├── phase-11-forms/          # Phase 11 - Forms (Tasks to be created)
├── phase-12-templates/      # Phase 12 - Templates (Tasks to be created)
├── phase-13-database/       # Phase 13 - Database Cleanup (Tasks to be created)
└── phase-14-frontend/       # Phase 14 - Next.js Frontend (DEFERRED)
```

## Task Distribution by Phase
- **phase-01-branding/**: 14 tasks (Pre-Implementation + Branding) ✅ Created
- **phase-02-roles/**: 10 tasks (User Roles & Permissions) ✅ Created
- **phase-03-madaris/**: 20 tasks (Madaris Model Transition) ✅ Created
- **phase-04-teachers/**: 5 tasks (Teachers/Asatidz App) ✅ Created
- **phase-05-curriculum/**: ~10 tasks (To be created)
- **phase-06-student/**: ~12 tasks (To be created)
- **phase-07-academic/**: ~10 tasks (To be created)
- **phase-08-programs/**: ~10 tasks (To be created)
- **phase-09-parent/**: ~10 tasks (To be created)
- **phase-10-adapt/**: ~8 tasks (To be created)
- **phase-11-forms/**: ~6 tasks (To be created)
- **phase-12-templates/**: ~5 tasks (To be created)
- **phase-13-database/**: ~8 tasks (To be created)
- **phase-14-frontend/**: 2 tasks (Next.js - DEFERRED)

## Task File Format
Each task file follows this structure:
```
# Task XXX: [Title]
## Phase: [Phase Name]
## Status: pending | in-progress | done
## Dependencies: [List of task files]
## Description: [What needs to be done]
## Acceptance Criteria: [Checkboxes]
## Steps: [Numbered steps]
## Files Affected: [List of files]
## Notes: [Additional context]
```

## How to Use

1. **Navigate to phase directory**: `cd phase-01-branding/`
2. **Read task file**: `cat task_001.txt`
3. **Complete tasks in order** (dependencies are tracked in each file)
4. **Mark task status** as you progress (pending → in_progress → done)
5. **Check off acceptance criteria** as completed
6. **Follow steps sequentially** within each task
7. **Test after completion** before moving to next task

## Progress Tracking

- **Total Tasks Created**: 49 tasks
  - Phase 1: 14 tasks ✅
  - Phase 2: 10 tasks ✅
  - Phase 3: 20 tasks ✅
  - Phase 4: 5 tasks ✅
- **Tasks to Create**: ~79 tasks (Phases 5-13)
- **Deferred Tasks**: 2 tasks (Phase 14 - Next.js)
- **Completed**: 3 tasks (001-003 marked done)
- **In Progress**: 0 tasks
- **Pending**: 46 tasks

## Quick Start

### For Developers:
1. Start with **phase-01-branding/** - Safe, non-destructive branding changes
2. Read **START_HERE.md** for parallel execution strategy
3. Review **CLAUDE_CODE_PARALLEL_EXECUTION.md** for agent-based workflows

### For Project Managers:
1. Review main architecture: `/docs/docs-new/architecture-tarbiyyah/REFACTORING_PLAN.md`
2. Check cost proposal: `/docs/docs-new/architecture-tarbiyyah/TMS_DEVELOPMENT_PROPOSAL.md`
3. Review UI plan: `/docs/docs-new/architecture-tarbiyyah/UI_NAVIGATION_PLAN.md`

## Key Files

- **START_HERE.md** - Quick start guide for safe, parallel task execution
- **CLAUDE_CODE_PARALLEL_EXECUTION.md** - Guide for using Claude Code agents
- **PROGRESS.md** - Daily progress tracking (created in task_005)

## References

- **Main Refactoring Plan**: `/docs/docs-new/architecture-tarbiyyah/REFACTORING_PLAN.md`
- **UI Navigation Plan**: `/docs/docs-new/architecture-tarbiyyah/UI_NAVIGATION_PLAN.md`
- **Development Proposal**: `/docs/docs-new/architecture-tarbiyyah/TMS_DEVELOPMENT_PROPOSAL.md`
- **Rollback Plan**: `/docs/ROLLBACK_PLAN.md` (created in phase-01-branding/task_005.txt)
- **Claude Code Instructions**: `/docs/CLAUDE.md`

## Notes

- **Phase 14 (Next.js Frontend)** is deferred to a separate development branch
- **Phases 1-13** focus on backend Django refactoring with Django templates
- **Multitenant architecture** with 5 different role-based navigation bars
- **No database changes until Phase 2** - Phase 1 is 100% safe
