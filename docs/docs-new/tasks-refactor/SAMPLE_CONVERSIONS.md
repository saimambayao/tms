# Sample Task Conversions - Before & After

## Sample 1: Simple Task with No Dependencies

### BEFORE (Current Format)
```markdown
# Task 008: Update PWA Manifest

## Phase: Phase 1 - Branding & Configuration

## Status: pending

## Dependencies:
None - Can start immediately after context processor

## Description:
Update the Progressive Web App (PWA) manifest to reflect new Tarbiyyah branding. This ensures the app icon and name are correct when installed on mobile devices.

## Acceptance Criteria:
- [ ] manifest.json updated with new app name
- [ ] App icon changed to Tarbiyyah logo
- [ ] Theme colors updated to match branding
- [ ] manifest.json validates successfully
- [ ] PWA installable on mobile (test in Chrome DevTools)

## Steps:
1. Open public/manifest.json
2. Update "name" field: "Tarbiyyah Management System"
3. Update "short_name": "TMS"
4. Update icon path to new logo: "icons/tarbiyyah-logo-192.png"
5. Update theme colors: primary #1a5f7a, secondary #e8b4b8
6. Validate manifest against spec
7. Test PWA installation

## Files Affected:
- public/manifest.json (update)
- public/icons/tarbiyyah-logo-192.png (new)
- public/icons/tarbiyyah-logo-512.png (new)

## Notes:
- Icon should be square PNG, minimum 192x192px
- Use official Tarbiyyah logo provided by stakeholders
- Test on actual mobile device if possible
- Estimate: 20 minutes
```

### AFTER (taskmaster-ai Format)
```markdown
# Task ID: 008
# Title: Update PWA Manifest
# Status: pending
# Dependencies: 007
# Priority: medium
# Description: Update the Progressive Web App manifest for Tarbiyyah branding.

# Details:
Update the Progressive Web App (PWA) manifest to reflect new Tarbiyyah branding. This ensures the app icon and name are correct when installed on mobile devices.

## Implementation Steps:
1. Navigate to: `public/manifest.json`
2. Update "name" field: `"Tarbiyyah Management System"`
3. Update "short_name": `"TMS"`
4. Update icon paths to new logo:
   ```json
   "icons": [
     {
       "src": "/icons/tarbiyyah-logo-192.png",
       "sizes": "192x192",
       "type": "image/png"
     },
     {
       "src": "/icons/tarbiyyah-logo-512.png",
       "sizes": "512x512",
       "type": "image/png"
     }
   ]
   ```
5. Update theme colors:
   ```json
   "theme_color": "#1a5f7a",
   "background_color": "#ffffff"
   ```
6. Validate manifest against PWA spec

## Acceptance Criteria:
- manifest.json updated with app name "Tarbiyyah Management System"
- App icon changed to official Tarbiyyah logo
- Theme colors updated to match branding (#1a5f7a primary)
- manifest.json validates against official spec
- PWA installable on mobile device (verified in Chrome DevTools)

## Files Modified:
- `public/manifest.json` (modified)
- `public/icons/tarbiyyah-logo-192.png` (new - square PNG, 192x192px minimum)
- `public/icons/tarbiyyah-logo-512.png` (new - square PNG, 512x512px)

## Important Notes:
- Icon must be square PNG format
- Minimum resolution: 192x192px (192 icon) and 512x512px (512 icon)
- Use official Tarbiyyah logo provided by stakeholders
- Theme color should match primary brand color (#1a5f7a)
- Estimated time: 20 minutes
- Non-destructive change (no database modifications)

# Test Strategy:
1. Open `public/manifest.json` and validate JSON syntax
2. Verify all icon paths are correct
3. Check Chrome DevTools (Application > Manifest) to ensure manifest loads without errors
4. Test PWA installation on Chrome/Edge (mobile or emulated):
   - Open DevTools > Application > Install
   - Verify app installs with correct name and icon
5. Open installed app and verify branding is correct
6. Success: PWA installs with "Tarbiyyah Management System" name and correct logo
```

---

## Sample 2: Task with Multiple Dependencies

### BEFORE (Current Format)
```markdown
# Task 020: Add Tarbiyyah Roles Migration

## Phase: Phase 2 - User Roles Extension

## Status: pending

## Dependencies:
- task_015.txt (Phase 1 verification complete)
- task_016.txt (Role choices added)
- task_018.txt (Permission groups created)

## Description:
Create database migration to add new Tarbiyyah roles. This migration is the bridge between the role models and the database state.

## Acceptance Criteria:
- [ ] Migration file created in proper location
- [ ] Migration adds TARBIYYAH_ADMIN role
- [ ] Migration adds MADRASAH_ADMIN role
- [ ] Migration adds MUDER role
- [ ] Migration adds ASATIDZ role
- [ ] Migration adds STUDENT role
- [ ] Migration adds PARENT role
- [ ] Migration is reversible
- [ ] Migration tested and verified

## Steps:
1. Create migration: python manage.py makemigrations users
2. Review migration file
3. Test forward migration
4. Test reverse migration
5. Document in MIGRATION_LOG.md

## Files Affected:
- src/apps/users/migrations/000X_tarbiyyah_roles.py (new)
- MIGRATION_LOG.md (update)

## Notes:
- Estimate: 45 minutes
- Database must be backed up before running
```

### AFTER (taskmaster-ai Format)
```markdown
# Task ID: 020
# Title: Add Tarbiyyah Roles Migration
# Status: pending
# Dependencies: 015, 016, 018
# Priority: high
# Description: Create database migration for new Tarbiyyah roles.

# Details:
Create database migration to add new Tarbiyyah roles. This migration bridges the role models defined in task_016 with the database state. Must be run after role choices are added to the User model.

## Implementation Steps:
1. Ensure task_016 is complete (Role choices added to User model)
2. Generate migration file:
   ```bash
   cd /Users/saidamenmambayao/apps/madaris-ms
   python manage.py makemigrations users
   ```
3. Review the generated migration file in `src/apps/users/migrations/00XX_*.py`
4. The migration should reflect role choice additions from task_016
5. Test forward migration:
   ```bash
   python manage.py migrate users --database=default
   ```
6. Test reverse migration:
   ```bash
   python manage.py migrate users zero
   python manage.py migrate users
   ```
7. Verify in Django shell:
   ```python
   from apps.users.models import User
   roles = [choice[0] for choice in User.Role.choices]
   print(roles)  # Should include all new Tarbiyyah roles
   ```
8. Document migration in MIGRATION_LOG.md

## Acceptance Criteria:
- Migration file created in `src/apps/users/migrations/`
- Migration is properly numbered and named
- Forward migration executes without errors
- Reverse migration executes without errors
- All role choices properly defined in database
- No data loss in forward/reverse migrations
- Django checks pass: `python manage.py check`

## Files Modified:
- `src/apps/users/migrations/000X_add_tarbiyyah_roles.py` (new migration file)
- `MIGRATION_LOG.md` (updated with migration details)

## Important Notes:
- **CRITICAL**: Task_015 (Phase 1 verification) must be complete
- **CRITICAL**: Task_016 (role choices) must be complete before running
- **CRITICAL**: Database must have backup from task_001
- Migration is reversible - allows safe rollback
- Do not manually edit migration file
- Estimated time: 45 minutes
- Database operation - requires downtime coordination

# Test Strategy:
1. Verify migration file syntax with:
   ```bash
   python manage.py sqlmigrate users 000X
   ```
2. Test on development database (already has backup)
3. Test forward migration - should complete without errors
4. Test reverse migration - should restore previous state
5. Verify in Django shell that all roles are available
6. Run full test suite: `python manage.py test`
7. Verify no regressions in user-related functionality
8. Success: Migration is reversible and preserves data integrity
```

---

## Sample 3: Complex Task with Multi-step Dependencies

### BEFORE (Current Format)
```markdown
# Task 035: Refactor Student Model with New Fields

## Phase: Phase 6 - Student Model

## Status: pending

## Dependencies:
- task_001.txt (database backup)
- task_015.txt (Phase 1 verification)
- task_020.txt (Tarbiyyah roles complete)
- task_033.txt (Madrasah model finalized)
- task_034.txt (Academic year setup)

## Description:
Add new fields to Student model for Tarbiyyah system: enrollment_date, graduation_date, parent_contact, emergency_contact, health_info. Create data migration to populate defaults.

## Acceptance Criteria:
- [ ] New fields added to Student model
- [ ] Data migration created
- [ ] Existing student data preserved
- [ ] Django migrations run successfully
- [ ] Admin interface updated for new fields
- [ ] Tests updated
- [ ] No data loss

## Steps:
1. Backup database (task_001)
2. Add fields to model
3. Create migration
4. Create data migration
5. Test migrations
6. Update admin
7. Update forms
8. Run tests

## Files Affected:
- src/apps/students/models.py
- src/apps/students/admin.py
- src/apps/students/forms.py
- src/apps/students/migrations/000X_*.py
- tests/test_students.py

## Notes:
- Estimate: 2-3 hours
- Multiple migrations needed
- Data migration required
```

### AFTER (taskmaster-ai Format)
```markdown
# Task ID: 035
# Title: Refactor Student Model with New Fields
# Status: pending
# Dependencies: 001, 015, 020, 033, 034
# Priority: high
# Description: Add new fields to Student model for Tarbiyyah system including enrollment tracking and guardian information.

# Details:
Add comprehensive fields to Student model for Tarbiyyah system: enrollment_date, graduation_date, parent_contact, emergency_contact, and health_info. Includes data migration to safely populate defaults for existing students. This task depends on completion of core models (Madrasah in 033) and academic year setup (034).

## Implementation Steps:
1. **Verify prerequisites:**
   - Confirm task_001 (backup) is complete
   - Confirm task_033 (Madrasah model) is done
   - Confirm task_034 (Academic year setup) is done

2. **Update Student model:**
   ```python
   # In src/apps/students/models.py
   class Student(models.Model):
       # ... existing fields ...
       
       enrollment_date = models.DateField(
           null=True, blank=True,
           help_text="Date student enrolled in the institution"
       )
       graduation_date = models.DateField(
           null=True, blank=True,
           help_text="Expected or actual graduation date"
       )
       parent_contact = models.JSONField(
           default=dict, blank=True,
           help_text="Primary guardian contact information"
       )
       emergency_contact = models.JSONField(
           default=dict, blank=True,
           help_text="Emergency contact information"
       )
       health_info = models.TextField(
           blank=True,
           help_text="Medical conditions, allergies, special needs"
       )
   ```

3. **Create database migration:**
   ```bash
   cd /Users/saidamenmambayao/apps/madaris-ms
   python manage.py makemigrations students
   ```

4. **Create data migration for default values:**
   ```bash
   python manage.py makemigrations students --name populate_student_defaults --empty
   ```
   
   In the generated data migration, set defaults for existing students.

5. **Test migrations on staging:**
   ```bash
   python manage.py migrate students --database=staging
   ```

6. **Update Django admin (src/apps/students/admin.py):**
   ```python
   @admin.register(Student)
   class StudentAdmin(admin.ModelAdmin):
       list_display = ['name', 'enrollment_date', 'graduation_date']
       fieldsets = (
           ('Basic Info', {'fields': ('user', 'madrasah')}),
           ('Enrollment', {'fields': ('enrollment_date', 'graduation_date')}),
           ('Contact Info', {'fields': ('parent_contact', 'emergency_contact')}),
           ('Health', {'fields': ('health_info',)}),
       )
   ```

7. **Update Student form (src/apps/students/forms.py)** if applicable

8. **Update tests (tests/test_students.py):**
   - Test new fields are saved correctly
   - Test data migration preserves existing data
   - Test admin displays new fields

## Acceptance Criteria:
- All new fields added to Student model in `src/apps/students/models.py`
- Data migration created and tested successfully
- Existing student data preserved during migration
- Django migration runs without errors: `python manage.py migrate`
- Admin interface shows new fields (enrollment_date, graduation_date, contacts, health_info)
- Form validation works for new fields
- All unit tests pass
- No data loss in production migration
- Admin list/detail views properly formatted

## Files Modified:
- `src/apps/students/models.py` (add new Student fields)
- `src/apps/students/migrations/000X_add_student_fields.py` (new schema migration)
- `src/apps/students/migrations/000Y_populate_student_defaults.py` (new data migration)
- `src/apps/students/admin.py` (update admin interface)
- `src/apps/students/forms.py` (update form fields if applicable)
- `tests/test_students.py` (add tests for new fields)

## Important Notes:
- **BLOCKING**: Requires task_033 (Madrasah model) to be complete
- **BLOCKING**: Requires task_034 (Academic year) to be complete
- **CRITICAL**: Ensure backup from task_001 exists before running
- This is a schema-changing migration - requires downtime coordination
- Data migration must handle NULL values for existing records
- Parent/emergency contact info stored as JSON for flexibility
- Health info stored as text field for sensitive information
- Estimated time: 2-3 hours
- Risk level: MEDIUM (modifies Student table structure)

# Test Strategy:
1. **Pre-migration verification:**
   ```bash
   python manage.py makemigrations --dry-run --verbosity 3
   python manage.py sqlmigrate students [migration_number]
   ```

2. **Test on staging database:**
   ```bash
   python manage.py migrate students --database=staging
   ```

3. **Verify migration reversibility:**
   ```bash
   python manage.py migrate students [previous_migration]
   python manage.py migrate students
   ```

4. **Test in Django shell:**
   ```python
   from apps.students.models import Student
   s = Student.objects.first()
   assert hasattr(s, 'enrollment_date')
   assert hasattr(s, 'parent_contact')
   print("All fields present and accessible")
   ```

5. **Test admin interface:**
   - Open Django admin > Students
   - Verify new fields visible in list and detail views
   - Create/edit student with new fields
   - Verify data saves correctly

6. **Run full test suite:**
   ```bash
   python manage.py test
   python manage.py test tests.test_students -v 2
   ```

7. **Success criteria:**
   - All migrations execute forward and backward successfully
   - No data loss
   - Admin interface fully functional
   - All tests pass
   - Student records have proper default values for new fields
```

---

## Conversion Checklist

When converting a task, ensure:

- [ ] **Task ID**: Extract number only (001, not Task 001)
- [ ] **Title**: Move description from first line
- [ ] **Status**: Keep original status (pending/in_progress/done)
- [ ] **Dependencies**: Convert to comma-separated format (none if no dependencies)
- [ ] **Priority**: Assign based on blocking status and impact
- [ ] **Description**: Keep brief, one-sentence summary
- [ ] **Details**: Consolidate all implementation content:
  - Step-by-step instructions
  - Code snippets where relevant
  - Acceptance criteria as bullet points
  - Files being modified
  - Important notes and gotchas
- [ ] **Test Strategy**: Create new section with:
  - Verification steps
  - How to test functionality
  - How to reverse/rollback if needed
  - Success criteria

## Priority Assignment Guide

| Criteria | Priority | Examples |
|----------|----------|----------|
| Blocks multiple other tasks | **high** | Database backups, core model changes, role setup |
| Required for one phase to complete | **medium** | UI updates, config changes, documentation |
| Enhancement/optional | **low** | Performance optimization, nice-to-have features |
| Database schema change | **high** | Migrations, model modifications |
| Non-destructive change | **medium** | Templates, static assets, documentation |
| Parallel-safe tasks | **medium** | Unrelated UI changes, documentation |

