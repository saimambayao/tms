# Phase 2 - User Roles & Permissions

## Status: Ready for Implementation

## Tasks: 10 files (016-025)

### Overview
This phase extends the User model with education-specific roles and implements role-based permissions. **First phase with database changes** - requires migration.

### Task List

**Model Extension (016-018):**
- task_016.txt - Add Role Choices to User Model
- task_017.txt - Create User Role Migration
- task_018.txt - Run Migration and Verify

**Permission System (019-020):**
- task_019.txt - Create Role Permission Mappings
- task_020.txt - Implement Role-Based Access Control

**Templates & UI (021-022):**
- task_021.txt - Update Templates for Role-Based Display
- task_022.txt - Create Role Selection Interface

**Testing & Data (023-025):**
- task_023.txt - Write Role-Based Tests
- task_024.txt - Create User Fixtures with Roles
- task_025.txt - Verify Phase 2 Roles Complete

### User Roles Implemented

1. **TARBIYYAH_ADMIN** - System-wide Tarbiyyah Committee administrator
2. **MADRASAH_ADMIN** - Madrasah administrator (school principal)
3. **MUDER** (مدير) - Madrasah director
4. **ASATIDZ** (أساتذة) - Teacher/Instructor
5. **STUDENT** - Enrolled student
6. **PARENT** - Parent/Guardian

### Dependencies
- **Required:** Phase 1 (Branding) must be complete
- **Specifically:** task_010.txt (Role-based navigation structure) must be done

### Risk Level: MEDIUM
- **Database migration required** - User model modification
- **Reversible** via migration rollback
- **Non-destructive** - Extends model, doesn't delete data

### Timeline Estimate
- **Sequential:** 10-15 hours
- **Parallel (after migration):** 4-5 hours

### Migration Strategy

**Sequential Part (MUST be done first):**
1. task_016: Add role field to User model
2. task_017: Generate migration
3. task_018: Run migration, verify

**Parallel Part (After migration complete):**
- 4 agents working on tasks 019-024 simultaneously

### Notes
- **User model extension** - Adding role field, not replacing User model
- **Preserves existing users** - Existing users get default role
- **Role-based navigation** from Phase 1 will now function properly
- **Permission mappings** align with Django's built-in permissions
- **Multitenant support** - Roles scoped by madrasah

### Completion Criteria
- [ ] User model has role field
- [ ] Migration created and run successfully
- [ ] All 6 roles defined as choices
- [ ] Permission mappings created
- [ ] Role-based access control implemented
- [ ] Templates show/hide based on role
- [ ] Role selection interface working
- [ ] Tests pass for all roles
- [ ] User fixtures created with sample roles
- [ ] task_025 verification passed

---

**Status: Ready to begin with task_016.txt (Add Role Choices)**

**⚠️ IMPORTANT:** This phase includes database migrations. Ensure Phase 1 backups are complete before starting.
