# Taskmaster-AI Format Refactoring Guide

## Current Status Analysis

**Total Tasks Found:** 130 task files
**Current Format:** Custom markdown format (non-standard)
**Target Format:** taskmaster-ai MCP specification

---

## Format Comparison

### Current Format (Custom)
```markdown
# Task 001: Create Full Database Backup

## Phase: Pre-Implementation

## Status: done

## Dependencies:
None - This is the first task

## Description:
Brief description...

## Acceptance Criteria:
- [ ] Criteria 1
- [ ] Criteria 2

## Steps:
1. Step 1
2. Step 2

## Files Affected:
- file1.txt
- file2.txt

## Notes:
Additional notes...
```

### Target Format (taskmaster-ai MCP)
```markdown
# Task ID: 001
# Title: Create Full Database Backup
# Status: done
# Dependencies: none
# Priority: high
# Description: Brief description of the task

# Details:
Comprehensive implementation instructions including:
- Step-by-step procedures
- Acceptance criteria (formatted as clear checkpoints)
- File modifications needed
- Important notes and edge cases
- Time estimates

# Test Strategy:
How to verify the task is complete:
- Verification steps
- Success criteria
- Rollback procedures if needed
```

---

## Key Differences to Address

| Aspect | Current | Target | Action |
|--------|---------|--------|--------|
| **Task ID Format** | `# Task 001:` | `# Task ID: 001` | Separate ID from title |
| **Title** | Inline with ID | `# Title:` | Create dedicated field |
| **Phase** | `## Phase:` | *(Removed)* | Remove/archive this field |
| **Status** | `## Status:` | `# Status:` | Change to single `#` |
| **Dependencies** | Bullet list | Comma-separated | Flatten to single line |
| **Priority** | *(Missing)* | `# Priority:` | Add priority field |
| **Description** | `## Description:` | `# Description:` | Keep but make concise |
| **Acceptance Criteria** | `## Acceptance Criteria:` | Merge into Details | Move to Details section |
| **Steps** | `## Steps:` | Part of Details | Consolidate content |
| **Files Affected** | `## Files Affected:` | Part of Details | Consolidate content |
| **Notes** | `## Notes:` | Merge into Details | Consolidate content |
| **Test/Verification** | *(Missing)* | `# Test Strategy:` | Create new section |

---

## Migration Steps

### Step 1: Define Priority Levels
For each task, assign a priority based on:
- **high** - Blocking other tasks, critical for system stability
- **medium** - Important but not immediately blocking
- **low** - Nice-to-have, can be deferred

### Step 2: Convert Dependencies Format
Change from:
```
## Dependencies:
- task_007.txt (context processor created)
- task_011.txt (base template updated)
```

To:
```
# Dependencies: 007, 011
```

### Step 3: Consolidate Content into Details
Merge all implementation information:
- Steps (numbered procedures)
- Acceptance Criteria (as verification checkpoints)
- Files Affected (list files being modified)
- Notes (edge cases, gotchas, time estimates)

### Step 4: Create Test Strategy Section
Document verification approach:
- How to verify the task is complete
- What success looks like
- Rollback steps if something goes wrong

### Step 5: Update Header Format
Convert from:
```
# Task 001: Create Full Database Backup

## Phase: Pre-Implementation

## Status: done
```

To:
```
# Task ID: 001
# Title: Create Full Database Backup
# Status: done
# Priority: high
# Dependencies: none
# Description: Create comprehensive backup of entire database before starting any refactoring work.
```

---

## Example Conversion

### Before (Current Format):
```markdown
# Task 001: Create Full Database Backup

## Phase: Pre-Implementation

## Status: done

## Dependencies:
None - This is the first task

## Description:
Create comprehensive backup of entire database before starting any refactoring work. This backup will be used for rollback if needed.

## Acceptance Criteria:
- [x] PostgreSQL database dump created successfully
- [x] Backup file is verified (can be restored)
- [x] Backup is stored in at least 2 locations
- [x] Backup file is dated with current timestamp
- [x] Backup size is reasonable
- [x] Test restore on a separate instance

## Steps:
1. Check database size
2. Create dump
3. Compress backup
4. Upload to cloud storage
5. Keep local copy
6. Document location
7. Test restore

## Files Affected:
- Database dump file: backup_YYYYMMDD_HHMMSS.sql.gz
- BACKUP_LOG.md

## Notes:
- Estimate: 30-60 minutes
- For dev environment, backup anytime
```

### After (taskmaster-ai Format):
```markdown
# Task ID: 001
# Title: Create Full Database Backup
# Status: done
# Dependencies: none
# Priority: high
# Description: Create comprehensive backup of entire database before starting any refactoring work.

# Details:
Comprehensive backup ensures safe rollback if refactoring goes wrong.

## Implementation Steps:
1. Check database size: `SELECT pg_size_pretty(pg_database_size('madaris_dev'));`
2. Create dump: `pg_dump madaris_dev > backup_$(date +%Y%m%d_%H%M%S).sql`
3. Compress: `gzip backup_*.sql`
4. Upload to cloud storage (AWS S3, Google Cloud, etc.)
5. Keep local copy in safe location
6. Document backup location in BACKUP_LOG.md
7. Test restore on staging/test environment

## Acceptance Criteria:
- PostgreSQL database dump created successfully
- Backup file is verified (can be restored)
- Backup is stored in at least 2 locations (local + cloud)
- Backup file is dated with current timestamp
- Backup size is reasonable (matches expected database size)
- Test restore on a separate instance to verify integrity

## Files Modified:
- backup_YYYYMMDD_HHMMSS.sql.gz (new database dump)
- BACKUP_LOG.md (created/updated with backup location)

## Important Notes:
- For dev environment: backup anytime (no low-traffic requirement needed)
- Ensure destination has 2-3x database size free space
- Large databases may take hours; check size first
- pg_dump doesn't include roles/users; backup separately if needed
- Estimated time: 30-60 minutes depending on database size

# Test Strategy:
1. Verify backup file exists and has reasonable size
2. Restore on test database:
   ```bash
   createdb madaris_test_restore
   gunzip -c backup_*.sql.gz | psql madaris_test_restore
   psql madaris_test_restore -c "SELECT COUNT(*) FROM chapters_chapter;"
   dropdb madaris_test_restore
   ```
3. Confirm restore completed without errors
4. Verify data integrity in restored database
```

---

## Implementation Plan

### Batch 1: Understand Current Structure (130 tasks)
- [x] Read all task files to understand current content
- [x] Identify priority levels for each task
- [x] Map dependencies between tasks
- [ ] Create a mapping spreadsheet

### Batch 2: Create Conversion Tool (Optional)
- [ ] Write Python script to automate format conversion
- [ ] Test on single task file
- [ ] Verify output matches taskmaster-ai spec

### Batch 3: Convert All Tasks
- [ ] Convert phase-01-branding tasks (14 tasks)
- [ ] Convert phase-02-roles tasks (10 tasks)
- [ ] Convert phase-03-madaris tasks (20 tasks)
- [ ] Convert phase-04-teachers tasks (5 tasks)
- [ ] Convert phase-05-curriculum tasks (10 tasks)
- [ ] Convert phase-06-student tasks (12 tasks)
- [ ] Convert phase-07-academic tasks (10 tasks)
- [ ] Convert phase-08-programs tasks (10 tasks)
- [ ] Convert phase-09-parent tasks (10 tasks)
- [ ] Convert phase-10-adapt tasks (8 tasks)
- [ ] Convert phase-11-forms tasks (6 tasks)
- [ ] Convert phase-12-templates tasks (5 tasks)
- [ ] Convert phase-13-database tasks (8 tasks)
- [ ] Convert phase-14-frontend tasks (2 tasks)

### Batch 4: Validation
- [ ] Verify all 130 tasks converted correctly
- [ ] Check all dependencies resolve properly
- [ ] Test with taskmaster-ai MCP commands
- [ ] Update any documentation

---

## Critical Considerations

### 1. Preserve All Information
Current format contains valuable information that must migrate:
- **Phase** field should be archived (perhaps in `# Description:` or separate tracking)
- **Acceptance Criteria** is crucial - move to Details
- **Notes** section contains important edge cases

### 2. Priority Assignment Strategy
Since current format lacks priority, assign based on:
- Tasks that block other tasks → **high**
- Database migration tasks → **high**
- UI/documentation tasks → **medium**
- Optional improvements → **low**

### 3. Maintain Dependency Graph
Current dependencies are well-documented. Ensure conversion maintains:
- Cross-phase dependencies
- Prerequisites relationships
- Blocking task identification

### 4. Test Strategy Creation
New `# Test Strategy:` section must document:
- How to know task is complete
- Verification commands
- How to roll back if needed

---

## Recommended Approach

### Option A: Automated Conversion (Recommended)
1. Write Python script to parse current format
2. Extract all fields
3. Generate taskmaster-ai formatted output
4. Batch update all 51 files
5. Manual review and testing

**Advantages:** Fast, consistent, less error-prone
**Time:** ~5-6 hours

### Option B: Manual Conversion
1. Convert files one by one
2. Review each conversion
3. Ensure information preservation
4. Manual consistency checks

**Advantages:** Complete control, catch edge cases
**Time:** ~20-25 hours

### Option C: Hybrid Approach
1. Use automated conversion as base
2. Manually review each file
3. Fix any formatting issues
4. Verify dependencies

**Advantages:** Best of both worlds
**Time:** ~10-12 hours

---

## Next Steps

1. **Review this guide** with team
2. **Decide on approach** (A, B, or C)
3. **Create automation** if pursuing Option A or C
4. **Convert tasks** in batches
5. **Test with taskmaster-ai** MCP
6. **Update documentation** references
7. **Archive old format** if needed

---

## Files to Update After Conversion

After tasks are converted, update these files:
- [ ] `START_HERE.md` - Update task file references
- [ ] `CLAUDE.md` - Update task file structure instructions
- [ ] All `README.md` in phase directories
- [ ] CI/CD scripts that parse task files

---

## Success Criteria

✅ All 130 task files converted to taskmaster-ai format
✅ All fields properly mapped (no data loss)
✅ Dependencies properly converted to comma-separated format
✅ Priority levels assigned to all tasks
✅ Test Strategy section added to all tasks
✅ No breaking changes to existing task workflows
✅ Compatible with taskmaster-ai MCP commands

