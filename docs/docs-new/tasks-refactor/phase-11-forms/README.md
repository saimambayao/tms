# Phase 11 - Forms Cleanup

## Status: Tasks Created - Ready for Implementation

## Tasks: 6 tasks (task_111.txt - task_116.txt)

### Overview
This phase updates all Django forms to use education terminology and validation:
- ModelForm updates with madrasah/student terminology
- Education-specific validation rules
- Custom widgets for enhanced UX
- Form accessibility improvements (WCAG 2.1)

### Task List:

#### task_111.txt - Audit All ModelForms for Terminology
- **Status**: pending
- **Duration**: 2-3 hours
- **Description**: Audit all forms.py files to identify terminology updates needed
- **Deliverables**: Forms audit document, terminology mapping, priority list
- **Dependencies**: Phase 10 complete

#### task_112.txt - Update Form Field Labels and Help Text
- **Status**: pending
- **Duration**: 2-3 hours
- **Description**: Update all form labels, placeholders, and help text to education terminology
- **Deliverables**: Updated ChapterForm, MembershipForm, BMParliamentMemberRegistrationForm, UserRegistrationForm
- **Dependencies**: task_111.txt

#### task_113.txt - Add Education-Specific Validation
- **Status**: pending
- **Duration**: 3-4 hours
- **Description**: Create custom validators for school codes, student numbers, ages, phone numbers
- **Deliverables**: apps/core/validators.py with 10+ validators, unit tests
- **Dependencies**: task_112.txt

#### task_114.txt - Create Custom Form Widgets
- **Status**: pending
- **Duration**: 4-5 hours
- **Description**: Build custom widgets for date pickers, photo upload, cascading selects, Arabic input
- **Deliverables**: apps/core/widgets.py with 8+ widgets, templates, JavaScript
- **Dependencies**: task_113.txt

#### task_115.txt - Update Form Error Messages
- **Status**: pending
- **Duration**: 2-3 hours
- **Description**: Create clear, contextual error messages for all form validations
- **Deliverables**: apps/core/error_messages.py with 50+ messages, error templates
- **Dependencies**: task_114.txt

#### task_116.txt - Verify Phase 11 Complete
- **Status**: pending
- **Duration**: 2-3 hours
- **Description**: Comprehensive verification of all form updates, testing, and documentation
- **Deliverables**: Verification checklist, testing report, completion documentation
- **Dependencies**: tasks 111-115 complete

### Total Estimated Time: 15-21 hours

### Key Features:
- **Validators**: School code (MAD-XXX-###), student number, age-grade matching, Philippine phone numbers
- **Widgets**: Islamic date picker, cascading province-municipality selects, photo upload with preview, Arabic RTL input
- **Error Messages**: 50+ contextual, actionable error messages in education terminology
- **Accessibility**: WCAG 2.1 AA compliance, keyboard navigation, screen reader support

### Files to be Created/Modified:
**New Files:**
- `src/apps/core/validators.py` - Custom validation functions
- `src/apps/core/widgets.py` - Enhanced form widgets
- `src/apps/core/error_messages.py` - Error message definitions
- `src/apps/core/tests/test_validators.py` - Validator unit tests
- `src/templates/widgets/` - Widget templates (5+ files)
- `src/static/js/` - Widget JavaScript files (5+ files)
- `src/static/css/` - Widget styles (3+ files)
- `docs/docs-new/tasks-refactor/phase-11-forms/audit/` - Audit documents

**Modified Files:**
- `src/apps/chapters/forms.py` - ChapterForm (madrasah registration)
- `src/apps/constituents/forms.py` - BMParliamentMemberRegistrationForm (student registration)
- `src/apps/users/forms.py` - UserRegistrationForm
- `src/apps/services/forms.py` - Program application forms
- `src/apps/documents/forms.py` - Document forms
- `src/apps/notifications/forms.py` - Notification forms

### Dependencies:
- **Requires**: Phase 10 (Adaptation) complete
- **Blocks**: Phase 12 (Templates) - templates need updated form context

### Success Criteria:
- [ ] All forms use education terminology (no "BM Parliament" references)
- [ ] Custom validators functioning for all education-specific fields
- [ ] Custom widgets enhance UX (date pickers, photo upload, cascading selects)
- [ ] Error messages clear, contextual, and actionable
- [ ] Forms accessible (WCAG 2.1 AA)
- [ ] Cross-browser testing passed (Chrome, Firefox, Safari)
- [ ] Mobile responsive forms verified
- [ ] Unit tests pass for all validators
- [ ] Documentation complete

### Testing Requirements:
1. **Unit Tests**: Validator tests (apps/core/tests/test_validators.py)
2. **Browser Tests**: Chrome, Firefox, Safari (desktop)
3. **Mobile Tests**: iOS Safari, Chrome Mobile
4. **Accessibility Tests**: Keyboard navigation, screen reader compatibility
5. **User Tests**: Validate terminology clarity with stakeholders

### Notes:
- Forms will work with existing models (Chapter, BMParliamentMember) during Phase 11
- Forms will be fully compatible with renamed models after Phase 3 and Phase 6 complete
- JavaScript for widgets is unobtrusive and uses progressive enhancement
- All error messages support Django i18n for future translations
- Widget styling uses Tailwind CSS utility classes
- Photo upload validates file size (5MB) and format (JPG/PNG) client-side
- Cascading selects improve address entry UX (province → municipality)
- Islamic date display helps users familiar with Hijri calendar
- Arabic input supports RTL text direction automatically

### Risk Assessment: LOW
- **Complexity**: Medium - involves validation logic and custom widgets
- **Data Impact**: None - no database changes in this phase
- **User Impact**: High positive - improved form UX and clarity
- **Rollback**: Easy - can revert form changes without data loss

---

**Tasks created**: November 20, 2025
**Created by**: Claude Code Agent
**Ready for**: Parallel execution by development team
