# #FahanieCares Portal RBAC Implementation Plan

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Role Definitions](#role-definitions)
3. [Permission Matrix](#permission-matrix)
4. [Implementation Architecture](#implementation-architecture)
5. [Technical Implementation Plan](#technical-implementation-plan)
6. [Security Considerations](#security-considerations)
7. [Testing Strategy](#testing-strategy)
8. [Migration Plan](#migration-plan)

## Executive Summary

This document outlines the comprehensive Role-Based Access Control (RBAC) implementation plan for the #FahanieCares portal. The system will provide granular access control for eight distinct user roles, ensuring secure and efficient management of constituent services, parliamentary operations, and public communications.

### Key Objectives
- Implement a secure, scalable RBAC system
- Provide role-appropriate access to portal features
- Ensure data privacy and regulatory compliance
- Enable efficient administrative management
- Support future system expansion

## Role Definitions

### 1. **Member of Parliament (MP)** - Level 9
- **Primary User**: MP Atty. Sittie Fahanie S. Uy-Oyod
- **Access Level**: Strategic oversight and decision-making
- **Key Responsibilities**:
  - View comprehensive analytics and reports
  - Strategic oversight of all operations
  - Final approval on critical decisions
  - Access to sensitive parliamentary data

### 2. **Chief of Staff** - Level 8
- **Access Level**: Operational leadership
- **Key Responsibilities**:
  - Full operational control
  - Staff management and coordination
  - Report generation and analysis
  - Workflow approval authority
  - All staff capabilities + strategic management

### 3. **System Administrator** - Level 7
- **Access Level**: Staff + Full technical portal management
- **Key Responsibilities**:
  - All base staff capabilities (task/calendar management)
  - User account management
  - System configuration and security management
  - Technical troubleshooting and database maintenance
  - Integration management

### 4. **Coordinator** - Level 6
- **Access Level**: Staff + Service management
- **Key Responsibilities**:
  - All base staff capabilities (task/calendar management)
  - Constituent registration management
  - Membership/constituent management
  - Service delivery coordination
  - Chapter operations management

### 5. **Information Officer** - Level 5
- **Access Level**: Staff + Communications management
- **Key Responsibilities**:
  - All base staff capabilities (task/calendar management)
  - Announcement creation and publishing
  - Content management and public communications
  - Media resource management
  - Newsletter management

### 6. **Parliamentary Office Staff** - Level 4 (BASE LEVEL)
- **Access Level**: Base parliamentary worker access
- **Key Responsibilities**:
  - Manage personal profile and account
  - Task management and assignment
  - Calendar management and scheduling
  - Office workflow coordination
  - Meeting and event coordination

### 7. **Chapter Members** - Level 3
- **Access Level**: Personal and chapter-specific data
- **Key Responsibilities**:
  - Manage personal profile
  - View chapter information
  - Apply for services
  - Track service requests
  - Participate in chapter activities

### 8. **Registered Users** - Level 2
- **Access Level**: Basic constituent access
- **Key Responsibilities**:
  - Manage personal profile
  - View available services
  - Apply for services
  - Track application status
  - View public announcements

### 9. **Public/Visitor** - Level 1
- **Access Level**: Public information only
- **Key Responsibilities**:
  - View public announcements
  - View available services
  - View general information
  - Access contact information
  - No personal data access

## Permission Matrix

### Core Module Permissions

| Module/Feature | MP | Chief of Staff | Admin | Coordinator | Info Officer | Staff | Chapter Member | Registered User | Public |
|----------------|----|----|-------|-------------|--------------|-------|----------------|-----------------|--------|
| **Dashboard** |
| Executive Dashboard | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Operational Dashboard | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Personal Dashboard | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Task & Calendar Management** |
| Manage Tasks | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Manage Calendar | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Schedule Coordination | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Office Workflow | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| **User Management** |
| Create Users | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Edit All Users | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Delete Users | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Assign Roles | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View User List | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Constituent Management** |
| Register Constituents | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Edit Constituents | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View All Constituents | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Export Constituent Data | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Service Management** |
| Create Services | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Edit Services | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Delete Services | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View All Services | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Apply for Services | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| **Referral Management** |
| Create Referrals | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Update Referral Status | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View All Referrals | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View Own Referrals | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Communications** |
| Create Announcements | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Edit Announcements | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Delete Announcements | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| View Announcements | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Analytics & Reports** |
| Executive Reports | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Operational Reports | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Service Analytics | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Export Reports | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **System Administration** |
| System Configuration | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Integration Management | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Security Settings | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Audit Logs | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

### Special Program Permissions

| Feature | MP | Chief of Staff | Admin | Coordinator | Info Officer | Staff | Chapter Member | Registered User | Public |
|---------|----|----|-------|-------------|--------------|-------|----------------|-----------------|--------|
| **#FahanieCares Programs** |
| Manage Programs | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Approve Applications | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View Applications | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **TDIF Projects** |
| Manage Projects | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Track Progress | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Ministry Programs** |
| Coordinate Programs | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Process Referrals | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Implementation Architecture

### 1. **Enhanced User Model**
```python
# Extension to existing User model with corrected staff-based hierarchy
USER_TYPES = (
    ('superuser', 'Superuser'),                     # Level 10 - Ultimate control
    ('mp', 'Member of Parliament'),                 # Level 9 - Strategic oversight  
    ('chief_of_staff', 'Chief of Staff'),           # Level 8 - Operational leadership
    ('admin', 'System Administrator'),              # Level 7 - Staff + Full portal management
    ('coordinator', 'Coordinator'),                 # Level 6 - Staff + Service management
    ('info_officer', 'Information Officer'),        # Level 5 - Staff + Communication management
    ('staff', 'Parliamentary Office Staff'),        # Level 4 - BASE STAFF LEVEL
    ('chapter_member', 'Chapter Member'),           # Level 3 - Chapter activities
    ('registered_user', 'Registered User'),         # Level 2 - Basic access
    ('visitor', 'Public/Visitor'),                 # Level 1 - Public only
)
```

### 2. **Permission Groups Structure (Staff-Based Inheritance)**
```
- Superuser_Group
  - Ultimate system control
  - All permissions available

- MP_Group
  - Strategic oversight permissions
  - View-only access to all data
  - No direct data manipulation

- ChiefOfStaff_Group
  - All staff base permissions (inherited)
  - Staff management permissions
  - Role assignment authority
  - Strategic workflow control

- Admin_Group (System Administrator)
  - All staff base permissions (inherited)
  - Full technical system control
  - Security and configuration management
  - Integration management

- Coordinator_Group  
  - All staff base permissions (inherited)
  - Service coordination and management
  - Constituent management
  - Chapter operations

- InfoOfficer_Group
  - All staff base permissions (inherited)
  - Communications management
  - Content creation/editing
  - Announcement publishing

- Staff_Group (Parliamentary Office Staff - BASE LEVEL)
  - Task management and assignment
  - Calendar management and scheduling
  - Office workflow coordination
  - Meeting and event management
  - Personal profile management

- ChapterMember_Group
  - Personal profile management
  - Service applications
  - Chapter participation

- RegisteredUser_Group
  - Profile management
  - Service viewing/application

- Public_Group
  - Public content viewing only
```

### 3. **Permission Naming Convention**
```
app_label.action_model

Examples:
- constituents.view_constituent
- constituents.add_constituent
- constituents.change_constituent
- constituents.delete_constituent
- referrals.approve_referral
- communications.publish_announcement
```

### 4. **Dynamic Permission System**
- Database-driven permission configuration
- Real-time permission updates
- Role inheritance hierarchy
- Context-based permissions (e.g., chapter-specific)

## Technical Implementation Plan

### Phase 1: Model Updates (Week 1)

1. **Update User Model**
```python
# apps/users/models.py
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('mp', 'Member of Parliament'),
        ('chief_of_staff', 'Chief of Staff'),
        ('admin', 'System Administrator'),
        ('coordinator', 'Coordinator'),
        ('info_officer', 'Information Officer'),
        ('chapter_member', 'Chapter Member'),
        ('registered_user', 'Registered User'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='registered_user')
    
    # Add new helper methods
    def is_chief_of_staff(self):
        return self.user_type == 'chief_of_staff'
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_info_officer(self):
        return self.user_type == 'info_officer'
```

2. **Create Permission Models**
```python
# apps/users/models.py
class DynamicPermission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
class RolePermission(models.Model):
    role = models.CharField(max_length=20, choices=User.USER_TYPE_CHOICES)
    permission = models.ForeignKey(DynamicPermission, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
```

### Phase 2: Permission System (Week 2)

1. **Enhanced Permission Classes**
```python
# apps/users/permissions.py
class EnhancedRolePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Implement role-based logic
        pass
    
    def has_object_permission(self, request, view, obj):
        # Implement object-level permissions
        pass
```

2. **Permission Decorators**
```python
# apps/users/decorators.py
def require_role(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.user.user_type in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped_view
    return decorator
```

### Phase 3: Middleware Updates (Week 3)

1. **Role-Based Middleware**
```python
# apps/users/middleware.py
class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add role context to request
        if request.user.is_authenticated:
            request.user_role = request.user.user_type
            request.role_permissions = self.get_role_permissions(request.user)
        
        response = self.get_response(request)
        return response
```

### Phase 4: View Updates (Week 4)

1. **Update all views with role-based permissions**
2. **Implement template context processors**
3. **Add role-based redirects**

### Phase 5: UI Implementation (Week 5)

1. **Role Management Interface**
   - User role assignment UI
   - Permission management dashboard
   - Audit log viewer

2. **Dynamic Navigation**
   - Role-based menu items
   - Context-aware UI elements

### Phase 6: Testing & Documentation (Week 6)

1. **Comprehensive test suite**
2. **User documentation**
3. **Administrator guide**

## Security Considerations

### 1. **Authentication Requirements**
- Multi-factor authentication for sensitive roles (MP, Chief of Staff, Admin)
- Strong password policies
- Session management and timeout
- IP whitelisting for admin roles

### 2. **Authorization Best Practices**
- Principle of least privilege
- Regular permission audits
- Role separation enforcement
- Activity logging and monitoring

### 3. **Data Protection**
- Encryption at rest and in transit
- Personal data access controls
- Audit trails for sensitive operations
- GDPR/privacy compliance

### 4. **Security Headers**
- CSRF protection
- XSS prevention
- Content Security Policy
- Secure cookie settings

## Testing Strategy

### 1. **Unit Tests**
```python
# Test role assignment
def test_user_role_assignment(self):
    user = User.objects.create_user(username='test', user_type='coordinator')
    self.assertEqual(user.user_type, 'coordinator')
    self.assertTrue(user.is_coordinator_or_above())

# Test permission checks
def test_permission_enforcement(self):
    # Test each role's permissions
    pass
```

### 2. **Integration Tests**
- Test role-based view access
- Test permission inheritance
- Test API endpoint permissions

### 3. **Security Tests**
- Penetration testing
- Permission bypass attempts
- Session hijacking prevention

### 4. **User Acceptance Tests**
- Role-specific workflows
- Permission denial scenarios
- UI/UX testing for each role

## Migration Plan

### 1. **Data Migration Steps**
1. Backup existing user data
2. Map existing user types to new roles
3. Create Django migration scripts
4. Test migration in staging
5. Execute production migration

### 2. **Rollout Strategy**
- Phase 1: Internal testing with staff accounts
- Phase 2: Pilot with selected coordinators
- Phase 3: Full rollout to all users
- Phase 4: Public access enablement

### 3. **Training Plan**
- Administrator training sessions
- Coordinator workshops
- User guides and documentation
- Video tutorials for each role

### 4. **Support Structure**
- Dedicated support during rollout
- FAQ documentation
- Issue tracking system
- Regular feedback collection

## Monitoring and Maintenance

### 1. **Performance Monitoring**
- Permission check performance
- Database query optimization
- Cache effectiveness

### 2. **Security Monitoring**
- Failed authentication attempts
- Permission denial patterns
- Unusual access patterns

### 3. **Regular Audits**
- Quarterly permission reviews
- Role assignment audits
- Inactive user cleanup
- Security compliance checks

## Future Enhancements

### 1. **Advanced Features**
- Attribute-based access control (ABAC)
- Dynamic role creation
- Temporary permission grants
- Delegation capabilities

### 2. **Integration Possibilities**
- Single Sign-On (SSO)
- External identity providers
- API key management
- Third-party service permissions

### 3. **Scalability Considerations**
- Distributed permission caching
- Microservices architecture
- Federation support
- Multi-region deployment

## Conclusion

This RBAC implementation plan provides a comprehensive, secure, and scalable access control system for the #FahanieCares portal. The phased approach ensures minimal disruption while delivering enhanced security and user management capabilities. Regular monitoring and maintenance will ensure the system remains effective and aligned with organizational needs.