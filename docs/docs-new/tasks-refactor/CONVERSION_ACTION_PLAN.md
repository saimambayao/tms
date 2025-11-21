# Task Conversion Action Plan

## Quick Summary

You have **130 task files** in custom markdown format that need to be converted to the **taskmaster-ai MCP format**.

**Current Status:** Analysis complete ✓
**Next Step:** Choose conversion approach and execute

**Estimated Time:** 5-12 hours (depending on approach)

---

## What Needs to Change

### Current Format Example:
```markdown
# Task 001: Create Full Database Backup

## Phase: Pre-Implementation
## Status: done
## Dependencies:
None - This is the first task

## Description:
...

## Acceptance Criteria:
- [ ] Criteria 1
...
```

### New Format Example:
```markdown
# Task ID: 001
# Title: Create Full Database Backup
# Status: done
# Priority: high
# Dependencies: none
# Description: Create comprehensive backup of entire database...

# Details:
[Consolidated implementation info]

# Test Strategy:
[Verification approach]
```

**Key Changes:**
- Separate Task ID from Title
- Add Priority field
- Consolidate implementation sections (Steps, Criteria, Files, Notes → Details)
- Add Test Strategy section
- Remove Phase field (can be noted elsewhere if needed)

---

## Three Conversion Approaches

### Approach A: Full Automation (FASTEST)

**Use the provided Python script to auto-convert all files**

**Steps:**
```bash
cd /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor

# Convert a single file first to verify:
python convert_to_taskmaster.py \
  --input phase-01-branding/task_001.txt \
  --output phase-01-branding/task_001_TEST.txt

# Review the output to verify conversion quality

# If satisfied, batch convert all files:
python convert_to_taskmaster.py \
  --batch \
  --input-dir phase-01-branding \
  --output-dir phase-01-branding-converted

# Repeat for each phase:
python convert_to_taskmaster.py --batch --input-dir phase-02-roles --output-dir phase-02-roles-converted
python convert_to_taskmaster.py --batch --input-dir phase-03-madaris --output-dir phase-03-madaris-converted
# ... etc for remaining phases

# Once verified, replace original files:
# BACKUP FIRST!
git checkout -b refactor/taskmaster-format
# ... move converted files back to original locations
# ... commit and PR
```

**Pros:**
- Fast (5-6 hours total)
- Consistent formatting
- Less manual error

**Cons:**
- Less human review
- May miss edge cases
- Requires Python script debugging if issues arise

---

### Approach B: Manual Conversion (THOROUGH)

**Edit each file manually, one by one**

**For each task file:**
1. Read the file
2. Identify: ID, Title, Status, Dependencies, Priority, Description
3. Consolidate Steps + Criteria + Files + Notes into Details
4. Create Test Strategy section
5. Save with new format

**Tools to use:**
```bash
# Open a file
code phase-01-branding/task_001.txt

# Edit, then verify format is correct
grep "^# Task ID:" phase-01-branding/task_001.txt  # Should exist
grep "^# Title:" phase-01-branding/task_001.txt    # Should exist
grep "^# Test Strategy:" phase-01-branding/task_001.txt  # Should exist
```

**Pros:**
- Full control and understanding
- Catch edge cases and nuances
- Ensure data integrity

**Cons:**
- Slow (20-25 hours)
- Error-prone
- Tedious and repetitive

---

### Approach C: Hybrid (RECOMMENDED)

**Use automation as foundation, then manual review**

**Steps:**
```bash
# 1. Create a test copy to work with
cp -r phase-01-branding phase-01-branding-test

# 2. Run conversion on test copy
python convert_to_taskmaster.py \
  --batch \
  --input-dir phase-01-branding-test \
  --output-dir phase-01-branding-test-converted

# 3. Review converted files
cd phase-01-branding-test-converted
for file in task_*.txt; do
  echo "=== $file ==="
  head -20 "$file"
  echo ""
done

# 4. For each file, verify:
#    - All information is present
#    - Dependencies are correct
#    - Priority seems appropriate
#    - Test Strategy makes sense

# 5. If acceptable, replace originals
cd ../..
git checkout -b refactor/taskmaster-format
cp phase-01-branding-test-converted/task_*.txt phase-01-branding/

# 6. Spot-check a few files
code phase-01-branding/task_001.txt
code phase-01-branding/task_010.txt
code phase-01-branding/task_015.txt

# 7. If all look good, commit
git add phase-01-branding/task_*.txt
git commit -m "Convert phase-01-branding tasks to taskmaster-ai format"

# 8. Repeat for remaining phases
```

**Pros:**
- Fast overall (10-12 hours)
- Good safety with verification
- Best balance

**Cons:**
- Still requires some manual work
- Need to manage test copies

---

## Recommended: Approach C (Hybrid)

### Why Hybrid is Best:
1. ✓ Speed of automation
2. ✓ Verification of manual review
3. ✓ Less error-prone than full manual
4. ✓ Less hands-off than full automation
5. ✓ Can catch converter bugs early

---

## Step-by-Step Execution (Hybrid Approach)

### Phase 1: Preparation
```bash
cd /Users/saidamenmambayao/apps/madaris-ms

# Ensure you're on main and up to date
git status
git pull origin main

# Create feature branch
git checkout -b refactor/taskmaster-format
```

### Phase 2: Test Conversion (Phase 1 as test case)
```bash
# Copy phase-01-branding to test directory
cp -r docs/docs-new/tasks-refactor/phase-01-branding \
     docs/docs-new/tasks-refactor/phase-01-branding-test

# Run conversion
cd docs/docs-new/tasks-refactor
python convert_to_taskmaster.py \
  --batch \
  --input-dir phase-01-branding-test \
  --output-dir phase-01-branding-converted

# Review sample converted files
echo "=== Reviewing converted files ==="
head -30 phase-01-branding-converted/task_001.txt
echo ""
head -30 phase-01-branding-converted/task_008.txt
echo ""
head -30 phase-01-branding-converted/task_016.txt
```

### Phase 3: Manual Verification
```bash
# Check each converted file for:
# 1. Format compliance
# 2. Data integrity
# 3. Priority assignment
# 4. Test Strategy relevance

# Open in editor for spot-checking
code phase-01-branding-converted/task_*.txt

# Specific checks:
# - Task ID: is it just the number? (001, not Task 001)
# - Title: is descriptive and clear?
# - Status: unchanged from original?
# - Dependencies: converted to comma-separated (001, 002, 003)?
# - Priority: high/medium/low assigned?
# - Description: one-sentence summary?
# - Details: contains all original information?
# - Test Strategy: makes sense for task type?
```

### Phase 4: Apply Conversion
```bash
# If conversion looks good, copy to production location
cd docs/docs-new/tasks-refactor
cp phase-01-branding-converted/task_*.txt phase-01-branding/

# Verify files were copied
ls -la phase-01-branding/task_*.txt | wc -l  # Should show count

# Show a converted file to verify
head -30 phase-01-branding/task_001.txt
```

### Phase 5: Repeat for Remaining Phases
```bash
# For each remaining phase, repeat steps 2-4:

# Phase 2
python convert_to_taskmaster.py --batch --input-dir phase-02-roles --output-dir phase-02-roles-converted
# ... review phase-02-roles-converted/task_*.txt
cp phase-02-roles-converted/task_*.txt phase-02-roles/

# Phase 3
python convert_to_taskmaster.py --batch --input-dir phase-03-madaris --output-dir phase-03-madaris-converted
# ... review
cp phase-03-madaris-converted/task_*.txt phase-03-madaris/

# Continue for all remaining phases...
# phase-04-teachers
# phase-05-curriculum
# phase-06-student
# phase-07-academic
# phase-08-programs
# phase-09-parent
# phase-10-adapt
# phase-11-forms
# phase-12-templates
# phase-13-database
# phase-14-frontend
```

### Phase 6: Cleanup
```bash
# Remove test directories
rm -rf phase-01-branding-test
rm -rf phase-01-branding-converted
rm -rf phase-02-roles-converted
# ... etc

# Verify all phases are converted
for phase in phase-*; do
  count=$(ls "$phase"/task_*.txt 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    # Check format of first task
    if grep -q "^# Task ID:" "$phase"/task_*.txt | head -1; then
      echo "✓ $phase: Converted ($count tasks)"
    else
      echo "✗ $phase: NOT converted ($count tasks)"
    fi
  fi
done
```

### Phase 7: Commit and Push
```bash
# Stage all changes
git add docs/docs-new/tasks-refactor/phase-*/task_*.txt

# Create meaningful commit
git commit -m "Refactor: Convert 130 task files to taskmaster-ai MCP format

- Separated Task IDs from Titles
- Added Priority field to all tasks
- Consolidated implementation steps into Details section
- Created Test Strategy sections for verification
- Converted dependencies to comma-separated format
- Preserved all original task information"

# Push to GitHub
git push -u origin refactor/taskmaster-format

# Create PR on GitHub for review
gh pr create \
  --title "Refactor: Convert tasks to taskmaster-ai format" \
  --body "Convert all 130 task files to taskmaster-ai MCP specification"
```

---

## Validation Checklist

After conversion, verify:

- [ ] All 130 task files converted to new format
- [ ] No task files missing
- [ ] All files follow new format (check headers)
- [ ] All dependencies converted to comma-separated format
- [ ] All priorities assigned (high/medium/low)
- [ ] All test strategies present
- [ ] Original content preserved (no data loss)
- [ ] Dependencies still make logical sense
- [ ] Ready for taskmaster-ai MCP compatibility

**Quick validation script:**
```bash
echo "Checking format compliance..."

# Count files
total=$(find phase-*/ -name "task_*.txt" | wc -l)
echo "Total tasks: $total (should be 130)"

# Check for required fields
echo ""
echo "Checking for required fields..."
for dir in phase-*/; do
  for file in "$dir"task_*.txt; do
    missing=""
    grep -q "^# Task ID:" "$file" || missing="$missing Task ID"
    grep -q "^# Title:" "$file" || missing="$missing Title"
    grep -q "^# Status:" "$file" || missing="$missing Status"
    grep -q "^# Priority:" "$file" || missing="$missing Priority"
    grep -q "^# Test Strategy:" "$file" || missing="$missing TestStrategy"

    if [ -n "$missing" ]; then
      echo "✗ $file:$missing"
    fi
  done
done

echo "✓ Validation complete"
```

---

## Rollback Plan

If conversion doesn't go well:

```bash
# Option 1: Rollback entire branch
git checkout main
git branch -D refactor/taskmaster-format

# Option 2: Reset to specific commit
git log --oneline | head -5
git reset --hard [commit-hash]

# Option 3: Restore from git history
git checkout main -- docs/docs-new/tasks-refactor/
```

---

## Timeline Estimate (Hybrid Approach)

| Phase | Time | Notes |
|-------|------|-------|
| Preparation & Branch | 10 min | Create git branch |
| Test Phase 1 | 30 min | Run conversion, review 3-5 files |
| Manual Verification | 45 min | Spot-check samples |
| Apply Phase 1 | 10 min | Copy files |
| Phases 2-14 | 195 min | Repeat: 10 min automation + 5 min review per phase (x13) |
| Cleanup & Validation | 30 min | Remove test dirs, final checks |
| Commit & Push | 15 min | Git operations |
| **Total** | **9-10 hours** | Per project preferences |

---

## Next Steps

1. **Choose an approach** (Recommended: Hybrid/Approach C)
2. **Run test conversion** on phase-01-branding first
3. **Review converted output** and verify quality
4. **Apply to all phases** once satisfied
5. **Commit and create PR** for team review
6. **Merge to main** after approval

---

## Support Files Created

The following documentation has been created to help:

1. **TASKMASTER_REFACTOR_GUIDE.md** - Detailed format comparison and guidelines
2. **SAMPLE_CONVERSIONS.md** - Before/after examples of task conversions
3. **convert_to_taskmaster.py** - Automation script (Python)
4. **CONVERSION_ACTION_PLAN.md** - This file with step-by-step instructions

---

## Questions to Resolve

Before starting, clarify:

1. **Approach Preference**: Which conversion method do you prefer?
   - A (Fully Automated)
   - B (Fully Manual)
   - C (Hybrid - Recommended)

2. **Archive Phase Field**: Should Phase information be:
   - Removed entirely?
   - Kept in Details section?
   - Added as comment?

3. **Timeline**: Can this be done this week, or should it be scheduled later?

4. **Team Review**: Who should review the converted files before merge?

5. **Compatibility**: Do any tools currently depend on the old task format?

---

## Success Criteria

✓ All 130 task files converted to taskmaster-ai format
✓ No data loss during conversion
✓ All dependencies properly mapped
✓ Priority levels assigned to all tasks
✓ Test Strategy sections added to all tasks
✓ Ready for use with taskmaster-ai MCP
✓ Team consensus on format
✓ Merged to main branch

---

## Starting the Conversion

Ready to begin? Run:

```bash
# Create working branch
git checkout -b refactor/taskmaster-format

# Test conversion on Phase 1
cd docs/docs-new/tasks-refactor
python convert_to_taskmaster.py \
  --input phase-01-branding/task_001.txt \
  --output phase-01-branding/task_001_TEST.txt

# Review the output
cat phase-01-branding/task_001_TEST.txt

# If satisfied, proceed with full batch conversion
# Follow the step-by-step guide above
```

Good luck! 🚀
