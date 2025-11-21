# 🚀 Quick Start - Non-Destructive Tasks

## Safe to Implement NOW (No Database Changes)

### ✅ **Immediate Start - Parallel Execution (6 tasks in parallel)**

These tasks are **100% safe** and can run simultaneously:

#### **Agent Team A: Safety Net (Backups)**
```bash
# Terminal 1
phase-01-branding/task_001.txt - Create Full Database Backup (30-60 min)
phase-01-branding/task_002.txt - Backup Media Files (15-30 min)
phase-01-branding/task_003.txt - Create Git Tag (10 min)
```

#### **Agent Team B: Documentation**
```bash
# Terminal 2
phase-01-branding/task_005.txt - Document Rollback Plan (30 min)
phase-01-branding/task_006.txt - Get Stakeholder Sign-off (2-3 hours, can be async)
```

#### **Agent Team C: Configuration (Additive Only)**
```bash
# Terminal 3
phase-01-branding/task_007.txt - Create Context Processor (30 min)
```

**Duration if parallel:** 1-2 hours total
**Duration if sequential:** 4-7 hours total

---

## ✅ **Phase 1 Tasks - All Non-Destructive (Can start after task_007)**

These are **visual/UI changes only** - no database modifications:

### **Agent Team A: Static Assets**
```bash
phase-01-branding/task_008.txt - Update PWA Manifest (15 min)
phase-01-branding/task_009.txt - Update Logos/Favicons (20 min)
phase-01-branding/task_010.txt - Implement Role-Based Navigation (60 min)
```

### **Agent Team B: Templates**
```bash
phase-01-branding/task_012.txt - Update Announcements (20 min)
phase-01-branding/task_013.txt - Update Home Page (30 min)
```

### **Agent Team C: Content**
```bash
phase-01-branding/task_014.txt - Update Page Titles (20 min)
```

**Phase 1 Duration if parallel:** 2-3 hours
**Phase 1 Duration if sequential:** 3-4 hours

---

## 🎯 **Recommended First Day Execution**

### **Session 1: Morning (2 hours) - PARALLEL**

Launch 3 terminal windows simultaneously:

**Terminal 1 - Safety Net:**
```bash
cd /Users/saidamenmambayao/apps/madaris-ms
cat docs/docs-new/tasks-refactor/phase-01-branding/task_001.txt
# Follow steps to create database backup
```

**Terminal 2 - Git Safety:**
```bash
cd /Users/saidamenmambayao/apps/madaris-ms
cat docs/docs-new/tasks-refactor/phase-01-branding/task_003.txt
# Create git tag
git add .
git commit -m "Pre-Tarbiyyah refactoring snapshot"
git tag -a v1.0-pre-tarbiyyah -m "Pre-Tarbiyyah Management System refactoring"
git push origin v1.0-pre-tarbiyyah
```

**Terminal 3 - Documentation:**
```bash
cd /Users/saidamenmambayao/apps/madaris-ms
cat docs/docs-new/tasks-refactor/phase-01-branding/task_005.txt
# Create rollback plan documentation
```

### **Session 2: Afternoon (3 hours) - PARALLEL**

After morning tasks complete, launch Phase 1:

**Terminal 1 - Backend:**
```bash
# task_007: Context Processor
cd /Users/saidamenmambayao/apps/madaris-ms/src

# Create context processor
cat > config/context_processors.py << 'EOF'
def tarbiyyah_branding(request):
    return {
        'SITE_NAME': 'Tarbiyyah Management System',
        'SITE_NAME_SHORT': 'TMS',
        'MADRASAH_LABEL': 'Madrasah',
        'STUDENT_LABEL': 'Student',
        'TEACHER_LABEL': 'Asatidz',
        'ORGANIZATION': 'BARMM - Ministry of Basic, Higher, and Technical Education',
    }
EOF

# Add to settings
# Edit config/settings/base.py to add context processor
```

**Terminal 2 - Static Assets:**
```bash
# task_008-010: Update static files and navigation
cd /Users/saidamenmambayao/apps/madaris-ms/src/static

# Update logos, manifests, implement role-based navigation
# Follow task instructions in phase-01-branding/
```

**Terminal 3 - Templates:**
```bash
# task_012-014: Update templates
cd /Users/saidamenmambayao/apps/madaris-ms/src/templates

# Update announcements, home page, page titles
# Follow task instructions in phase-01-branding/
```

---

## ✅ **Immediate Visual Results**

After completing these tasks, you'll see:

1. ✅ **Browser Tab** - "Tarbiyyah Management System" instead of "BM Parliament"
2. ✅ **Site Header** - New branding and logo
3. ✅ **Navigation** - Updated menu items
4. ✅ **Home Page** - Tarbiyyah-focused content
5. ✅ **PWA Icon** - New app icon when installed

**Zero database changes** - completely safe!

---

## ⚠️ **Tasks to AVOID for Now**

These require database migrations - save for later:

- ❌ phase-02-roles/task_016-025 (Phase 2: Roles) - Modifies User model
- ❌ phase-03-madaris/task_026+ (Phase 3: Models) - Renames database tables
- ❌ phase-04-teachers/task_046+ (Phase 4+: New Apps) - Creates new models

**Wait until Phase 1 is complete and tested before touching these.**

---

## 📊 **Progress Tracking**

Create a file to track progress:

```bash
cat > /Users/saidamenmambayao/apps/madaris-ms/docs/docs-new/tasks-refactor/PROGRESS.md << 'EOF'
# Tarbiyyah Refactoring Progress

## Day 1: Non-Destructive Changes

### Morning Session (2 hours)
- [ ] task_001 - Database Backup
- [ ] task_002 - Media Backup
- [ ] task_003 - Git Tag
- [ ] task_005 - Rollback Plan

### Afternoon Session (3 hours)
- [ ] task_007 - Context Processor
- [ ] task_008 - PWA Manifest
- [ ] task_009 - Logos/Favicons
- [ ] task_010 - CSS Branding
- [ ] task_011 - Base Template
- [ ] task_012 - Navigation
- [ ] task_013 - Home Page
- [ ] task_014 - Page Titles

## Overall Progress: 0/14 tasks complete (0%)
EOF
```

---

## 🚀 **Recommended: Start with phase-01-branding/task_001**

This is the MOST IMPORTANT task:

```bash
# 1. Check database size
psql -d madaris_dev -c "SELECT pg_size_pretty(pg_database_size('madaris_dev'));"

# 2. Create backup
pg_dump madaris_dev > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Compress
gzip backup_*.sql

# 4. Verify
ls -lh backup_*.sql.gz

# 5. Test restore on different database
createdb madaris_test_restore
gunzip -c backup_*.sql.gz | psql madaris_test_restore
psql madaris_test_restore -c "SELECT COUNT(*) FROM chapters_chapter;"
dropdb madaris_test_restore
```

**Once phase-01-branding/task_001 is done, you can proceed with confidence!**

---

## 🎯 **Expected Outcome After Day 1**

After completing these 14 tasks:

✅ **Safety:**
- Full database backup exists
- Git tag created for rollback
- Rollback plan documented

✅ **Visible Changes:**
- Site name updated everywhere
- New branding/logos visible
- Templates updated with Tarbiyyah terminology
- No broken functionality

✅ **Ready for Phase 2:**
- Safe to proceed with database changes
- Confidence that rollback is possible
- Team can see progress

---

## ⏱️ **Time Estimate**

**Sequential:** 7-11 hours
**Parallel (3 terminals):** 4-5 hours

**Recommendation:** Use parallel execution to see results faster!

---

## 🔄 **After Phase 1 Complete**

Test everything:

```bash
# 1. Run Django checks
python manage.py check

# 2. Run tests
python manage.py test

# 3. Start development server
python manage.py runserver

# 4. Open browser and verify:
# - http://localhost:8000 - Home page loads
# - Site name shows "Tarbiyyah Management System"
# - Navigation updated
# - No console errors
```

If all tests pass, **Phase 1 is complete!** ✅

Then review progress with stakeholders before proceeding to Phase 2 (database changes).

---

**Ready to start?** Begin with `phase-01-branding/task_001.txt` - database backup! 🚀

---

## 📁 **New Task Organization**

All tasks are now organized in phase subdirectories:

- **phase-01-branding/** - Pre-Implementation + Phase 1 (Branding & Configuration)
- **phase-02-roles/** - Phase 2 (User Roles)
- **phase-03-madaris/** - Phase 3 (Madaris Management)
- **phase-04-teachers/** - Phase 4 (Teachers/Asatidz)
- **phase-05-curriculum/** - Phase 5 (Curriculum) - Tasks to be created
- **phase-06-student/** - Phase 6 (Student Model) - Tasks to be created
- **phase-07-academic/** - Phase 7 (Academic Records) - Tasks to be created
- **phase-08-programs/** - Phase 8 (Programs Adaptation) - Tasks to be created
- **phase-09-parent/** - Phase 9 (Parent Portal) - Tasks to be created
- **phase-10-adapt/** - Phase 10 (Adaptation) - Tasks to be created
- **phase-11-forms/** - Phase 11 (Forms) - Tasks to be created
- **phase-12-templates/** - Phase 12 (Templates) - Tasks to be created
- **phase-13-database/** - Phase 13 (Database Cleanup) - Tasks to be created
- **phase-14-frontend/** - Phase 14 (Next.js Frontend - DEFERRED)
