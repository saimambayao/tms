# Phase 4 - Asatidz (Teachers) Management

## Status: Ready for Implementation

## Tasks: 5 files (046-050)

### Overview
This phase creates the teachers management app, establishing the foundation for teacher assignments, curriculum delivery, and academic management.

### Task List

- task_046.txt - Create Asatidz (Teachers) App
- task_047.txt - Create Teacher Model and Fields
- task_048.txt - Create Teacher Assignment Model
- task_049.txt - Create Teacher Admin Interface
- task_050.txt - Verify Phase 4 Complete

### Features Implemented

**Teacher Management:**
- Teacher profiles with Islamic education credentials
- Teacher-to-Madrasah assignments
- Subject specializations
- Teaching certificates and qualifications

**Model Structure:**
- `Teacher` model - Core teacher information
- `TeacherAssignment` model - Links teachers to madaris and subjects
- Integration with User model (ASATIDZ role)
- Support for multiple madrasah assignments

**Admin Interface:**
- Teacher CRUD operations
- Assignment management
- Qualification tracking
- Teacher search and filtering

### Dependencies
- **Required:** Phase 3 (Madaris) must be complete
- **Required:** Phase 2 (User Roles - ASATIDZ role) must be complete
- **Specifically:** Madrasah model must exist for teacher assignments

### Risk Level: LOW
- **New app creation** - No modification of existing models
- **Additive changes only** - No data migration needed
- **Reversible** - Can be removed if needed

### Timeline Estimate
- **Sequential:** 6-8 hours
- **Parallel:** Not applicable (small phase, sequential is fine)

### Key Models

**Teacher Model:**
```python
class Teacher(models.Model):
    user = OneToOneField(User)  # Link to ASATIDZ user
    employee_id = CharField
    specialization = CharField
    qualifications = TextField
    hire_date = DateField
    is_active = BooleanField
```

**TeacherAssignment Model:**
```python
class TeacherAssignment(models.Model):
    teacher = ForeignKey(Teacher)
    madrasah = ForeignKey(Madrasah)
    subject = CharField
    grade_levels = JSONField
    assignment_date = DateField
    is_primary_madrasah = BooleanField
```

### Integration Points

**With Phase 2 (Roles):**
- Teacher accounts use ASATIDZ role
- Permission checks for teacher-specific features

**With Phase 3 (Madaris):**
- Teachers assigned to specific madaris
- Madrasah-scoped teacher management

**With Future Phases:**
- Phase 5: Teachers assigned to curriculum/subjects
- Phase 6: Teachers linked to student records
- Phase 7: Teachers manage grades and attendance

### Notes
- **"Asatidz" (أساتذة)** is Arabic for "teachers/professors"
- **Multi-madrasah support** - Teachers can teach at multiple madaris
- **Islamic education focus** - Tracks Islamic qualifications (Ijazah, etc.)
- **Foundation for curriculum** - Sets up teacher-subject relationships

### Completion Criteria
- [ ] Asatidz app created
- [ ] Teacher model implemented
- [ ] TeacherAssignment model implemented
- [ ] Admin interface working
- [ ] Teacher registration workflow functional
- [ ] Teacher-madrasah assignment working
- [ ] Integration with User model (ASATIDZ role)
- [ ] Sample teacher data created
- [ ] task_050 verification passed

---

**Status: Ready to begin with task_046.txt (Create Asatidz App)**

**Note:** This phase lays the foundation for curriculum management (Phase 5) and academic records (Phase 7).
