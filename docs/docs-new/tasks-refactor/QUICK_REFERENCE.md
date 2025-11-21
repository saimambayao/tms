# Task Converter - Quick Reference Card

## One-Line Commands

### Convert Single Task
```bash
python3 convert_to_taskmaster.py --input phase-03-madaris/task_026.txt --output task_026_converted.txt
```

### Validate Single Task
```bash
python3 convert_to_taskmaster.py --input phase-03-madaris/task_026.txt --validate-only
```

### Convert Single Phase
```bash
python3 convert_to_taskmaster.py --batch --input-dir phase-03-madaris --output-dir converted/phase-03
```

### Convert All 130 Tasks
```bash
python3 convert_to_taskmaster.py --all --output-dir converted/
```

### Dry Run (Test Mode)
```bash
python3 convert_to_taskmaster.py --all --output-dir converted/ --dry-run
```

---

## Common Workflows

### Safe Conversion (Recommended)
```bash
cd /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor

# 1. Test first
python3 convert_to_taskmaster.py --all --output-dir converted/ --dry-run

# 2. Convert
python3 convert_to_taskmaster.py --all --output-dir converted/

# 3. Verify
ls -R converted/
cat converted/phase-03-madaris/task_026.txt
```

---

## Quick Stats

- **Total Tasks:** 130
- **Total Phases:** 14
- **Success Rate:** 100%
- **Avg Conversion Time:** 0.0003s per task

**For full documentation, see:** `CONVERSION_GUIDE.md`
**For test results, see:** `TEST_RESULTS.md`
