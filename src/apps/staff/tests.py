"""
Comprehensive test suite for Staff application.
Covers unit tests, integration tests, and end-to-end workflows.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from datetime import datetime, timedelta, date
from decimal import Decimal

from .models import (
    Staff, StaffTeam, StaffSupervisor, StaffAttendance, StaffPerformance,
    Task, TaskCategory, TaskComment, TaskTimeLog, StaffWorkflowTemplate, WorkflowTask
)

User = get_user_model()


# ==============================
# UNIT TESTS - MODELS
# ==============================

class StaffModelTests(TestCase):
    """Unit tests for Staff model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='teststaff',
            email='staff@test.com',
            password='TestPass123!',
            user_type='staff',
            first_name='Test',
            last_name='Staff'
        )
    
    def test_staff_creation(self):
        """Test basic staff creation."""
        staff = Staff.objects.create(
            user=self.user,
            full_name='Test Staff Member',
            position='Software Developer',
            email='test@fahaniecares.ph',
            phone_number='09123456789',
            division='it_unit',
            employment_status='contractual',
            date_hired=timezone.now().date()
        )
        
        self.assertEqual(staff.full_name, 'Test Staff Member')
        self.assertEqual(staff.position, 'Software Developer')
        self.assertEqual(staff.division, 'it_unit')
        self.assertEqual(staff.employment_status, 'contractual')
        self.assertTrue(staff.is_active)
        self.assertTrue(staff.has_user_account)
    
    def test_staff_str_representation(self):
        """Test string representation."""
        staff = Staff.objects.create(
            full_name='John Doe',
            position='Manager'
        )
        self.assertEqual(str(staff), 'John Doe - Manager')
        
        staff_no_position = Staff.objects.create(full_name='Jane Doe')
        self.assertEqual(str(staff_no_position), 'Jane Doe - Staff')
    
    def test_display_name_property(self):
        """Test display_name property."""
        # Staff with user account
        staff_with_user = Staff.objects.create(
            user=self.user,
            full_name='Staff Name'
        )
        self.assertEqual(staff_with_user.display_name, 'Test Staff')
        
        # Staff without user account
        staff_without_user = Staff.objects.create(full_name='External Staff')
        self.assertEqual(staff_without_user.display_name, 'External Staff')
    
    def test_staff_without_user(self):
        """Test staff creation without user account."""
        staff = Staff.objects.create(
            full_name='External Consultant',
            position='Consultant',
            email='consultant@external.com',
            employment_status='consultant'
        )
        
        self.assertFalse(staff.has_user_account)
        self.assertEqual(staff.display_name, 'External Consultant')


class StaffTeamModelTests(TestCase):
    """Unit tests for StaffTeam model."""
    
    def setUp(self):
        self.staff1 = Staff.objects.create(full_name='Team Lead', position='Lead Developer')
        self.staff2 = Staff.objects.create(full_name='Developer 1', position='Developer')
        self.staff3 = Staff.objects.create(full_name='Developer 2', position='Developer')
    
    def test_team_creation(self):
        """Test team creation with members."""
        team = StaffTeam.objects.create(
            name='Development Team',
            description='Software development team',
            team_lead=self.staff1,
            division='it_unit'
        )
        team.members.add(self.staff1, self.staff2, self.staff3)
        
        self.assertEqual(team.name, 'Development Team')
        self.assertEqual(team.team_lead, self.staff1)
        self.assertEqual(team.members.count(), 3)
        self.assertTrue(team.is_active)
    
    def test_team_str_representation(self):
        """Test team string representation."""
        team = StaffTeam.objects.create(name='Test Team')
        self.assertEqual(str(team), 'Test Team')


class TaskModelTests(TestCase):
    """Unit tests for Task model."""
    
    def setUp(self):
        self.staff1 = Staff.objects.create(full_name='Assignee', position='Developer')
        self.staff2 = Staff.objects.create(full_name='Assigner', position='Manager')
        self.category = TaskCategory.objects.create(name='Development', color='#3B82F6')
    
    def test_task_creation(self):
        """Test basic task creation."""
        task = Task.objects.create(
            title='Implement new feature',
            description='Detailed description of the feature',
            assigned_to=self.staff1,
            assigned_by=self.staff2,
            category=self.category,
            priority='high',
            due_date=timezone.now() + timedelta(days=7),
            estimated_hours=Decimal('8.5')
        )
        
        self.assertEqual(task.title, 'Implement new feature')
        self.assertEqual(task.assigned_to, self.staff1)
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.progress_percentage, 0)
        self.assertFalse(task.is_overdue)
    
    def test_task_is_overdue(self):
        """Test is_overdue property."""
        # Future due date
        future_task = Task.objects.create(
            title='Future Task',
            assigned_to=self.staff1,
            due_date=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(future_task.is_overdue)
        
        # Past due date
        overdue_task = Task.objects.create(
            title='Overdue Task',
            assigned_to=self.staff1,
            due_date=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(overdue_task.is_overdue)
        
        # Completed task (not overdue even if past due)
        completed_task = Task.objects.create(
            title='Completed Task',
            assigned_to=self.staff1,
            due_date=timezone.now() - timedelta(days=1),
            status='completed'
        )
        self.assertFalse(completed_task.is_overdue)
    
    def test_days_until_due(self):
        """Test days_until_due property."""
        future_datetime = timezone.now() + timedelta(days=3)
        task = Task.objects.create(
            title='Test Task',
            assigned_to=self.staff1,
            due_date=future_datetime
        )
        # Use the actual calculated value since timezone.now() can vary slightly
        expected_days = (future_datetime - timezone.now()).days
        self.assertEqual(task.days_until_due, expected_days)
        
        # Task without due date
        no_due_task = Task.objects.create(
            title='No Due Date',
            assigned_to=self.staff1
        )
        self.assertIsNone(no_due_task.days_until_due)
    
    def test_mark_completed(self):
        """Test mark_completed method."""
        task = Task.objects.create(
            title='Test Task',
            assigned_to=self.staff1
        )
        
        task.mark_completed()
        
        self.assertEqual(task.status, 'completed')
        self.assertEqual(task.progress_percentage, 100)
        self.assertIsNotNone(task.completed_date)
    
    def test_task_dependencies(self):
        """Test task dependencies."""
        task1 = Task.objects.create(title='Task 1', assigned_to=self.staff1)
        task2 = Task.objects.create(title='Task 2', assigned_to=self.staff1)
        task3 = Task.objects.create(title='Task 3', assigned_to=self.staff1)
        
        # Task 3 depends on Task 1 and Task 2
        task3.depends_on.add(task1, task2)
        
        # Can't start Task 3 until dependencies are completed
        self.assertFalse(task3.can_start)
        
        # Complete Task 1
        task1.mark_completed()
        self.assertFalse(task3.can_start)  # Still waiting for Task 2
        
        # Complete Task 2
        task2.mark_completed()
        self.assertTrue(task3.can_start)  # Now can start


class StaffAttendanceModelTests(TestCase):
    """Unit tests for StaffAttendance model."""
    
    def setUp(self):
        self.staff = Staff.objects.create(full_name='Test Staff', position='Developer')
        self.supervisor = Staff.objects.create(full_name='Supervisor', position='Manager')
    
    def test_attendance_creation(self):
        """Test attendance record creation."""
        from datetime import time
        
        attendance = StaffAttendance.objects.create(
            staff=self.staff,
            date=timezone.now().date(),
            time_in=time(9, 0),
            time_out=time(17, 0),
            status='present',
            approved_by=self.supervisor,
            is_approved=True
        )
        
        self.assertEqual(attendance.staff, self.staff)
        self.assertEqual(attendance.status, 'present')
        self.assertTrue(attendance.is_approved)
    
    def test_hours_worked_calculation(self):
        """Test hours_worked property."""
        from datetime import time
        
        attendance = StaffAttendance.objects.create(
            staff=self.staff,
            date=timezone.now().date(),
            time_in=time(9, 0),
            time_out=time(17, 30),
            status='present'
        )
        
        self.assertEqual(attendance.hours_worked, 8.5)
    
    def test_unique_attendance_per_day(self):
        """Test that only one attendance record per staff per day is allowed."""
        today = timezone.now().date()
        
        StaffAttendance.objects.create(
            staff=self.staff,
            date=today,
            status='present'
        )
        
        # Try to create another record for same staff and date
        with self.assertRaises(IntegrityError):
            StaffAttendance.objects.create(
                staff=self.staff,
                date=today,
                status='late'
            )


# ==============================
# UNIT TESTS - VIEWS
# ==============================

class StaffDashboardViewTests(TestCase):
    """Unit tests for staff dashboard view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='staff'
        )
        
        # Create test staff
        self.staff = Staff.objects.create(
            user=self.user,
            full_name='Test Staff',
            position='Developer',
            division='it_unit',
            employment_status='contractual'
        )
        
        # Create test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Create test data for dashboard."""
        # Create additional staff
        for i in range(5):
            Staff.objects.create(
                full_name=f'Staff {i}',
                position=f'Position {i}',
                division='administrative_affairs' if i < 3 else 'communications',
                employment_status='contractual'
            )
        
        # Create tasks
        category = TaskCategory.objects.create(name='Development')
        for i in range(10):
            Task.objects.create(
                title=f'Task {i}',
                assigned_to=self.staff,
                category=category,
                status='pending' if i < 5 else 'completed',
                priority='high' if i < 2 else 'medium'
            )
        
        # Create attendance for today
        today = timezone.now().date()
        StaffAttendance.objects.create(
            staff=self.staff,
            date=today,
            status='present'
        )
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication."""
        response = self.client.get(reverse('staff:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_dashboard_loads_successfully(self):
        """Test dashboard loads with proper data."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        self.assertIn('total_staff', response.context)
        self.assertIn('division_stats', response.context)
        self.assertIn('task_stats', response.context)
        self.assertIn('attendance_summary', response.context)
        
        # Check that statistics are calculated correctly
        self.assertEqual(response.context['total_staff'], 6)  # 5 + self.staff
        self.assertGreater(len(response.context['division_stats']), 0)
        
        # Check task statistics
        task_stats = response.context['task_stats']
        self.assertEqual(task_stats['total_tasks'], 10)
        self.assertEqual(task_stats['pending_tasks'], 5)
        self.assertEqual(task_stats['completed_tasks'], 5)
    
    def test_dashboard_content_rendering(self):
        """Test dashboard template content."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:dashboard'))
        
        # Check that key elements are rendered
        self.assertContains(response, 'Staff Management Dashboard')
        self.assertContains(response, 'Total Active Staff')
        self.assertContains(response, 'Task Status Overview')
        self.assertContains(response, 'My Tasks')
        self.assertContains(response, 'Quick Actions')
    
    def test_dashboard_my_tasks_section(self):
        """Test the 'My Tasks' section for logged-in staff."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:dashboard'))
        
        # Should show user's tasks
        self.assertIn('my_tasks', response.context)
        self.assertIn('current_staff', response.context)
        self.assertEqual(response.context['current_staff'], self.staff)


class StaffListViewTests(TestCase):
    """Unit tests for staff list view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            user_type='staff'
        )
        
        # Create test staff
        for i in range(15):
            Staff.objects.create(
                full_name=f'Staff {i}',
                position=f'Position {i}',
                email=f'staff{i}@test.com',
                division='it_unit' if i < 5 else 'communications',
                employment_status='contractual' if i < 10 else 'consultant',
                office='main_office' if i < 8 else 'satellite_office'
            )
    
    def test_staff_list_requires_login(self):
        """Test that staff list requires authentication."""
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_staff_list_pagination(self):
        """Test staff list pagination."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check pagination (paginate_by = 20, so all 15 should be on page 1)
        self.assertContains(response, 'Staff 0')
        self.assertContains(response, 'Staff 14')
    
    def test_staff_list_search(self):
        """Test staff list search functionality."""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Search by name
        response = self.client.get(reverse('staff:staff_list'), {'search': 'Staff 5'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff 5')
        self.assertNotContains(response, 'Staff 1')
        
        # Search by position
        response = self.client.get(reverse('staff:staff_list'), {'search': 'Position 3'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff 3')
    
    def test_staff_list_filters(self):
        """Test staff list filtering."""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Filter by division
        response = self.client.get(reverse('staff:staff_list'), {'division': 'it_unit'})
        self.assertEqual(response.status_code, 200)
        # Should show only IT unit staff (Staff 0-4)
        self.assertContains(response, 'Staff 0')
        self.assertContains(response, 'Staff 4')
        self.assertNotContains(response, 'Staff 5')
        
        # Filter by employment status
        response = self.client.get(reverse('staff:staff_list'), {'employment_status': 'consultant'})
        self.assertEqual(response.status_code, 200)
        # Should show only consultants (Staff 10-14)
        self.assertContains(response, 'Staff 10')
        self.assertNotContains(response, 'Staff 9')


class StaffDetailViewTests(TestCase):
    """Unit tests for staff detail view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            user_type='staff'
        )
        
        self.staff = Staff.objects.create(
            full_name='Test Staff',
            position='Developer',
            email='test@test.com',
            division='it_unit'
        )
        
        # Create attendance records
        for i in range(5):
            StaffAttendance.objects.create(
                staff=self.staff,
                date=timezone.now().date() - timedelta(days=i),
                status='present'
            )
    
    def test_staff_detail_requires_login(self):
        """Test that staff detail requires authentication."""
        response = self.client.get(reverse('staff:staff_detail', kwargs={'pk': self.staff.pk}))
        self.assertEqual(response.status_code, 302)
    
    def test_staff_detail_loads_successfully(self):
        """Test staff detail view loads with proper data."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:staff_detail', kwargs={'pk': self.staff.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Check context includes staff and related data
        self.assertEqual(response.context['staff_member'], self.staff)
        self.assertIn('recent_attendance', response.context)
        self.assertEqual(len(response.context['recent_attendance']), 5)
    
    def test_staff_detail_404_for_invalid_staff(self):
        """Test 404 for non-existent staff."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:staff_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)


class TaskManagementViewTests(TestCase):
    """Unit tests for task management views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            user_type='staff'
        )
        
        self.staff = Staff.objects.create(
            user=self.user,
            full_name='Test Staff',
            position='Developer'
        )
        
        self.other_staff = Staff.objects.create(
            full_name='Other Staff',
            position='Manager'
        )
        
        self.category = TaskCategory.objects.create(name='Development')
        
        # Create test tasks
        for i in range(5):
            Task.objects.create(
                title=f'Task {i}',
                assigned_to=self.staff if i < 3 else self.other_staff,
                assigned_by=self.other_staff,
                category=self.category,
                priority='high' if i == 0 else 'medium',
                status='pending' if i < 2 else 'completed'
            )
    
    def test_task_list_view(self):
        """Test task list view."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:task_list'))
        self.assertEqual(response.status_code, 200)
        
        # Should show all tasks
        self.assertContains(response, 'Task 0')
        self.assertContains(response, 'Task 4')
    
    def test_my_tasks_view(self):
        """Test my tasks view."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('staff:my_tasks'))
        self.assertEqual(response.status_code, 200)
        
        # Should show only user's active tasks (pending and in_progress)
        # Task 0 and Task 1 are 'pending', Task 2 is 'completed' (filtered out by default)
        self.assertContains(response, 'Task 0')  # pending - should appear
        self.assertContains(response, 'Task 1')  # pending - should appear
        self.assertNotContains(response, 'Task 2')  # completed - filtered out
        self.assertNotContains(response, 'Task 3')  # Assigned to other staff
        
        # Test with status filter to show completed tasks
        response = self.client.get(reverse('staff:my_tasks') + '?status=completed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 2')  # completed - should appear with filter
        self.assertNotContains(response, 'Task 0')  # pending - filtered out
    
    def test_task_creation(self):
        """Test task creation."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.post(reverse('staff:task_create'), {
            'title': 'New Test Task',
            'description': 'Task description',
            'assigned_to': self.staff.id,
            'category': self.category.id,
            'priority': 'high',
            'due_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'estimated_hours': '8.5'
        })
        
        # Should redirect to task detail
        self.assertEqual(response.status_code, 302)
        
        # Verify task was created
        task = Task.objects.get(title='New Test Task')
        self.assertEqual(task.assigned_to, self.staff)
        self.assertEqual(task.assigned_by, self.staff)
        self.assertEqual(task.priority, 'high')


# ==============================
# INTEGRATION TESTS
# ==============================

class StaffDashboardIntegrationTests(TestCase):
    """Integration tests for staff dashboard workflows."""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.manager_user = User.objects.create_user(
            username='manager',
            password='TestPass123!',
            user_type='staff'
        )
        self.staff_user = User.objects.create_user(
            username='developer',
            password='TestPass123!',
            user_type='staff'
        )
        
        # Create staff profiles
        self.manager = Staff.objects.create(
            user=self.manager_user,
            full_name='Manager User',
            position='Team Manager',
            division='it_unit',
            employment_status='coterminous'
        )
        self.developer = Staff.objects.create(
            user=self.staff_user,
            full_name='Developer User',
            position='Software Developer',
            division='it_unit',
            employment_status='contractual'
        )
        
        self.setup_comprehensive_test_data()
    
    def setup_comprehensive_test_data(self):
        """Setup comprehensive test data."""
        # Create teams
        self.dev_team = StaffTeam.objects.create(
            name='Development Team',
            description='Software development team',
            team_lead=self.manager,
            division='it_unit'
        )
        self.dev_team.members.add(self.manager, self.developer)
        
        # Create task categories
        self.dev_category = TaskCategory.objects.create(name='Development', color='#3B82F6')
        self.bug_category = TaskCategory.objects.create(name='Bug Fix', color='#EF4444')
        
        # Create tasks with different statuses and priorities
        self.urgent_task = Task.objects.create(
            title='Critical Bug Fix',
            description='Fix critical production bug',
            assigned_to=self.developer,
            assigned_by=self.manager,
            category=self.bug_category,
            priority='urgent',
            status='in_progress',
            due_date=timezone.now() + timedelta(hours=2),
            estimated_hours=Decimal('4.0')
        )
        
        self.feature_task = Task.objects.create(
            title='Implement New Feature',
            description='Add new dashboard feature',
            assigned_to=self.developer,
            assigned_by=self.manager,
            category=self.dev_category,
            priority='high',
            status='pending',
            due_date=timezone.now() + timedelta(days=5),
            estimated_hours=Decimal('16.0')
        )
        
        self.completed_task = Task.objects.create(
            title='Setup CI/CD Pipeline',
            description='Configure automated deployment',
            assigned_to=self.developer,
            assigned_by=self.manager,
            category=self.dev_category,
            priority='medium',
            status='completed',
            completed_date=timezone.now() - timedelta(days=1),
            estimated_hours=Decimal('8.0'),
            actual_hours=Decimal('6.5')
        )
        
        # Create attendance records
        today = timezone.now().date()
        for i in range(7):
            StaffAttendance.objects.create(
                staff=self.developer,
                date=today - timedelta(days=i),
                status='present' if i < 5 else 'absent',
                time_in=datetime.strptime('09:00', '%H:%M').time() if i < 5 else None,
                time_out=datetime.strptime('17:30', '%H:%M').time() if i < 5 else None
            )
        
        # Create performance evaluation
        StaffPerformance.objects.create(
            staff=self.developer,
            evaluation_period='quarterly',
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            overall_rating=4,
            quality_of_work=4,
            punctuality=5,
            teamwork=4,
            communication=3,
            initiative=4,
            evaluated_by=self.manager,
            evaluation_date=timezone.now().date() - timedelta(days=30)
        )
    
    def test_dashboard_statistics_integration(self):
        """Test dashboard statistics calculation and display."""
        self.client.login(username='manager', password='TestPass123!')
        
        response = self.client.get(reverse('staff:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify statistics
        context = response.context
        
        # Staff statistics
        self.assertEqual(context['total_staff'], 2)
        division_stats = context['division_stats']
        it_division = next((d for d in division_stats if d['division'] == 'it_unit'), None)
        self.assertIsNotNone(it_division)
        self.assertEqual(it_division['count'], 2)
        
        # Task statistics
        task_stats = context['task_stats']
        self.assertEqual(task_stats['total_tasks'], 3)
        self.assertEqual(task_stats['pending_tasks'], 1)
        self.assertEqual(task_stats['in_progress_tasks'], 1)
        self.assertEqual(task_stats['completed_tasks'], 1)
        
        # Urgent tasks
        urgent_tasks = context['urgent_tasks']
        self.assertEqual(len(urgent_tasks), 2)  # urgent + high priority
        
        # Attendance summary
        attendance_summary = context['attendance_summary']
        self.assertEqual(attendance_summary['present'], 1)  # Only developer present today
    
    def test_staff_workflow_integration(self):
        """Test complete staff management workflow."""
        # Manager logs in
        self.client.login(username='manager', password='TestPass123!')
        
        # 1. View staff list
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Developer User')
        
        # 2. View developer's detail
        response = self.client.get(reverse('staff:staff_detail', kwargs={'pk': self.developer.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Developer')
        
        # 3. Create new task for developer
        response = self.client.post(reverse('staff:task_create'), {
            'title': 'Code Review',
            'description': 'Review pull requests',
            'assigned_to': self.developer.id,
            'category': self.dev_category.id,
            'priority': 'medium',
            'estimated_hours': '2.0'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify task creation
        new_task = Task.objects.get(title='Code Review')
        self.assertEqual(new_task.assigned_to, self.developer)
        self.assertEqual(new_task.assigned_by, self.manager)
        
        # 4. Switch to developer view
        self.client.login(username='developer', password='TestPass123!')
        
        # 5. View my tasks
        response = self.client.get(reverse('staff:my_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Code Review')
        self.assertContains(response, 'Critical Bug Fix')
        
        # 6. View task detail and add comment
        response = self.client.post(
            reverse('staff:task_detail', kwargs={'task_id': new_task.id}),
            {'comment': 'Started working on this task'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify comment was added
        comment = TaskComment.objects.get(task=new_task)
        self.assertEqual(comment.comment, 'Started working on this task')
        self.assertEqual(comment.author, self.developer)
    
    def test_attendance_tracking_integration(self):
        """Test attendance tracking workflow."""
        self.client.login(username='manager', password='TestPass123!')
        
        # 1. View attendance tracking page
        response = self.client.get(reverse('staff:attendance_tracking'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Record attendance for staff
        today = timezone.now().date()
        response = self.client.post(reverse('staff:attendance_tracking'), {
            'staff_id': self.manager.id,
            'status': 'present',
            'time_in': '08:30',
            'time_out': '17:00',
            'notes': 'Regular work day'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Attendance recorded for')
        
        # 3. Verify attendance was recorded
        attendance = StaffAttendance.objects.get(staff=self.manager, date=today)
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.hours_worked, 8.5)
    
    def test_performance_overview_integration(self):
        """Test performance overview functionality."""
        self.client.login(username='manager', password='TestPass123!')
        
        response = self.client.get(reverse('staff:performance_overview'))
        self.assertEqual(response.status_code, 200)
        
        # Check that performance data is displayed
        self.assertContains(response, 'Developer User')
        
        # Verify context data
        context = response.context
        self.assertIn('division_performance', context)
        self.assertIn('latest_evaluations', context)
        self.assertEqual(context['total_evaluations'], 1)


# ==============================
# END-TO-END TESTS
# ==============================

class StaffE2EWorkflowTests(TestCase):
    """End-to-end tests for complete staff management workflows."""
    
    def setUp(self):
        self.client = Client()
        
        # Create comprehensive user setup
        self.mp_user = User.objects.create_user(
            username='mp_user',
            password='MPPass123!',
            user_type='mp',
            first_name='MP',
            last_name='Uy-Oyod'
        )
        
        self.chief_staff_user = User.objects.create_user(
            username='chief_staff',
            password='ChiefPass123!',
            user_type='chief_of_staff',
            first_name='Chief',
            last_name='Staff'
        )
        
        self.coordinator_user = User.objects.create_user(
            username='coordinator',
            password='CoordPass123!',
            user_type='coordinator',
            first_name='Area',
            last_name='Coordinator'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff_member',
            password='StaffPass123!',
            user_type='staff',
            first_name='Regular',
            last_name='Staff'
        )
        
        # Create staff profiles
        self.mp_staff = Staff.objects.create(
            user=self.mp_user,
            full_name='MP Fahanie Uy-Oyod',
            position='Member of Parliament',
            division='mp_office',
            employment_status='coterminous',
            date_hired=date(2022, 1, 1)
        )
        
        self.chief = Staff.objects.create(
            user=self.chief_staff_user,
            full_name='Chief of Staff',
            position='Chief of Staff',
            division='administrative_affairs',
            employment_status='coterminous',
            date_hired=date(2022, 1, 15)
        )
        
        self.coordinator = Staff.objects.create(
            user=self.coordinator_user,
            full_name='Area Coordinator',
            position='Field Coordinator',
            division='administrative_affairs',
            employment_status='contractual',
            date_hired=date(2023, 3, 1)
        )
        
        self.staff_member = Staff.objects.create(
            user=self.staff_user,
            full_name='Regular Staff Member',
            position='Administrative Assistant',
            division='administrative_affairs',
            employment_status='contractual',
            date_hired=date(2023, 6, 1)
        )
        
        self.setup_e2e_test_data()
    
    def setup_e2e_test_data(self):
        """Setup comprehensive test data for E2E scenarios."""
        # Create organizational structure
        StaffSupervisor.objects.create(staff=self.chief, supervisor=self.mp_staff)
        StaffSupervisor.objects.create(staff=self.coordinator, supervisor=self.chief)
        StaffSupervisor.objects.create(staff=self.staff_member, supervisor=self.coordinator)
        
        # Create teams
        admin_team = StaffTeam.objects.create(
            name='Administrative Team',
            description='Main administrative operations team',
            team_lead=self.chief,
            division='administrative_affairs'
        )
        admin_team.members.add(self.chief, self.coordinator, self.staff_member)
        
        # Create task categories
        categories = [
            TaskCategory.objects.create(name='Administrative', color='#3B82F6'),
            TaskCategory.objects.create(name='Field Work', color='#10B981'),
            TaskCategory.objects.create(name='Planning', color='#8B5CF6'),
            TaskCategory.objects.create(name='Emergency', color='#EF4444'),
        ]
        
        # Create realistic task scenarios
        self.create_realistic_tasks(categories)
        
        # Create attendance patterns
        self.create_attendance_patterns()
        
        # Create performance evaluations
        self.create_performance_evaluations()
    
    def create_realistic_tasks(self, categories):
        """Create realistic task scenarios."""
        admin_cat, field_cat, planning_cat, emergency_cat = categories
        
        # Emergency task from MP
        Task.objects.create(
            title='Urgent: Coordinate Disaster Response',
            description='Typhoon approaching, coordinate evacuation and relief operations',
            assigned_to=self.chief,
            assigned_by=self.mp_staff,
            category=emergency_cat,
            priority='urgent',
            status='in_progress',
            due_date=timezone.now() + timedelta(hours=6),
            estimated_hours=Decimal('12.0')
        )
        
        # Planning task delegated down
        planning_task = Task.objects.create(
            title='Plan Community Health Program',
            description='Develop implementation plan for Q2 health initiatives',
            assigned_to=self.coordinator,
            assigned_by=self.chief,
            category=planning_cat,
            priority='high',
            status='pending',
            due_date=timezone.now() + timedelta(days=14),
            estimated_hours=Decimal('20.0')
        )
        
        # Field work task
        Task.objects.create(
            title='Conduct Barangay Visits',
            description='Visit 5 barangays to assess infrastructure needs',
            assigned_to=self.coordinator,
            assigned_by=self.chief,
            category=field_cat,
            priority='medium',
            status='in_progress',
            due_date=timezone.now() + timedelta(days=7),
            estimated_hours=Decimal('16.0')
        )
        
        # Administrative task for staff
        Task.objects.create(
            title='Update Constituent Database',
            description='Update contact information for all registered constituents',
            assigned_to=self.staff_member,
            assigned_by=self.coordinator,
            category=admin_cat,
            priority='medium',
            status='pending',
            due_date=timezone.now() + timedelta(days=10),
            estimated_hours=Decimal('8.0')
        )
        
        # Completed task with time log
        completed_task = Task.objects.create(
            title='Monthly Report Preparation',
            description='Prepare monthly progress report for MP',
            assigned_to=self.staff_member,
            assigned_by=self.coordinator,
            category=admin_cat,
            priority='medium',
            status='completed',
            completed_date=timezone.now() - timedelta(days=2),
            estimated_hours=Decimal('6.0'),
            actual_hours=Decimal('5.5')
        )
        
        # Add time log for completed task
        TaskTimeLog.objects.create(
            task=completed_task,
            staff=self.staff_member,
            start_time=timezone.now() - timedelta(days=2, hours=8),
            end_time=timezone.now() - timedelta(days=2, hours=2, minutes=30),
            description='Compiled data and wrote report'
        )
    
    def create_attendance_patterns(self):
        """Create realistic attendance patterns."""
        today = timezone.now().date()
        
        # Create 30 days of attendance for all staff
        for staff in [self.mp_staff, self.chief, self.coordinator, self.staff_member]:
            for i in range(30):
                attendance_date = today - timedelta(days=i)
                
                # Skip weekends
                if attendance_date.weekday() >= 5:
                    continue
                
                # Determine status based on patterns
                if staff == self.mp_staff:
                    # MP has varied schedule
                    status = 'present' if i % 3 != 0 else 'official_business'
                elif i < 2:  # Last 2 days
                    status = 'present'
                elif i < 5:  # Days 2-4
                    status = 'present' if staff != self.coordinator else 'late'
                else:
                    status = 'present'
                
                time_in = datetime.strptime('08:30', '%H:%M').time() if status in ['present', 'late'] else None
                time_out = datetime.strptime('17:00', '%H:%M').time() if status in ['present', 'late'] else None
                
                if status == 'late':
                    time_in = datetime.strptime('09:30', '%H:%M').time()
                
                StaffAttendance.objects.create(
                    staff=staff,
                    date=attendance_date,
                    status=status,
                    time_in=time_in,
                    time_out=time_out,
                    approved_by=self.chief if staff != self.chief else self.mp_staff,
                    is_approved=True
                )
    
    def create_performance_evaluations(self):
        """Create performance evaluation records."""
        # Quarterly evaluations
        for quarter in range(1, 4):  # Q1, Q2, Q3
            period_start = date(2024, (quarter-1)*3 + 1, 1)
            if quarter == 3:
                period_end = date(2024, 9, 30)
            else:
                period_end = date(2024, quarter*3, 30)
            
            # Chief evaluates coordinator
            StaffPerformance.objects.create(
                staff=self.coordinator,
                evaluation_period='quarterly',
                period_start=period_start,
                period_end=period_end,
                overall_rating=4,
                quality_of_work=4,
                punctuality=3 if quarter == 3 else 4,  # Late issues in Q3
                teamwork=5,
                communication=4,
                initiative=4,
                evaluated_by=self.chief,
                evaluation_date=period_end + timedelta(days=7)
            )
            
            # Coordinator evaluates staff member
            StaffPerformance.objects.create(
                staff=self.staff_member,
                evaluation_period='quarterly',
                period_start=period_start,
                period_end=period_end,
                overall_rating=4,
                quality_of_work=5,
                punctuality=5,
                teamwork=4,
                communication=3,
                initiative=3,
                evaluated_by=self.coordinator,
                evaluation_date=period_end + timedelta(days=7)
            )
    
    def test_mp_oversight_workflow(self):
        """Test MP's complete oversight workflow."""
        # 1. MP logs in and views dashboard
        self.client.login(username='mp_user', password='MPPass123!')
        
        response = self.client.get(reverse('staff:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify MP sees comprehensive overview
        self.assertContains(response, 'Staff Management Dashboard')
        
        context = response.context
        self.assertEqual(context['total_staff'], 4)
        
        # Check urgent tasks are visible
        urgent_tasks = context['urgent_tasks']
        self.assertGreater(len(urgent_tasks), 0)
        disaster_task = next((t for t in urgent_tasks if 'Disaster Response' in t.title), None)
        self.assertIsNotNone(disaster_task)
        
        # 2. Review all staff
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chief of Staff')
        self.assertContains(response, 'Area Coordinator')
        self.assertContains(response, 'Regular Staff Member')
        
        # 3. Review performance overview
        response = self.client.get(reverse('staff:performance_overview'))
        self.assertEqual(response.status_code, 200)
        
        # Should see performance data
        context = response.context
        self.assertGreater(context['total_evaluations'], 0)
        
        # 4. Check specific staff performance
        response = self.client.get(reverse('staff:staff_detail', kwargs={'pk': self.coordinator.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Area Coordinator')
        
        # Should see attendance and performance data
        self.assertIn('recent_attendance', response.context)
        self.assertIn('recent_evaluations', response.context)
        
        # 5. Create high-priority task
        response = self.client.post(reverse('staff:task_create'), {
            'title': 'Prepare Emergency Response Plan',
            'description': 'Update and test emergency response procedures',
            'assigned_to': self.chief.id,
            'priority': 'urgent',
            'due_date': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
            'estimated_hours': '16.0'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify task creation
        new_task = Task.objects.get(title='Prepare Emergency Response Plan')
        self.assertEqual(new_task.assigned_by, self.mp_staff)
        self.assertEqual(new_task.priority, 'urgent')
    
    def test_hierarchical_task_delegation(self):
        """Test task delegation through organizational hierarchy."""
        # 1. Chief of Staff logs in
        self.client.login(username='chief_staff', password='ChiefPass123!')
        
        # 2. Create task and assign to coordinator
        response = self.client.post(reverse('staff:task_create'), {
            'title': 'Organize Community Meeting',
            'description': 'Set up town hall meeting for next month',
            'assigned_to': self.coordinator.id,
            'priority': 'high',
            'due_date': (timezone.now() + timedelta(days=21)).strftime('%Y-%m-%dT%H:%M'),
            'estimated_hours': '12.0'
        })
        self.assertEqual(response.status_code, 302)
        
        parent_task = Task.objects.get(title='Organize Community Meeting')
        
        # 3. Switch to coordinator
        self.client.login(username='coordinator', password='CoordPass123!')
        
        # 4. Coordinator sees task and creates subtasks
        response = self.client.get(reverse('staff:my_tasks'))
        self.assertContains(response, 'Organize Community Meeting')
        
        # Create subtask for staff member
        response = self.client.post(reverse('staff:task_create'), {
            'title': 'Book Venue for Community Meeting',
            'description': 'Reserve appropriate venue and setup',
            'assigned_to': self.staff_member.id,
            'priority': 'medium',
            'due_date': (timezone.now() + timedelta(days=14)).strftime('%Y-%m-%dT%H:%M'),
            'estimated_hours': '4.0'
        })
        self.assertEqual(response.status_code, 302)
        
        subtask = Task.objects.get(title='Book Venue for Community Meeting')
        
        # 5. Switch to staff member
        self.client.login(username='staff_member', password='StaffPass123!')
        
        # 6. Staff member sees and completes subtask
        response = self.client.get(reverse('staff:my_tasks'))
        self.assertContains(response, 'Book Venue for Community Meeting')
        
        # Complete the task
        response = self.client.post(
            reverse('staff:task_update_status', kwargs={'task_id': subtask.id}),
            {'status': 'completed', 'progress': '100'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify task completion
        subtask.refresh_from_db()
        self.assertEqual(subtask.status, 'completed')
        self.assertEqual(subtask.progress_percentage, 100)
    
    def test_attendance_management_workflow(self):
        """Test complete attendance management workflow."""
        # 1. Coordinator logs in and checks attendance
        self.client.login(username='coordinator', password='CoordPass123!')
        
        response = self.client.get(reverse('staff:attendance_tracking'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Record today's attendance
        today = timezone.now().date()
        response = self.client.post(reverse('staff:attendance_tracking'), {
            'staff_id': self.staff_member.id,
            'status': 'late',
            'time_in': '09:30',
            'time_out': '17:00',
            'notes': 'Traffic issues'
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify attendance recorded
        attendance = StaffAttendance.objects.get(staff=self.staff_member, date=today)
        self.assertEqual(attendance.status, 'late')
        
        # 3. Generate attendance report
        response = self.client.get(reverse('staff:attendance_report'), {
            'start_date': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, 200)
        
        # Should show attendance statistics
        self.assertIn('staff_attendance', response.context)
    
    def test_performance_evaluation_workflow(self):
        """Test performance evaluation workflow."""
        # 1. Chief of Staff reviews team performance
        self.client.login(username='chief_staff', password='ChiefPass123!')
        
        response = self.client.get(reverse('staff:performance_overview'))
        self.assertEqual(response.status_code, 200)
        
        # Should see evaluation data
        context = response.context
        self.assertIn('division_performance', context)
        self.assertIn('latest_evaluations', context)
        
        # Check for administrative division performance
        division_performance = context['division_performance']
        admin_performance = next(
            (d for d in division_performance if d['staff__division'] == 'administrative_affairs'),
            None
        )
        self.assertIsNotNone(admin_performance)
        
        # 2. View individual staff performance
        response = self.client.get(reverse('staff:staff_detail', kwargs={'pk': self.coordinator.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Should show performance evaluations
        evaluations = response.context['recent_evaluations']
        self.assertGreater(len(evaluations), 0)
        
        # Verify evaluation details
        latest_eval = evaluations[0]
        self.assertEqual(latest_eval.staff, self.coordinator)
        self.assertEqual(latest_eval.evaluated_by, self.chief)
    
    def test_database_of_staff_access_control(self):
        """Test access control for database of staff functionality."""
        # Test different user types accessing staff database
        
        # 1. MP should have full access
        self.client.login(username='mp_user', password='MPPass123!')
        
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Export to CSV')  # MP can export
        
        # 2. Chief of Staff should have access
        self.client.login(username='chief_staff', password='ChiefPass123!')
        
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Coordinator should have limited access
        self.client.login(username='coordinator', password='CoordPass123!')
        
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Regular staff should have limited access
        self.client.login(username='staff_member', password='StaffPass123!')
        
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        
        # But cannot access sensitive functions
        response = self.client.get(reverse('staff:export_staff_csv'))
        # Should be restricted or redirected based on permissions
        self.assertIn(response.status_code, [302, 403])
    
    def test_complete_staff_lifecycle(self):
        """Test complete staff member lifecycle management."""
        # 1. Create new staff member (simulating HR process)
        self.client.login(username='chief_staff', password='ChiefPass123!')
        
        # Create user account first
        new_user = User.objects.create_user(
            username='new_staff',
            email='newstaff@fahaniecares.ph',
            password='NewStaff123!',
            user_type='staff',
            first_name='New',
            last_name='Employee'
        )
        
        # Create staff profile
        new_staff = Staff.objects.create(
            user=new_user,
            full_name='New Employee',
            position='Junior Assistant',
            email='newstaff@fahaniecares.ph',
            phone_number='09123456789',
            division='administrative_affairs',
            employment_status='contractual',
            date_hired=timezone.now().date(),
            duties_responsibilities='Administrative support tasks'
        )
        
        # 2. Assign to team
        admin_team = StaffTeam.objects.get(name='Administrative Team')
        admin_team.members.add(new_staff)
        
        # 3. Set up supervisor relationship
        StaffSupervisor.objects.create(staff=new_staff, supervisor=self.coordinator)
        
        # 4. Assign initial tasks
        orientation_task = Task.objects.create(
            title='Complete Staff Orientation',
            description='Complete orientation program and training',
            assigned_to=new_staff,
            assigned_by=self.chief,
            priority='high',
            due_date=timezone.now() + timedelta(days=5),
            estimated_hours=Decimal('16.0')
        )
        
        # 5. Switch to new staff and complete onboarding
        self.client.login(username='new_staff', password='NewStaff123!')
        
        response = self.client.get(reverse('staff:my_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Staff Orientation')
        
        # 6. Mark orientation complete
        response = self.client.post(
            reverse('staff:task_update_status', kwargs={'task_id': orientation_task.id}),
            {'status': 'completed', 'progress': '100'}
        )
        self.assertEqual(response.status_code, 200)
        
        # 7. Verify in dashboard statistics
        self.client.login(username='chief_staff', password='ChiefPass123!')
        
        response = self.client.get(reverse('staff:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Should show updated staff count
        self.assertEqual(response.context['total_staff'], 5)  # Original 4 + new staff
        
        # Should show new staff in recent hires
        recent_hires = response.context['recent_hires']
        new_hire_found = any(staff.full_name == 'New Employee' for staff in recent_hires)
        self.assertTrue(new_hire_found)


class StaffSystemIntegrationTests(TestCase):
    """Integration tests between staff system and other #FahanieCares modules."""
    
    def setUp(self):
        self.client = Client()
        
        # Create staff users
        self.coordinator_user = User.objects.create_user(
            username='coordinator',
            password='TestPass123!',
            user_type='coordinator'
        )
        
        # Create MP user for export functionality test
        self.mp_user = User.objects.create_user(
            username='mp_user',
            password='TestPass123!',
            user_type='mp'
        )
        
        self.staff = Staff.objects.create(
            user=self.coordinator_user,
            full_name='System Coordinator',
            position='Area Coordinator',
            division='administrative_affairs'
        )
    
    def test_staff_dashboard_navigation_integration(self):
        """Test integration with main navigation system."""
        self.client.login(username='coordinator', password='TestPass123!')
        
        # Access dashboard
        response = self.client.get(reverse('staff:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify navigation elements are present
        self.assertContains(response, 'Staff Management Dashboard')
        self.assertContains(response, 'Quick Actions')
        
        # Test navigation to other staff functions
        staff_functions = [
            reverse('staff:staff_list'),
            reverse('staff:task_list'),
            reverse('staff:attendance_tracking'),
            reverse('staff:performance_overview')
        ]
        
        for url in staff_functions:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_staff_profile_integration(self):
        """Test staff profile integration with user system."""
        self.client.login(username='coordinator', password='TestPass123!')
        
        # Access staff profile
        response = self.client.get(reverse('staff:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Should show user's staff profile
        self.assertContains(response, 'System Coordinator')
        self.assertContains(response, 'Area Coordinator')
        
        # Test profile editing
        response = self.client.post(reverse('staff:edit_profile'), {
            'email': 'updated@fahaniecares.ph',
            'phone_number': '09987654321',
            'bio': 'Updated bio information'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify profile was updated
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.email, 'updated@fahaniecares.ph')
        self.assertEqual(self.staff.phone_number, '09987654321')
    
    def test_export_functionality_integration(self):
        """Test CSV export functionality."""
        self.client.login(username='mp_user', password='TestPass123!')
        
        response = self.client.get(reverse('staff:export_staff_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Verify CSV content includes staff data
        content = response.content.decode('utf-8')
        self.assertIn('System Coordinator', content)
        self.assertIn('Area Coordinator', content)


# ==============================
# PERFORMANCE AND EDGE CASE TESTS
# ==============================

class StaffPerformanceTests(TestCase):
    """Performance tests for staff system with large datasets."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            user_type='staff'
        )
        self.client.login(username='testuser', password='TestPass123!')
    
    def test_dashboard_performance_with_large_dataset(self):
        """Test dashboard performance with large amounts of data."""
        # Create large dataset
        staff_members = []
        for i in range(100):
            staff = Staff.objects.create(
                full_name=f'Staff Member {i}',
                position=f'Position {i}',
                division='administrative_affairs' if i < 50 else 'communications',
                employment_status='contractual'
            )
            staff_members.append(staff)
        
        # Create many tasks
        category = TaskCategory.objects.create(name='Test Category')
        for i in range(500):
            Task.objects.create(
                title=f'Task {i}',
                assigned_to=staff_members[i % 100],
                category=category,
                status='pending' if i < 250 else 'completed'
            )
        
        # Create attendance records
        today = timezone.now().date()
        for staff in staff_members[:50]:  # Only for first 50 to save time
            StaffAttendance.objects.create(
                staff=staff,
                date=today,
                status='present'
            )
        
        # Test dashboard load time
        import time
        start_time = time.time()
        response = self.client.get(reverse('staff:dashboard'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 5.0)  # Should load within 5 seconds
        
        # Verify data integrity
        context = response.context
        self.assertEqual(context['total_staff'], 100)
        self.assertEqual(context['task_stats']['total_tasks'], 500)


class StaffEdgeCaseTests(TestCase):
    """Edge case tests for staff system."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            user_type='staff'
        )
        self.staff = Staff.objects.create(
            user=self.user,
            full_name='Test Staff'
        )
        self.client.login(username='testuser', password='TestPass123!')
    
    def test_staff_without_user_account(self):
        """Test handling of staff members without user accounts."""
        # Create staff without user
        external_staff = Staff.objects.create(
            full_name='External Consultant',
            position='Consultant',
            employment_status='consultant'
        )
        
        # Should appear in staff list
        response = self.client.get(reverse('staff:staff_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'External Consultant')
        
        # Should be viewable in detail
        response = self.client.get(reverse('staff:staff_detail', kwargs={'pk': external_staff.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'External Consultant')
    
    def test_task_with_circular_dependencies(self):
        """Test handling of invalid circular task dependencies."""
        task1 = Task.objects.create(title='Task 1', assigned_to=self.staff)
        task2 = Task.objects.create(title='Task 2', assigned_to=self.staff)
        
        # Create circular dependency
        task1.depends_on.add(task2)
        task2.depends_on.add(task1)
        
        # Both tasks should not be able to start
        self.assertFalse(task1.can_start)
        self.assertFalse(task2.can_start)
    
    def test_attendance_edge_cases(self):
        """Test edge cases in attendance tracking."""
        today = timezone.now().date()
        
        # Test overnight shift
        attendance = StaffAttendance.objects.create(
            staff=self.staff,
            date=today,
            time_in=datetime.strptime('23:00', '%H:%M').time(),
            time_out=datetime.strptime('07:00', '%H:%M').time(),
            status='present'
        )
        
        # Should calculate 8 hours for overnight shift
        self.assertEqual(attendance.hours_worked, 8.0)
    
    def test_task_without_due_date(self):
        """Test tasks without due dates."""
        task = Task.objects.create(
            title='No Due Date Task',
            assigned_to=self.staff
        )
        
        self.assertFalse(task.is_overdue)
        self.assertIsNone(task.days_until_due)
    
    def test_empty_dashboard_data(self):
        """Test dashboard with minimal data."""
        # Delete all created data
        Staff.objects.all().delete()
        Task.objects.all().delete()
        StaffAttendance.objects.all().delete()
        
        response = self.client.get(reverse('staff:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Should handle empty data gracefully
        context = response.context
        self.assertEqual(context['total_staff'], 0)
        self.assertEqual(context['task_stats']['total_tasks'], 0)
