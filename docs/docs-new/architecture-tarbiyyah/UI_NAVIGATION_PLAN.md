# TMS Multitenant Architecture - Role-Based Navigation Plan

**Document Version:** 4.0
**Date:** November 20, 2025
**Purpose:** Define the multitenant architecture with 5 different navigation bars based on user roles

---

## Architecture Overview

**One TMS Application with 5 Different Navigation Bars:**

1. **Main TMS Navigation** - For Tarbiyyah Committee administrators (TARBIYYAH_ADMIN)
2. **Madrasah Navigation** - For school administrators (MADRASAH_ADMIN, MUDER)
3. **Teacher Navigation** - For teachers (ASATIDZ)
4. **Student Navigation** - For students (STUDENT)
5. **Parent Navigation** - For parents (PARENT)

**Key Principles:**
- ONE Django application (single codebase)
- FIVE different navigation bars (different menu items per role)
- Multitenant system (each madrasah is a tenant)
- Role-based UI rendering (different navbar templates)
- All users access the same domain: `https://tms.tarbiyyah.gov.ph/`

---

## System Overview

The Tarbiyyah Management System (TMS) is a **multitenant platform** where:

1. **Tarbiyyah Committee** manages the entire system (all madaris region-wide)
2. **Each madrasah** is a separate tenant with its own account
3. **Different user types** see completely different navigation bars
4. **All users** access the same Django application
5. **Navigation rendered** based on authenticated user's role

---

## User Roles & Their Navigation

### 1. TARBIYYAH_ADMIN - Main TMS Navigation

**Role:** System administrators managing all madaris across BARMM and beyond

**Navigation Bar:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🕌 Tarbiyyah Management System                            [User Menu]   │
├─────────────────────────────────────────────────────────────────────────┤
│  Homepage | About | Madaris ▼ | Support | Curriculum | Dashboards      │
└─────────────────────────────────────────────────────────────────────────┘
```

**Menu Items:**

| Menu Item | URL | Purpose |
|-----------|-----|---------|
| **Homepage** | `/` | System-wide overview and announcements |
| **About** | `/about/` | About the Tarbiyyah Committee |
| **Madaris** (dropdown) | `/madaris/` | Information System hub |
| ├─ Madrasah Registration | `/madaris/madrasah/register/` | Register new madaris |
| ├─ Madrasah Database | `/madaris/madrasah/directory/` | All registered madaris |
| ├─ Asatidz Registration | `/madaris/asatidz/register/` | Register teachers |
| ├─ Asatidz Database | `/madaris/asatidz/directory/` | All registered teachers |
| ├─ Student Registration | `/madaris/students/register/` | Register students |
| └─ Student Database | `/madaris/students/directory/` | All registered students |
| **Support** | `/support/` | Madaris support programs |
| **Curriculum** | `/curriculum/` | Curriculum management |
| **Dashboards** | `/dashboards/` | System-wide reports and analytics |
| **User Dropdown** | | Profile, Settings, Notifications, Logout |

**Access Scope:**
- System-wide access to ALL madaris
- ALL students across all schools
- ALL teachers across all schools
- Full administrative capabilities

---

### 2. MADRASAH_ADMIN & MUDER - Madrasah Navigation

**Roles:**
- **MADRASAH_ADMIN:** Regional/municipal administrators
- **MUDER:** Individual school principals/administrators

**Navigation Bar:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🕌 [Madrasah Name]                                       [User Menu]    │
├─────────────────────────────────────────────────────────────────────────┤
│  Dashboard | Students ▼ | Teachers ▼ | Classes | Academic | Reports     │
└─────────────────────────────────────────────────────────────────────────┘
```

**Menu Items:**

| Menu Item | URL | Purpose |
|-----------|-----|---------|
| **Dashboard** | `/madrasah/dashboard/` | School overview, statistics, today's schedule |
| **Students** (dropdown) | `/madrasah/students/` | Student management hub |
| ├─ Enroll Student | `/madrasah/students/enroll/` | Enroll new student |
| ├─ Student Directory | `/madrasah/students/directory/` | All students in this madrasah |
| ├─ Manage Enrollment | `/madrasah/students/enrollment/` | Manage enrollments |
| └─ Student Records | `/madrasah/students/records/` | Academic records |
| **Teachers** (dropdown) | `/madrasah/teachers/` | Teacher management hub |
| ├─ Add Teacher | `/madrasah/teachers/add/` | Add new teacher |
| ├─ Teacher Directory | `/madrasah/teachers/directory/` | All teachers at this madrasah |
| ├─ Assignments | `/madrasah/teachers/assignments/` | Subject/class assignments |
| └─ Performance | `/madrasah/teachers/performance/` | Teacher performance reviews |
| **Classes** | `/madrasah/classes/` | Class sections and schedules |
| **Academic** | `/madrasah/academic/` | Grading, attendance, assessments |
| **Reports** | `/madrasah/reports/` | School reports and analytics |
| **Settings** | `/madrasah/settings/` | School settings and configuration |
| **User Dropdown** | | Profile, Settings, Help, Logout |

**Access Scope:**
- **MADRASAH_ADMIN:** Regional/municipal scope (multiple schools)
- **MUDER:** Single school scope (their assigned madrasah only)

---

### 3. ASATIDZ - Teacher Navigation

**Role:** Teachers/instructors

**Navigation Bar:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🕌 [Teacher Name] - [Madrasah Name]                     [User Menu]     │
├─────────────────────────────────────────────────────────────────────────┤
│  Dashboard | My Classes ▼ | Students | Gradebook | Attendance | Calendar│
└─────────────────────────────────────────────────────────────────────────┘
```

**Menu Items:**

| Menu Item | URL | Purpose |
|-----------|-----|---------|
| **Dashboard** | `/teacher/dashboard/` | Today's schedule, upcoming tasks, student performance |
| **My Classes** (dropdown) | `/teacher/classes/` | Classes taught by this teacher |
| ├─ Class List | `/teacher/classes/list/` | All assigned classes |
| ├─ [Class 1] | `/teacher/classes/{id}/` | Specific class details |
| ├─ [Class 2] | `/teacher/classes/{id}/` | Specific class details |
| └─ Class Schedule | `/teacher/classes/schedule/` | Teaching schedule |
| **Students** | `/teacher/students/` | Students in teacher's classes |
| **Gradebook** | `/teacher/gradebook/` | Enter and manage grades |
| **Attendance** | `/teacher/attendance/` | Take and manage attendance |
| **Curriculum** | `/teacher/curriculum/` | Lesson plans and teaching resources |
| **Calendar** | `/teacher/calendar/` | Class calendar and deadlines |
| **User Dropdown** | | Profile, Settings, Resources, Help, Logout |

**Access Scope:**
- Only students in teacher's assigned classes
- Only classes assigned to this teacher
- Grade entry for their subjects
- Attendance for their class sessions

---

### 4. STUDENT - Student Navigation

**Role:** Students enrolled in madrasah

**Navigation Bar:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🕌 [Student Name] - [Madrasah Name]                     [User Menu]     │
├─────────────────────────────────────────────────────────────────────────┤
│  Dashboard | My Classes | Grades | Schedule | Assignments | Resources   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Menu Items:**

| Menu Item | URL | Purpose |
|-----------|-----|---------|
| **Dashboard** | `/student/dashboard/` | Personal overview, today's classes, recent grades |
| **My Classes** | `/student/classes/` | Enrolled classes and subjects |
| **Grades** | `/student/grades/` | Report cards and grade history |
| **Schedule** | `/student/schedule/` | Class schedule and timetable |
| **Assignments** | `/student/assignments/` | Homework and assignments |
| **Resources** | `/student/resources/` | Learning materials and resources |
| **Calendar** | `/student/calendar/` | Academic calendar and events |
| **User Dropdown** | | Profile, Settings, Help, Logout |

**Access Scope:**
- Only own academic records
- Only enrolled classes
- Only personal grades and attendance
- Own profile and settings

---

### 5. PARENT - Parent Navigation

**Role:** Parents of enrolled students

**Navigation Bar:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🕌 [Parent Name] - Parent Portal                        [User Menu]     │
├─────────────────────────────────────────────────────────────────────────┤
│  Dashboard | My Children ▼ | Academic Progress | Attendance | Messages  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Menu Items:**

| Menu Item | URL | Purpose |
|-----------|-----|---------|
| **Dashboard** | `/parent/dashboard/` | Overview of all children's progress |
| **My Children** (dropdown) | `/parent/children/` | Children management |
| ├─ [Child 1 Name] | `/parent/children/{id}/` | First child's profile |
| ├─ [Child 2 Name] | `/parent/children/{id}/` | Second child's profile |
| └─ Add Child | `/parent/children/add/` | Enroll new child |
| **Academic Progress** | `/parent/academic/` | Children's grades and reports |
| **Attendance** | `/parent/attendance/` | Children's attendance records |
| **Messages** | `/parent/messages/` | Communication with teachers/school |
| **Calendar** | `/parent/calendar/` | School events and activities |
| **User Dropdown** | | Profile, Settings, Help, Logout |

**Access Scope:**
- Only their enrolled children's data
- Children's academic records
- Children's attendance
- Communication with children's teachers

---

## Multitenant Architecture

### What is Multitenancy in TMS?

**Each Madrasah = One Tenant**

Each madrasah operates independently within the system:

1. **Separate Data Isolation:**
   - Students at Madrasah A cannot see students at Madrasah B
   - Teachers at one school only see their own school's data
   - School administrators manage only their school

2. **Shared Infrastructure:**
   - All madaris use the same Django application
   - Same database with tenant filtering
   - Same codebase and deployment

3. **System-Level Oversight:**
   - Tarbiyyah Committee (TARBIYYAH_ADMIN) can see across ALL tenants
   - Regional admins (MADRASAH_ADMIN) can see multiple tenants in their region

### Tenant Identification

```python
# Every user belongs to a tenant (madrasah)
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    madrasah = models.ForeignKey('Madrasah', on_delete=models.CASCADE, null=True)
    # TARBIYYAH_ADMIN has madrasah=None (system-wide access)

# Every record is scoped to a tenant
class Student(models.Model):
    madrasah = models.ForeignKey('Madrasah', on_delete=models.CASCADE)
    # ... other fields

class Teacher(models.Model):
    madrasah = models.ForeignKey('Madrasah', on_delete=models.CASCADE)
    # ... other fields
```

### Tenant Filtering Middleware

```python
# Automatic tenant filtering based on logged-in user
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Store current tenant in request
            if request.user.role == 'TARBIYYAH_ADMIN':
                request.tenant = None  # System-wide access
            else:
                request.tenant = request.user.madrasah

        response = self.get_response(request)
        return response
```

---

## Navigation Rendering Logic

### Base Template Strategy

**One base template with role-based navbar includes:**

```django
{# templates/base.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}TMS{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body>
    {# Include navbar based on user role #}
    {% if user.is_authenticated %}
        {% if user.role == 'TARBIYYAH_ADMIN' %}
            {% include 'navbars/tarbiyyah_admin_navbar.html' %}

        {% elif user.role in 'MADRASAH_ADMIN,MUDER' %}
            {% include 'navbars/madrasah_navbar.html' %}

        {% elif user.role == 'ASATIDZ' %}
            {% include 'navbars/teacher_navbar.html' %}

        {% elif user.role == 'STUDENT' %}
            {% include 'navbars/student_navbar.html' %}

        {% elif user.role == 'PARENT' %}
            {% include 'navbars/parent_navbar.html' %}

        {% endif %}
    {% else %}
        {% include 'navbars/public_navbar.html' %}
    {% endif %}

    <main class="content">
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>&copy; 2025 Tarbiyyah Committee - BARMM</p>
    </footer>

    <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

### Navbar Templates

Each role has its own navbar template:

**1. TMS Admin Navbar**
```django
{# templates/navbars/tarbiyyah_admin_navbar.html #}
<nav class="navbar navbar-tms-admin">
    <div class="navbar-brand">
        <img src="{% static 'images/tms-logo.png' %}" alt="TMS">
        <span>Tarbiyyah Management System</span>
    </div>

    <ul class="navbar-menu">
        <li><a href="/">Homepage</a></li>
        <li><a href="/about/">About</a></li>
        <li class="dropdown">
            <a href="/madaris/">Madaris ▼</a>
            <ul class="dropdown-menu">
                <li><a href="/madaris/madrasah/register/">Madrasah Registration</a></li>
                <li><a href="/madaris/madrasah/directory/">Madrasah Database</a></li>
                <li><a href="/madaris/asatidz/register/">Asatidz Registration</a></li>
                <li><a href="/madaris/asatidz/directory/">Asatidz Database</a></li>
                <li><a href="/madaris/students/register/">Student Registration</a></li>
                <li><a href="/madaris/students/directory/">Student Database</a></li>
            </ul>
        </li>
        <li><a href="/support/">Support</a></li>
        <li><a href="/curriculum/">Curriculum</a></li>
        <li><a href="/dashboards/">Dashboards</a></li>
    </ul>

    <div class="navbar-user">
        <div class="dropdown">
            <a href="#" class="user-menu">
                {{ user.get_full_name }}
                <span class="badge badge-tarbiyyah">{{ user.role }}</span>
            </a>
            <ul class="dropdown-menu">
                <li><a href="/profile/">Profile</a></li>
                <li><a href="/settings/">Settings</a></li>
                <li><a href="/notifications/">Notifications</a></li>
                <li><a href="/help/">Help</a></li>
                <li><hr></li>
                <li><a href="/logout/">Logout</a></li>
            </ul>
        </div>
    </div>
</nav>
```

**2. Madrasah Navbar**
```django
{# templates/navbars/madrasah_navbar.html #}
<nav class="navbar navbar-madrasah">
    <div class="navbar-brand">
        <img src="{{ user.madrasah.logo_url }}" alt="{{ user.madrasah.name }}">
        <span>{{ user.madrasah.name }}</span>
    </div>

    <ul class="navbar-menu">
        <li><a href="/madrasah/dashboard/">Dashboard</a></li>

        <li class="dropdown">
            <a href="/madrasah/students/">Students ▼</a>
            <ul class="dropdown-menu">
                <li><a href="/madrasah/students/enroll/">Enroll Student</a></li>
                <li><a href="/madrasah/students/directory/">Student Directory</a></li>
                <li><a href="/madrasah/students/enrollment/">Manage Enrollment</a></li>
                <li><a href="/madrasah/students/records/">Student Records</a></li>
            </ul>
        </li>

        <li class="dropdown">
            <a href="/madrasah/teachers/">Teachers ▼</a>
            <ul class="dropdown-menu">
                <li><a href="/madrasah/teachers/add/">Add Teacher</a></li>
                <li><a href="/madrasah/teachers/directory/">Teacher Directory</a></li>
                <li><a href="/madrasah/teachers/assignments/">Assignments</a></li>
                <li><a href="/madrasah/teachers/performance/">Performance</a></li>
            </ul>
        </li>

        <li><a href="/madrasah/classes/">Classes</a></li>
        <li><a href="/madrasah/academic/">Academic</a></li>
        <li><a href="/madrasah/reports/">Reports</a></li>
        <li><a href="/madrasah/settings/">Settings</a></li>
    </ul>

    <div class="navbar-user">
        <div class="dropdown">
            <a href="#" class="user-menu">
                {{ user.get_full_name }}
                <span class="badge badge-muder">{{ user.role }}</span>
            </a>
            <ul class="dropdown-menu">
                <li><a href="/profile/">Profile</a></li>
                <li><a href="/settings/">Settings</a></li>
                <li><a href="/help/">Help</a></li>
                <li><hr></li>
                <li><a href="/logout/">Logout</a></li>
            </ul>
        </div>
    </div>
</nav>
```

**3. Teacher Navbar**
```django
{# templates/navbars/teacher_navbar.html #}
<nav class="navbar navbar-teacher">
    <div class="navbar-brand">
        <img src="{{ user.madrasah.logo_url }}" alt="{{ user.madrasah.name }}">
        <span>{{ user.get_full_name }} - {{ user.madrasah.name }}</span>
    </div>

    <ul class="navbar-menu">
        <li><a href="/teacher/dashboard/">Dashboard</a></li>

        <li class="dropdown">
            <a href="/teacher/classes/">My Classes ▼</a>
            <ul class="dropdown-menu">
                <li><a href="/teacher/classes/list/">Class List</a></li>
                {% for class in user.assigned_classes.all %}
                <li><a href="/teacher/classes/{{ class.id }}/">{{ class.name }}</a></li>
                {% endfor %}
                <li><hr></li>
                <li><a href="/teacher/classes/schedule/">Class Schedule</a></li>
            </ul>
        </li>

        <li><a href="/teacher/students/">Students</a></li>
        <li><a href="/teacher/gradebook/">Gradebook</a></li>
        <li><a href="/teacher/attendance/">Attendance</a></li>
        <li><a href="/teacher/curriculum/">Curriculum</a></li>
        <li><a href="/teacher/calendar/">Calendar</a></li>
    </ul>

    <div class="navbar-user">
        <div class="dropdown">
            <a href="#" class="user-menu">
                {{ user.get_full_name }}
                <span class="badge badge-teacher">Teacher</span>
            </a>
            <ul class="dropdown-menu">
                <li><a href="/profile/">Profile</a></li>
                <li><a href="/settings/">Settings</a></li>
                <li><a href="/teacher/resources/">Resources</a></li>
                <li><a href="/help/">Help</a></li>
                <li><hr></li>
                <li><a href="/logout/">Logout</a></li>
            </ul>
        </div>
    </div>
</nav>
```

**4. Student Navbar**
```django
{# templates/navbars/student_navbar.html #}
<nav class="navbar navbar-student">
    <div class="navbar-brand">
        <img src="{{ user.student_profile.madrasah.logo_url }}" alt="{{ user.student_profile.madrasah.name }}">
        <span>{{ user.get_full_name }} - {{ user.student_profile.madrasah.name }}</span>
    </div>

    <ul class="navbar-menu">
        <li><a href="/student/dashboard/">Dashboard</a></li>
        <li><a href="/student/classes/">My Classes</a></li>
        <li><a href="/student/grades/">Grades</a></li>
        <li><a href="/student/schedule/">Schedule</a></li>
        <li><a href="/student/assignments/">Assignments</a></li>
        <li><a href="/student/resources/">Resources</a></li>
        <li><a href="/student/calendar/">Calendar</a></li>
    </ul>

    <div class="navbar-user">
        <div class="dropdown">
            <a href="#" class="user-menu">
                {{ user.get_full_name }}
                <span class="badge badge-student">Student</span>
            </a>
            <ul class="dropdown-menu">
                <li><a href="/profile/">Profile</a></li>
                <li><a href="/settings/">Settings</a></li>
                <li><a href="/help/">Help</a></li>
                <li><hr></li>
                <li><a href="/logout/">Logout</a></li>
            </ul>
        </div>
    </div>
</nav>
```

**5. Parent Navbar**
```django
{# templates/navbars/parent_navbar.html #}
<nav class="navbar navbar-parent">
    <div class="navbar-brand">
        <img src="{% static 'images/tms-logo.png' %}" alt="TMS">
        <span>{{ user.get_full_name }} - Parent Portal</span>
    </div>

    <ul class="navbar-menu">
        <li><a href="/parent/dashboard/">Dashboard</a></li>

        <li class="dropdown">
            <a href="/parent/children/">My Children ▼</a>
            <ul class="dropdown-menu">
                {% for child in user.children.all %}
                <li><a href="/parent/children/{{ child.id }}/">{{ child.get_full_name }}</a></li>
                {% endfor %}
                <li><hr></li>
                <li><a href="/parent/children/add/">Enroll Child</a></li>
            </ul>
        </li>

        <li><a href="/parent/academic/">Academic Progress</a></li>
        <li><a href="/parent/attendance/">Attendance</a></li>
        <li><a href="/parent/messages/">Messages</a></li>
        <li><a href="/parent/calendar/">Calendar</a></li>
    </ul>

    <div class="navbar-user">
        <div class="dropdown">
            <a href="#" class="user-menu">
                {{ user.get_full_name }}
                <span class="badge badge-parent">Parent</span>
            </a>
            <ul class="dropdown-menu">
                <li><a href="/profile/">Profile</a></li>
                <li><a href="/settings/">Settings</a></li>
                <li><a href="/help/">Help</a></li>
                <li><hr></li>
                <li><a href="/logout/">Logout</a></li>
            </ul>
        </div>
    </div>
</nav>
```

---

## URL Structure

### All Roles Access Same Domain

```
https://tms.tarbiyyah.gov.ph/
```

**No separate subdomains** - tenant filtering happens server-side.

### URL Patterns by Role

**TMS Admin URLs:**
```
/                             # Homepage (system-wide overview)
/about/                       # About Tarbiyyah Committee
/madaris/madrasah/directory/  # All madaris
/madaris/students/directory/  # All students (system-wide)
/dashboards/                  # System analytics
```

**Madrasah URLs:**
```
/madrasah/dashboard/              # School dashboard
/madrasah/students/directory/     # Students in this madrasah
/madrasah/teachers/directory/     # Teachers at this madrasah
/madrasah/classes/                # Classes at this madrasah
/madrasah/reports/                # School reports
```

**Teacher URLs:**
```
/teacher/dashboard/          # Teacher dashboard
/teacher/classes/            # Teacher's classes
/teacher/students/           # Students in teacher's classes
/teacher/gradebook/          # Enter grades
/teacher/attendance/         # Mark attendance
```

**Student URLs:**
```
/student/dashboard/          # Student dashboard
/student/classes/            # Student's enrolled classes
/student/grades/             # Student's grades
/student/schedule/           # Student's schedule
```

**Parent URLs:**
```
/parent/dashboard/           # Parent dashboard
/parent/children/            # Parent's children
/parent/academic/            # Children's academic progress
/parent/messages/            # Messages from school
```

### URL Configuration

```python
# src/urls.py
from django.urls import path, include

urlpatterns = [
    # Public pages
    path('', include('apps.core.urls')),  # Homepage, About, Login

    # TMS Admin pages (TARBIYYAH_ADMIN only)
    path('madaris/', include('apps.madaris.urls')),  # System-wide madaris management
    path('support/', include('apps.support.urls')),
    path('curriculum/', include('apps.curriculum.urls')),
    path('dashboards/', include('apps.dashboards.urls')),

    # Madrasah pages (MADRASAH_ADMIN, MUDER)
    path('madrasah/', include('apps.madrasah_portal.urls')),

    # Teacher pages (ASATIDZ)
    path('teacher/', include('apps.teacher_portal.urls')),

    # Student pages (STUDENT)
    path('student/', include('apps.student_portal.urls')),

    # Parent pages (PARENT)
    path('parent/', include('apps.parent_portal.urls')),

    # User management
    path('accounts/', include('apps.accounts.urls')),
]
```

---

## Django App Structure

### Recommended App Organization

```
apps/
├── core/                          # Core functionality
│   ├── templates/
│   │   ├── base.html             # Main base template
│   │   ├── homepage.html         # Homepage (role-aware)
│   │   ├── about.html            # About page
│   │   └── navbars/              # Navigation templates
│   │       ├── tarbiyyah_admin_navbar.html
│   │       ├── madrasah_navbar.html
│   │       ├── teacher_navbar.html
│   │       ├── student_navbar.html
│   │       ├── parent_navbar.html
│   │       └── public_navbar.html
│   ├── context_processors.py    # Role context for templates
│   ├── middleware.py             # Tenant middleware
│   └── views.py                  # Homepage, About

├── madaris/                       # TMS Admin - Madaris Management
│   ├── views/
│   │   ├── madrasah.py           # Madrasah CRUD (system-wide)
│   │   ├── asatidz.py            # Teacher management (system-wide)
│   │   └── students.py           # Student management (system-wide)
│   ├── templates/madaris/
│   └── urls.py

├── support/                       # Support services
├── curriculum/                    # Curriculum management
├── dashboards/                    # TMS Admin dashboards

├── madrasah_portal/               # Madrasah Admin Portal
│   ├── views/
│   │   ├── dashboard.py          # School dashboard
│   │   ├── students.py           # Student management (school-level)
│   │   ├── teachers.py           # Teacher management (school-level)
│   │   ├── classes.py            # Class management
│   │   └── reports.py            # School reports
│   ├── templates/madrasah_portal/
│   └── urls.py

├── teacher_portal/                # Teacher Portal
│   ├── views/
│   │   ├── dashboard.py          # Teacher dashboard
│   │   ├── classes.py            # Class views
│   │   ├── students.py           # Student views (class-level)
│   │   ├── gradebook.py          # Grade entry
│   │   └── attendance.py         # Attendance marking
│   ├── templates/teacher_portal/
│   └── urls.py

├── student_portal/                # Student Portal
│   ├── views/
│   │   ├── dashboard.py          # Student dashboard
│   │   ├── classes.py            # Class views
│   │   ├── grades.py             # Grade views
│   │   └── schedule.py           # Schedule views
│   ├── templates/student_portal/
│   └── urls.py

├── parent_portal/                 # Parent Portal
│   ├── views/
│   │   ├── dashboard.py          # Parent dashboard
│   │   ├── children.py           # Children management
│   │   ├── academic.py           # Academic progress
│   │   └── messages.py           # Communication
│   ├── templates/parent_portal/
│   └── urls.py

└── accounts/                      # User management
    ├── models.py                  # User model with role field
    ├── views.py                   # Login, logout, profile
    └── templates/accounts/
```

---

## Role-Based Access Control

### View Permissions

```python
# apps/core/decorators.py

from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles):
    """
    Decorator to restrict view access by role
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.role not in allowed_roles:
                raise PermissionDenied(
                    f"This page is only accessible to: {', '.join(allowed_roles)}"
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Example Usage

```python
# apps/madrasah_portal/views/dashboard.py

from django.shortcuts import render
from apps.core.decorators import role_required

@role_required(['MADRASAH_ADMIN', 'MUDER'])
def madrasah_dashboard(request):
    """
    School dashboard - only accessible to school administrators
    """
    madrasah = request.user.madrasah

    context = {
        'madrasah': madrasah,
        'student_count': madrasah.students.count(),
        'teacher_count': madrasah.teachers.count(),
        'class_count': madrasah.class_sections.count(),
    }

    return render(request, 'madrasah_portal/dashboard.html', context)
```

```python
# apps/teacher_portal/views/dashboard.py

from django.shortcuts import render
from apps.core.decorators import role_required

@role_required(['ASATIDZ'])
def teacher_dashboard(request):
    """
    Teacher dashboard - only accessible to teachers
    """
    teacher = request.user

    context = {
        'classes': teacher.assigned_classes.all(),
        'student_count': teacher.get_total_students(),
        'upcoming_classes': teacher.get_today_schedule(),
    }

    return render(request, 'teacher_portal/dashboard.html', context)
```

---

## Tenant Filtering Implementation

### Automatic Tenant Scoping

```python
# apps/core/middleware.py

class TenantMiddleware:
    """
    Middleware to automatically scope queries to the user's tenant (madrasah)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Set current tenant based on user role
            if request.user.role == 'TARBIYYAH_ADMIN':
                # System-wide access - no tenant filtering
                request.tenant = None
            elif request.user.role in ['MADRASAH_ADMIN', 'MUDER', 'ASATIDZ']:
                # Scoped to their assigned madrasah
                request.tenant = request.user.madrasah
            elif request.user.role == 'STUDENT':
                # Scoped to student's enrolled madrasah
                request.tenant = request.user.student_profile.madrasah
            elif request.user.role == 'PARENT':
                # Parents may have children at multiple madaris
                request.tenant = None  # Handle in view logic
            else:
                request.tenant = None
        else:
            request.tenant = None

        response = self.get_response(request)
        return response
```

### Query Filtering Helper

```python
# apps/core/utils.py

def get_tenant_filtered_queryset(model, user):
    """
    Get a queryset filtered by the user's tenant scope
    """
    if user.role == 'TARBIYYAH_ADMIN':
        # System-wide access
        return model.objects.all()

    elif user.role in ['MADRASAH_ADMIN', 'MUDER']:
        # Filter by madrasah
        return model.objects.filter(madrasah=user.madrasah)

    elif user.role == 'ASATIDZ':
        # Filter by teacher's classes
        if model.__name__ == 'Student':
            return model.objects.filter(
                enrollments__class_section__teacher=user
            ).distinct()
        else:
            return model.objects.filter(madrasah=user.madrasah)

    elif user.role == 'STUDENT':
        # Only own record
        if model.__name__ == 'Student':
            return model.objects.filter(user=user)
        else:
            return model.objects.none()

    elif user.role == 'PARENT':
        # Only children
        if model.__name__ == 'Student':
            return model.objects.filter(parent=user)
        else:
            return model.objects.none()

    return model.objects.none()
```

---

## Authentication & Login Flow

### Login and Role-Based Redirect

```python
# apps/accounts/views.py

from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, render

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on role
            if user.role == 'TARBIYYAH_ADMIN':
                return redirect('/')  # TMS homepage

            elif user.role in ['MADRASAH_ADMIN', 'MUDER']:
                return redirect('/madrasah/dashboard/')  # School dashboard

            elif user.role == 'ASATIDZ':
                return redirect('/teacher/dashboard/')  # Teacher dashboard

            elif user.role == 'STUDENT':
                return redirect('/student/dashboard/')  # Student dashboard

            elif user.role == 'PARENT':
                return redirect('/parent/dashboard/')  # Parent dashboard

            else:
                return redirect('/')  # Default homepage

        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid credentials'
            })

    return render(request, 'accounts/login.html')
```

---

## Visual Design Differentiation

### Color Schemes by Role

**TMS Admin (Tarbiyyah Committee):**
- Primary: Islamic Green (#00916E)
- Secondary: Gold (#C5A572)
- Accent: Blue (#0066CC)

**Madrasah Portal:**
- Primary: Deep Blue (#003366)
- Secondary: Teal (#008080)
- Accent: Orange (#FF6B35)

**Teacher Portal:**
- Primary: Purple (#6A0DAD)
- Secondary: Light Purple (#B19CD9)
- Accent: Green (#4CAF50)

**Student Portal:**
- Primary: Sky Blue (#00A8E8)
- Secondary: Light Blue (#6DD3FF)
- Accent: Yellow (#FFC914)

**Parent Portal:**
- Primary: Warm Orange (#FF8C42)
- Secondary: Coral (#FF6F59)
- Accent: Teal (#00CFC1)

---

## Benefits of This Architecture

### 1. Clear Role Separation
- Each role has a tailored interface
- Navigation reflects role-specific tasks
- Reduces cognitive load (users only see relevant options)

### 2. Multitenancy
- Each madrasah operates independently
- Data isolation between tenants
- Tarbiyyah Committee maintains oversight

### 3. Single Codebase
- One Django application
- Shared infrastructure and deployment
- Easier maintenance and updates

### 4. Scalability
- Add new madaris without code changes
- Add users to existing madaris seamlessly
- System-wide updates roll out to all tenants

### 5. Security
- Role-based access control
- Tenant data isolation
- Centralized authentication

---

## Implementation Phases

### Phase 1: Core Infrastructure
1. Set up base template with role-based navbar rendering
2. Create all 5 navbar templates
3. Implement role-based decorators
4. Set up tenant middleware
5. Implement login with role-based redirect

### Phase 2: TMS Admin Portal
1. Homepage (system-wide overview)
2. About page
3. Madaris Information System:
   - Madrasah directory
   - Asatidz directory
   - Student directory
4. Support pages (placeholder)
5. Curriculum pages (placeholder)
6. Dashboards (system analytics)

### Phase 3: Madrasah Portal
1. School dashboard
2. Student management (enroll, directory, records)
3. Teacher management (add, directory, assignments)
4. Class management
5. Academic management
6. School reports

### Phase 4: Teacher Portal
1. Teacher dashboard
2. My Classes
3. Student views
4. Gradebook (grade entry)
5. Attendance marking
6. Curriculum access

### Phase 5: Student Portal
1. Student dashboard
2. My Classes
3. Grades view
4. Schedule view
5. Assignments view
6. Resources

### Phase 6: Parent Portal
1. Parent dashboard
2. Children management
3. Academic progress view
4. Attendance view
5. Messages
6. Calendar

---

## Summary

### Key Architectural Points

1. **One Django Application** - Single TMS system
2. **Five Different Navigation Bars** - Based on user role:
   - TMS Admin Navigation (TARBIYYAH_ADMIN)
   - Madrasah Navigation (MADRASAH_ADMIN, MUDER)
   - Teacher Navigation (ASATIDZ)
   - Student Navigation (STUDENT)
   - Parent Navigation (PARENT)
3. **Multitenant Architecture** - Each madrasah is a tenant
4. **Role-Based UI Rendering** - Different navbar templates per role
5. **Same Domain** - All users access `tms.tarbiyyah.gov.ph`
6. **Tenant Filtering** - Server-side data scoping by madrasah

---

**Document Status:** READY FOR IMPLEMENTATION
**Last Updated:** November 20, 2025
**Version:** 4.0
