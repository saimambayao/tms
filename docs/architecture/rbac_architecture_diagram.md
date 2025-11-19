# BM Parliament RBAC Architecture Diagrams

## Role Hierarchy Diagram

```mermaid
graph TD
    SUPER[Superuser<br/>Level 10 - Ultimate Control]
    MP[Member of Parliament<br/>Level 9 - Strategic Oversight]
    COS[Chief of Staff<br/>Level 8 - Operational Leadership]
    ADMIN[System Administrator<br/>Level 7 - Staff + Full Portal Management]
    COORD[Coordinator<br/>Level 6 - Staff + Service Management]
    INFO[Information Officer<br/>Level 5 - Staff + Communications]
    STAFF[Parliamentary Office Staff<br/>Level 4 - BASE STAFF LEVEL]
    MEMBER[Chapter Member<br/>Level 3 - Chapter Activities]
    USER[Registered User<br/>Level 2 - Basic Access]
    PUBLIC[Public/Visitor<br/>Level 1 - Public Only]

    SUPER --> MP
    MP --> COS
    COS --> ADMIN
    COS --> COORD
    COS --> INFO
    
    %% Staff-based inheritance: Admin, Coordinator, Info Officer all inherit from Staff
    ADMIN --> STAFF
    COORD --> STAFF
    INFO --> STAFF
    
    %% Chapter and user hierarchy
    STAFF --> MEMBER
    MEMBER --> USER
    USER --> PUBLIC

    style SUPER fill:#9333ea,stroke:#7c2d12,color:#fff
    style MP fill:#2563eb,stroke:#1d4ed8,color:#fff
    style COS fill:#7c3aed,stroke:#6d28d9,color:#fff
    style ADMIN fill:#dc2626,stroke:#b91c1c,color:#fff
    style COORD fill:#16a34a,stroke:#15803d,color:#fff
    style INFO fill:#ea580c,stroke:#c2410c,color:#fff
    style STAFF fill:#0891b2,stroke:#0e7490,color:#fff
    style MEMBER fill:#64748b,stroke:#475569,color:#fff
    style USER fill:#94a3b8,stroke:#64748b,color:#fff
    style PUBLIC fill:#e2e8f0,stroke:#cbd5e1,color:#334155
```

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[User Interface]
        TEMPLATES[Django Templates]
        COMPONENTS[Component Library]
    end

    subgraph "Authentication Layer"
        AUTH[Django Auth]
        MFA[Multi-Factor Auth]
        SESSION[Session Management]
    end

    subgraph "Authorization Layer"
        RBAC[RBAC Engine]
        PERMS[Permission Manager]
        DECORATORS[Permission Decorators]
        MIDDLEWARE[Role Middleware]
    end

    subgraph "Application Layer"
        VIEWS[Django Views]
        APIS[REST APIs]
        SERVICES[Service Layer]
    end

    subgraph "Data Layer"
        MODELS[Django Models]
        CACHE[Redis Cache]
        DB[(PostgreSQL)]
        NOTION[Notion API]
    end

    UI --> AUTH
    AUTH --> RBAC
    RBAC --> VIEWS
    VIEWS --> SERVICES
    SERVICES --> MODELS
    MODELS --> DB
    MODELS --> NOTION
    PERMS --> CACHE
    
    TEMPLATES --> COMPONENTS
    DECORATORS --> VIEWS
    MIDDLEWARE --> RBAC
    APIS --> SERVICES
```

## Permission Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Auth
    participant RBAC
    participant View
    participant Service
    participant Database

    User->>Frontend: Access Request
    Frontend->>Auth: Authenticate User
    Auth->>Auth: Verify Credentials & MFA
    Auth-->>Frontend: Auth Token
    
    Frontend->>RBAC: Request with Token
    RBAC->>RBAC: Check User Role
    RBAC->>RBAC: Load Role Permissions
    RBAC->>RBAC: Evaluate Access Rules
    
    alt Has Permission
        RBAC->>View: Grant Access
        View->>Service: Process Request
        Service->>Database: Query Data
        Database-->>Service: Return Data
        Service-->>View: Process Response
        View-->>Frontend: Render Response
        Frontend-->>User: Display Content
    else No Permission
        RBAC-->>Frontend: Access Denied
        Frontend-->>User: Show Error
    end
```

## Module Access Matrix

```mermaid
graph LR
    subgraph "Modules"
        DASH[Dashboard]
        USERS[User Mgmt]
        CONST[Constituents]
        SERV[Services]
        REF[Referrals]
        COMM[Communications]
        ANALYTICS[Analytics]
        ADMIN_MOD[Admin Tools]
        TASKS[Task Mgmt]
        CALENDAR[Calendar]
    end

    subgraph "Roles"
        R_SUPER[Superuser]
        R_MP[MP]
        R_COS[Chief of Staff]
        R_ADMIN[System Admin]
        R_COORD[Coordinator]
        R_INFO[Info Officer]
        R_STAFF[Staff]
        R_MEMBER[Member]
        R_USER[User]
        R_PUBLIC[Public]
    end

    R_SUPER -->|Ultimate Control| DASH
    R_SUPER -->|Ultimate Control| USERS
    R_SUPER -->|Ultimate Control| CONST
    R_SUPER -->|Ultimate Control| SERV
    R_SUPER -->|Ultimate Control| REF
    R_SUPER -->|Ultimate Control| COMM
    R_SUPER -->|Ultimate Control| ANALYTICS
    R_SUPER -->|Ultimate Control| ADMIN_MOD
    R_SUPER -->|Ultimate Control| TASKS
    R_SUPER -->|Ultimate Control| CALENDAR

    R_MP -.->|Strategic View| DASH
    R_MP -.->|Strategic View| ANALYTICS
    R_MP -.->|View Only| TASKS
    R_MP -.->|View Only| CALENDAR
    
    R_COS -->|Full Operational| DASH
    R_COS -->|Role Management| USERS
    R_COS -->|Full Access| CONST
    R_COS -->|Full Access| SERV
    R_COS -->|Full Access| REF
    R_COS -->|Full Access| COMM
    R_COS -->|Full Access| ANALYTICS
    R_COS -->|Workflow Control| ADMIN_MOD
    R_COS -->|Full Access| TASKS
    R_COS -->|Full Access| CALENDAR
    
    R_ADMIN -->|Staff Base Access| TASKS
    R_ADMIN -->|Staff Base Access| CALENDAR
    R_ADMIN -->|Full Technical| USERS
    R_ADMIN -->|Full Technical| ADMIN_MOD
    R_ADMIN -->|Full Access| CONST
    R_ADMIN -->|Full Access| SERV
    R_ADMIN -->|Full Access| REF
    R_ADMIN -->|Full Access| COMM
    R_ADMIN -->|Reports Access| ANALYTICS
    
    R_COORD -->|Staff Base Access| TASKS
    R_COORD -->|Staff Base Access| CALENDAR
    R_COORD -->|Service Management| CONST
    R_COORD -->|Service Management| SERV
    R_COORD -->|Service Management| REF
    R_COORD -->|Service Reports| ANALYTICS
    
    R_INFO -->|Staff Base Access| TASKS
    R_INFO -->|Staff Base Access| CALENDAR
    R_INFO -->|Full Communications| COMM
    R_INFO -->|Content Analytics| ANALYTICS
    
    R_STAFF -->|Base Access| TASKS
    R_STAFF -->|Base Access| CALENDAR
    
    R_MEMBER -->|Own Data| CONST
    R_MEMBER -->|Apply| SERV
    R_MEMBER -->|View Own| REF
    
    R_USER -->|Own Profile| CONST
    R_USER -->|View & Apply| SERV
    
    R_PUBLIC -->|View Only| COMM
    R_PUBLIC -->|View Info| SERV
```

## Database Schema for RBAC

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string user_type
        int chapter_id FK
        boolean is_active
        boolean mfa_enabled
        datetime created_at
        datetime updated_at
    }
    
    DJANGO_GROUP {
        int id PK
        string name
        string description
    }
    
    DJANGO_PERMISSION {
        int id PK
        string name
        string codename
        int content_type_id FK
    }
    
    DYNAMIC_PERMISSION {
        int id PK
        string name
        string codename
        text description
        boolean is_active
        datetime created_at
    }
    
    ROLE_PERMISSION {
        int id PK
        string role
        int permission_id FK
        boolean is_active
        datetime created_at
    }
    
    USER_GROUPS {
        int user_id FK
        int group_id FK
    }
    
    GROUP_PERMISSIONS {
        int group_id FK
        int permission_id FK
    }
    
    AUDIT_LOG {
        int id PK
        int user_id FK
        string action
        string model
        int object_id
        json changes
        datetime timestamp
    }
    
    USER ||--o{ USER_GROUPS : has
    DJANGO_GROUP ||--o{ USER_GROUPS : contains
    DJANGO_GROUP ||--o{ GROUP_PERMISSIONS : has
    DJANGO_PERMISSION ||--o{ GROUP_PERMISSIONS : assigned_to
    ROLE_PERMISSION }o--|| DYNAMIC_PERMISSION : references
    USER ||--o{ AUDIT_LOG : generates
```

## Security Layers

```mermaid
graph TD
    subgraph "Security Stack"
        L1[Network Security<br/>SSL/TLS, Firewall]
        L2[Application Security<br/>CSRF, XSS Protection]
        L3[Authentication<br/>Password + MFA]
        L4[Authorization<br/>RBAC System]
        L5[Data Security<br/>Encryption, Masking]
        L6[Audit & Monitoring<br/>Logs, Alerts]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    L5 --> L6
    
    style L1 fill:#fee2e2,stroke:#dc2626
    style L2 fill:#fef3c7,stroke:#f59e0b
    style L3 fill:#dbeafe,stroke:#3b82f6
    style L4 fill:#d1fae5,stroke:#10b981
    style L5 fill:#e0e7ff,stroke:#6366f1
    style L6 fill:#fce7f3,stroke:#ec4899
```

## Implementation Timeline

```mermaid
gantt
    title RBAC Implementation Schedule
    dateFormat  YYYY-MM-DD
    section Phase 1
    Model Updates           :2025-06-08, 7d
    Migration Scripts       :2025-06-12, 3d
    
    section Phase 2
    Permission System       :2025-06-15, 7d
    Decorators & Utils     :2025-06-19, 3d
    
    section Phase 3
    Middleware Updates      :2025-06-22, 7d
    Role Management API     :2025-06-26, 3d
    
    section Phase 4
    View Updates           :2025-06-29, 7d
    Template Updates       :2025-06-02, 3d
    
    section Phase 5
    Admin UI               :2025-06-05, 7d
    User Management UI     :2025-06-09, 3d
    
    section Phase 6
    Testing                :2025-06-12, 7d
    Documentation          :2025-06-16, 3d
    Deployment             :2025-06-19, 2d
```

## API Endpoint Security Matrix

```mermaid
graph TD
    subgraph "API Endpoints"
        subgraph "Public APIs"
            API1[GET /api/services/]
            API2[GET /api/announcements/]
        end
        
        subgraph "Authenticated APIs"
            API3[GET /api/profile/]
            API4[POST /api/services/apply/]
        end
        
        subgraph "Staff APIs"
            API5[POST /api/constituents/]
            API6[PUT /api/referrals/:id/]
        end
        
        subgraph "Admin APIs"
            API7[POST /api/users/]
            API8[DELETE /api/users/:id/]
        end
    end
    
    subgraph "Security Checks"
        CHECK1{Is Authenticated?}
        CHECK2{Has Permission?}
        CHECK3{Rate Limit OK?}
    end
    
    API1 --> CHECK3
    API2 --> CHECK3
    API3 --> CHECK1
    API4 --> CHECK1
    API5 --> CHECK1
    API6 --> CHECK1
    API7 --> CHECK1
    API8 --> CHECK1
    
    CHECK1 -->|Yes| CHECK2
    CHECK1 -->|No| DENY[Access Denied]
    CHECK2 -->|Yes| CHECK3
    CHECK2 -->|No| DENY
    CHECK3 -->|Yes| ALLOW[Process Request]
    CHECK3 -->|No| LIMIT[Rate Limited]
```

## Role Transition Workflow

```mermaid
stateDiagram-v2
    [*] --> Public: Visit Site
    Public --> RegisteredUser: Sign Up
    RegisteredUser --> ChapterMember: Verify & Join Chapter
    
    %% Staff-based promotion paths
    RegisteredUser --> Staff: Hired as Parliamentary Staff
    ChapterMember --> Staff: Promoted to Parliamentary Staff
    
    %% Staff role progressions (all inherit from Staff base)
    Staff --> InfoOfficer: Assigned Communication Role
    Staff --> Coordinator: Assigned Service Coordination Role  
    Staff --> Admin: Assigned System Administration Role
    
    %% Higher level assignments
    InfoOfficer --> Coordinator: Cross-training/Promotion
    Coordinator --> Admin: Technical Promotion
    Admin --> ChiefOfStaff: Leadership Assignment
    ChiefOfStaff --> MP: Not Applicable (Elected Position)
    
    %% Superuser assignments
    Admin --> Superuser: Ultimate Access Assignment
    ChiefOfStaff --> Superuser: Ultimate Access Assignment
    
    state "Staff-Based Hierarchy" {
        InfoOfficer: Staff + Communications
        Coordinator: Staff + Services  
        Admin: Staff + Full Management
    }
    
    %% Deactivation paths
    RegisteredUser --> [*]: Account Deactivated
    ChapterMember --> [*]: Account Deactivated
    Staff --> [*]: Employment Ended
    InfoOfficer --> [*]: Employment Ended
    Coordinator --> [*]: Employment Ended
    Admin --> [*]: Employment Ended
```

## Component Access Control

```mermaid
graph TB
    subgraph "UI Components"
        NAV[Navigation Menu]
        DASH_COMP[Dashboard Components]
        FORMS[Form Components]
        TABLES[Data Tables]
        REPORTS[Report Widgets]
    end
    
    subgraph "Access Control"
        ROLE_CHECK{Check User Role}
        PERM_CHECK{Check Permission}
        RENDER[Render Component]
        HIDE[Hide Component]
    end
    
    NAV --> ROLE_CHECK
    DASH_COMP --> ROLE_CHECK
    FORMS --> PERM_CHECK
    TABLES --> PERM_CHECK
    REPORTS --> ROLE_CHECK
    
    ROLE_CHECK -->|Authorized| RENDER
    ROLE_CHECK -->|Unauthorized| HIDE
    PERM_CHECK -->|Has Permission| RENDER
    PERM_CHECK -->|No Permission| HIDE
```

These diagrams provide a comprehensive visual representation of the RBAC architecture, including:

1. **Role Hierarchy**: Shows the hierarchical relationship between roles with staff-based inheritance
2. **System Architecture**: Illustrates the technical layers and components
3. **Permission Flow**: Demonstrates how permissions are evaluated
4. **Module Access Matrix**: Maps roles to module access with staff base level
5. **Database Schema**: Shows the RBAC data model
6. **Security Layers**: Illustrates the defense-in-depth approach
7. **Implementation Timeline**: Gantt chart for project phases
8. **API Security**: Shows API endpoint protection
9. **Role Transitions**: State diagram for role changes with staff-based progression
10. **Component Access**: UI component visibility control

## Key Architecture Updates

The diagrams have been updated to reflect the corrected staff-based hierarchy:

- **Parliamentary Office Staff (Level 4)**: Established as the BASE LEVEL for all parliamentary workers
- **Information Officer (Level 5)**: Staff + Communication management capabilities
- **Coordinator (Level 6)**: Staff + Service coordination and management capabilities  
- **System Administrator (Level 7)**: Staff + Full portal management and technical control
- **Staff-Based Inheritance**: All parliamentary roles (Info Officer, Coordinator, Admin) inherit base staff permissions for task/calendar management
- **Clear Role Progression**: Shows natural promotion paths through the staff-based hierarchy
- **Enhanced Module Access**: Task Management and Calendar modules added to reflect staff base functionality

This architecture ensures that all parliamentary workers have consistent access to core office functionality while maintaining role-specific capabilities and security boundaries.

These diagrams can be rendered using any Mermaid-compatible viewer or documentation system.