# Phase 3 - Madaris Management (Full Transition)

## Status: Ready for Implementation

## Tasks: 20 files (026-045)

### Overview
This phase performs the **complete transition from Chapter to Madrasah** model. This is the core refactoring that transforms the parliamentary system into an education management system.

### Task List

**Madrasah Model (026-036):**
- task_026.txt - Plan Madrasah Model Migration Strategy
- task_027.txt - Create Madrasah Model (rename from Chapter)
- task_028.txt - Add Education-Specific Fields
- task_029.txt - Create Madrasah Type Choices (Ibtidaiyyah, I'dadiyyah, Thanawiyyah, Kulliyah)
- task_030.txt - Add Accreditation Fields
- task_031.txt - Add Location/Region Fields
- task_032.txt - Create Data Migration Script
- task_033.txt - Run Madrasah Migration
- task_034.txt - Update Foreign Key References
- task_035.txt - Verify Data Integrity
- task_036.txt - Update Madrasah Admin Interface

**Enrollment Model (037-039):**
- task_037.txt - Create MadrasahEnrollment Model (rename from ChapterMembership)
- task_038.txt - Migrate Enrollment Data
- task_039.txt - Update Enrollment Admin

**Activity Model (040-042):**
- task_040.txt - Create MadrasahActivity Model (rename from ChapterActivity)
- task_041.txt - Migrate Activity Data
- task_042.txt - Update Activity Admin

**Integration (043-045):**
- task_043.txt - Update Madaris URLs and Views
- task_044.txt - Update Madaris Templates
- task_045.txt - Verify Phase 3 Complete

### Key Transformations

**Model Renaming:**
- `Chapter` → `Madrasah` (مدرسة)
- `ChapterMembership` → `MadrasahEnrollment`
- `ChapterActivity` → `MadrasahActivity`

**New Fields Added:**
- `madrasah_type` - Ibtidaiyyah, I'dadiyyah, Thanawiyyah, Kulliyah
- `accreditation_status` - MBHTE accreditation level
- `accreditation_date` - Last accreditation date
- `student_capacity` - Maximum enrollment
- `region`, `municipality`, `barangay` - Location details
- `principal_name`, `principal_contact` - Leadership info

**URL Changes:**
- `/chapters/` → `/madaris/`
- `/chapter/<id>/` → `/madrasah/<id>/`

### Dependencies
- **Required:** Phase 2 (User Roles) must be complete
- **Required:** Phase 1 (Branding) must be complete
- **Specifically:** Database backups from Phase 1 must exist

### Risk Level: HIGH
- **Database table renaming** - Most critical migration
- **Data migration** - All Chapter data must transfer to Madrasah
- **Foreign key updates** - Many tables reference Chapter
- **Reversible** via rollback plan, but complex

### Timeline Estimate
- **Sequential:** 20-30 hours
- **Parallel (3 branches):** 6-8 hours
  - Branch 1: Madrasah model (026-036)
  - Branch 2: Enrollment model (037-039)
  - Branch 3: Activity model (040-042)
  - Merge: Integration tasks (043-045)

### Migration Strategy

**Branch-Based Parallelization:**
1. Create 3 feature branches
2. Each branch handles one model transition
3. Merge branches sequentially
4. Run integration tasks

**Data Preservation:**
- All existing Chapter data → Madrasah
- No data loss
- Preserve relationships
- Update all foreign keys

### Notes
- **Most critical phase** - Core system transformation
- **Extensive testing required** after completion
- **Rollback plan essential** before starting
- **Coordinate with stakeholders** before migration
- **Downtime may be required** for production migration

### Completion Criteria
- [ ] Madrasah model created and migrated
- [ ] All Chapter data transferred to Madrasah
- [ ] Education-specific fields populated
- [ ] Enrollment model renamed and migrated
- [ ] Activity model renamed and migrated
- [ ] All foreign keys updated
- [ ] Data integrity verified (no orphaned records)
- [ ] Admin interfaces updated
- [ ] URLs working (/madaris/)
- [ ] Views updated
- [ ] Templates updated
- [ ] No references to "Chapter" in user-facing pages
- [ ] task_045 verification passed

---

**Status: Ready to begin with task_026.txt (Plan Migration Strategy)**

**⚠️ CRITICAL:** This phase includes major database changes. Ensure:
1. Full database backup exists (task_001 complete)
2. Rollback plan documented (task_005 complete)
3. Stakeholder approval obtained
4. Consider maintenance window for production
