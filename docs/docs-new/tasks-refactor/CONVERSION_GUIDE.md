# Task Conversion Guide

## Overview

This guide explains how to use `convert_to_taskmaster.py` to convert task files from the current custom format to taskmaster-ai MCP format.

**Script Location:** `/Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/convert_to_taskmaster.py`

**Total Tasks:** 130 tasks across 14 phases (phases 1-14)

---

## Quick Start

### 1. Convert a Single Task

```bash
cd /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor

python3 convert_to_taskmaster.py \
  --input phase-03-madaris/task_026.txt \
  --output converted/task_026.txt
```

**Output:**
```
✓ Converted: task_026.txt → converted/task_026.txt

✓ Conversion complete!
  Input:  phase-03-madaris/task_026.txt
  Output: converted/task_026.txt
```

---

### 2. Convert a Single Phase (Batch Mode)

```bash
cd /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor

python3 convert_to_taskmaster.py \
  --batch \
  --input-dir phase-03-madaris \
  --output-dir converted/phase-03-madaris
```

**Output:**
```
============================================================
Converting phase: phase-03-madaris
Found 20 task files...
============================================================

[1/20] ✓ Converted: task_026.txt → converted/phase-03-madaris/task_026.txt
[2/20] ✓ Converted: task_027.txt → converted/phase-03-madaris/task_027.txt
...
[20/20] ✓ Converted: task_045.txt → converted/phase-03-madaris/task_045.txt

============================================================
Phase conversion complete!
  ✓ Success: 20
  ✗ Errors:  0
============================================================
```

---

### 3. Convert All Phases (All 130 Tasks)

```bash
cd /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor

python3 convert_to_taskmaster.py \
  --all \
  --output-dir converted/
```

**Output:**
```
############################################################
# CONVERTING ALL PHASES
# Base directory: /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor
# Output directory: converted/
# Found 14 phases
# Mode: LIVE
############################################################

[... processes all 130 tasks across 14 phases ...]

############################################################
# CONVERSION SUMMARY
############################################################

Phase Results:
  ✓ phase-01-branding: 14 succeeded, 0 failed
  ✓ phase-02-roles: 10 succeeded, 0 failed
  ✓ phase-03-madaris: 20 succeeded, 0 failed
  ✓ phase-04-teachers: 5 succeeded, 0 failed
  ✓ phase-05-curriculum: 10 succeeded, 0 failed
  ✓ phase-06-student: 12 succeeded, 0 failed
  ✓ phase-07-academic: 10 succeeded, 0 failed
  ✓ phase-08-programs: 10 succeeded, 0 failed
  ✓ phase-09-parent: 10 succeeded, 0 failed
  ✓ phase-10-adapt: 8 succeeded, 0 failed
  ✓ phase-11-forms: 6 succeeded, 0 failed
  ✓ phase-12-templates: 5 succeeded, 0 failed
  ✓ phase-13-database: 8 succeeded, 0 failed
  ✓ phase-14-frontend: 2 succeeded, 0 failed

============================================================
Total Statistics:
  Total tasks processed: 130
  ✓ Successful conversions: 130
  ✗ Failed conversions: 0
  Duration: 3.45 seconds
  Average: 0.03 seconds per task
============================================================

✓ All converted files saved to: converted/
```

---

## Advanced Usage

### 4. Dry Run (Validate Without Writing)

Test the conversion without creating output files:

```bash
python3 convert_to_taskmaster.py \
  --all \
  --output-dir converted/ \
  --dry-run
```

**Use Case:** Validate that all tasks can be converted successfully before actually writing files.

---

### 5. Validate a Single Task

Check if a task file is valid without converting:

```bash
python3 convert_to_taskmaster.py \
  --input phase-03-madaris/task_026.txt \
  --validate-only
```

**Output:**
```
Validating: phase-03-madaris/task_026.txt
✓ Task file is valid
```

Or if there are issues:
```
Validating: phase-03-madaris/task_026.txt
✗ Task file has errors:
  - Missing required field: # Task ID:
  - Task ID could not be parsed

Warnings:
  - No acceptance criteria found
```

---

## Command Reference

### Required Arguments

| Mode | Arguments | Description |
|------|-----------|-------------|
| Single file | `--input FILE` `--output FILE` | Convert one task file |
| Batch (phase) | `--batch` `--input-dir DIR` `--output-dir DIR` | Convert all tasks in a directory |
| All phases | `--all` `--output-dir DIR` | Convert all tasks in all phase directories |

### Optional Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Validate without writing files |
| `--validate-only` | Only validate, don't convert (single file only) |
| `-h`, `--help` | Show help message |

---

## Conversion Details

### Input Format (Current)

```markdown
# Task 026: Backup Chapter App Before Renaming

## Phase: Phase 3 - Madaris Management (Chapter Transition)

## Status: pending

## Dependencies:
- task_025.txt (Phase 2 verified complete)
- task_001.txt (database backup exists)

## Description:
Create comprehensive backup of chapters app directory...

## Acceptance Criteria:
- [ ] chapters app directory backed up
- [ ] Chapter-related database tables exported
- [ ] Backup verified (can be restored)

## Steps:
1. Create backup directory:
   ```bash
   mkdir -p /path/to/backups
   ```
...

## Files Affected:
- backups/phase3_chapters/chapters_app_backup/
- backups/phase3_chapters/chapter_data.json

## Notes:
- This backup is specific to Phase 3
- Keep backup until Phase 3 is fully verified
```

### Output Format (Taskmaster-AI MCP)

```markdown
# Task ID: 026
# Title: Backup Chapter App Before Renaming
# Status: pending
# Dependencies: 001, 025
# Priority: high
# Description: Create comprehensive backup of chapters app directory and database tables before renaming Chapter model to Madrasah.

# Details:
Create comprehensive backup of chapters app directory and database tables before renaming Chapter model to Madrasah. This allows rollback if issues occur.

## Implementation Steps:
1. Create backup directory:
   ```bash
   mkdir -p /path/to/backups
   ```
...

## Acceptance Criteria:
- chapters app directory backed up
- Chapter-related database tables exported
- Backup verified (can be restored)

## Files Modified:
- `backups/phase3_chapters/chapters_app_backup/`
- `backups/phase3_chapters/chapter_data.json`

## Important Notes:
- This backup is specific to Phase 3
- Keep backup until Phase 3 is fully verified

# Test Strategy:
1. Verify backup file exists and has reasonable size
2. Restore on test database to verify integrity
3. Confirm all tables present in restored database
4. Compare row counts with original database
```

---

## Key Features

### 1. Automatic Priority Detection

The converter automatically assigns priority based on keywords:

**High Priority:**
- database, migration, backup, rollback, security, critical
- risk, production, data loss, authentication, authorization

**Medium Priority:**
- model, admin, form, template, api, view, url
- endpoint, validation, testing, configuration

**Low Priority:**
- documentation, style, css, ui, optimization, refactor
- cleanup, formatting, comment

### 2. Smart Test Strategy Generation

The converter generates context-aware test strategies based on task type:

- **Backup tasks:** Verify, restore, compare
- **Migration tasks:** Test forward/reverse, check data integrity
- **Model tasks:** Test schema, admin interface, backward compatibility
- **Template tasks:** Visual testing, responsive design
- **API tasks:** Test endpoints, auth, error responses
- **Form tasks:** Validation, error messages, CSRF
- **Admin tasks:** CRUD operations, filters, search

### 3. Validation & Error Handling

The converter validates:
- Required fields (Task ID, Title, Status, Dependencies, Priority)
- Required sections (Details, Test Strategy)
- Task ID format (supports numbers and letters like "015a")
- Status values (pending, in_progress, done)
- File parsing errors

Warnings for:
- Missing acceptance criteria
- Missing implementation steps
- Unknown status values (auto-corrects to 'pending')

### 4. Progress Reporting

For batch operations, the converter shows:
- Current progress: `[15/20]`
- Success/error counts per phase
- Overall summary with statistics
- Duration and average time per task
- Phase-by-phase results

---

## Example Workflow

### Scenario: Convert All Tasks for Production Use

```bash
# Step 1: Navigate to tasks directory
cd /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor

# Step 2: Dry run to validate all tasks
python3 convert_to_taskmaster.py --all --output-dir converted/ --dry-run

# Step 3: Review the validation results
# (Check for any errors or warnings)

# Step 4: Convert all tasks
python3 convert_to_taskmaster.py --all --output-dir converted/

# Step 5: Verify output
ls -R converted/

# Step 6: Test a few converted files
cat converted/phase-03-madaris/task_026.txt
cat converted/phase-01-branding/task_001.txt

# Step 7: Use converted files with taskmaster-ai MCP
# (The converted files are now ready to use)
```

---

## Troubleshooting

### Issue: "No task files found"

**Cause:** Wrong directory or no files matching `task_*.txt` pattern

**Solution:**
```bash
# Verify you're in the correct directory
pwd

# List available task files
ls phase-*/task_*.txt

# Use correct path
python3 convert_to_taskmaster.py --batch \
  --input-dir ./phase-03-madaris \
  --output-dir ./converted/phase-03
```

### Issue: "Validation failed"

**Cause:** Task file doesn't match expected format

**Solution:**
```bash
# Validate to see specific errors
python3 convert_to_taskmaster.py \
  --input problem_task.txt \
  --validate-only

# Check errors and fix source file
# Common issues:
# - Missing "# Task NNN:" header
# - Missing "## Status:" section
# - Malformed task ID
```

### Issue: "Permission denied"

**Cause:** Can't write to output directory

**Solution:**
```bash
# Check directory permissions
ls -la converted/

# Create output directory with correct permissions
mkdir -p converted/phase-03
chmod 755 converted/phase-03

# Or use a different output location
python3 convert_to_taskmaster.py \
  --batch \
  --input-dir phase-03-madaris \
  --output-dir ~/temp/converted
```

---

## Task Breakdown by Phase

| Phase | Directory | Tasks | Description |
|-------|-----------|-------|-------------|
| 1 | phase-01-branding | 14 | Branding and naming updates |
| 2 | phase-02-roles | 10 | Role-based access control |
| 3 | phase-03-madaris | 20 | Chapter to Madrasah transition |
| 4 | phase-04-teachers | 5 | Teacher/Asatidz management |
| 5 | phase-05-curriculum | 10 | Curriculum management |
| 6 | phase-06-student | 12 | Student model transition |
| 7 | phase-07-academic | 10 | Academic year management |
| 8 | phase-08-programs | 10 | Program management |
| 9 | phase-09-parent | 10 | Parent/Guardian features |
| 10 | phase-10-adapt | 8 | Adaptation and refinement |
| 11 | phase-11-forms | 6 | Forms and validation |
| 12 | phase-12-templates | 5 | Template updates |
| 13 | phase-13-database | 8 | Database optimization |
| 14 | phase-14-frontend | 2 | Frontend improvements |
| **TOTAL** | | **130** | |

---

## Best Practices

1. **Always dry-run first** when converting large batches
2. **Validate critical tasks** individually before batch conversion
3. **Review warnings** - they indicate potential issues
4. **Backup original files** before overwriting
5. **Test converted files** with taskmaster-ai before committing
6. **Use meaningful output directories** to organize converted files

---

## Script Enhancements

### Version 2.0 Features

1. **Better Error Handling**
   - Custom exceptions for conversion and validation errors
   - Detailed error messages with context
   - Graceful handling of malformed files

2. **Progress Reporting**
   - Real-time progress indicators: `[15/20]`
   - Phase-by-phase summaries
   - Overall statistics with timing

3. **Validation**
   - Pre-conversion validation
   - Required field checks
   - Format validation
   - Warning for non-critical issues

4. **Batch Operations**
   - Convert single phase with `--batch`
   - Convert all phases with `--all`
   - Dry-run mode for testing
   - Validate-only mode

5. **Improved Priority Detection**
   - More keywords for high/medium/low priority
   - Context-aware detection from title, description, notes
   - Handles risk-level indicators

6. **Enhanced Test Strategies**
   - More task type patterns (app, api, form, admin, view, plan, test)
   - Multiple keyword matching
   - Duplicate removal with order preservation
   - Context-aware test generation

---

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Run with `--validate-only` to see specific errors
3. Use `--dry-run` to test without writing files
4. Review the script source code for implementation details

---

**Last Updated:** 2025-11-20
**Script Version:** 2.0
**Total Tasks:** 130 across 14 phases
