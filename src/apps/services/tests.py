"""
Comprehensive test suite for the Database of PPAs functionality.
Testing unit, integration, and API functionality.
"""

from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from django.test.utils import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from decimal import Decimal
import json
import tempfile
from datetime import date, timedelta, datetime
from unittest.mock import patch, Mock

from .models import (
    MinistryProgram, 
    MinistryProgramHistory, 
    ServiceProgram, 
    ServiceApplication, 
    ServiceDisbursement
)
from .forms import MinistryProgramInlineForm, MinistryProgramForm
from .audit import MinistryProgramAuditService

User = get_user_model()


class MinistryProgramModelTests(TestCase):
    """Unit tests for MinistryProgram model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        self.ministry_program_data = {
            'title': 'Test Program',
            'ministry': 'mssd',
            'ppa_type': 'program',
            'description': 'Test program description',
            'objectives': 'Test objectives',
            'expected_outcomes': 'Test outcomes',
            'key_performance_indicators': 'Test KPIs',
            'target_beneficiaries': 'Test beneficiaries',
            'geographic_coverage': 'BARMM Region',
            'implementation_strategy': 'Test strategy',
            'implementing_units': 'Test units',
            'total_budget': Decimal('1000000.00'),
            'allocated_budget': Decimal('800000.00'),
            'utilized_budget': Decimal('200000.00'),
            'funding_source': 'national',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'duration_months': 12,
            'status': 'active',
            'priority_level': 'high',
            'created_by': self.user,
            'estimated_beneficiaries': 500
        }
    
    def test_ministry_program_creation(self):
        """Test creating a ministry program with valid data."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        
        self.assertEqual(program.title, 'Test Program')
        self.assertEqual(program.ministry, 'mssd')
        self.assertEqual(program.status, 'active')
        self.assertEqual(program.created_by, self.user)
        self.assertIsNotNone(program.slug)
        self.assertIsNotNone(program.code)
        self.assertTrue(program.is_public)
        self.assertFalse(program.is_deleted)
    
    def test_auto_generate_slug(self):
        """Test automatic slug generation."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        expected_slug = 'mssd-test-program'
        self.assertEqual(program.slug, expected_slug)
    
    def test_auto_generate_code(self):
        """Test automatic code generation."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        year = program.start_date.year
        expected_code = f"MSSD-{year}-001"
        self.assertEqual(program.code, expected_code)
    
    def test_code_uniqueness(self):
        """Test that program codes are unique."""
        program1 = MinistryProgram.objects.create(**self.ministry_program_data)
        
        # Create second program - should get different code
        data2 = self.ministry_program_data.copy()
        data2['title'] = 'Test Program 2'
        program2 = MinistryProgram.objects.create(**data2)
        
        self.assertNotEqual(program1.code, program2.code)
        self.assertEqual(program2.code, f"MSSD-{program2.start_date.year}-002")
    
    def test_slug_uniqueness(self):
        """Test that program slugs are unique."""
        program1 = MinistryProgram.objects.create(**self.ministry_program_data)
        
        # Try to create another program with same title and ministry
        with self.assertRaises(IntegrityError):
            MinistryProgram.objects.create(**self.ministry_program_data)
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        reason = "Test deletion"
        
        program.soft_delete(self.user, reason)
        
        self.assertTrue(program.is_deleted)
        self.assertIsNotNone(program.deleted_at)
        self.assertEqual(program.deleted_by, self.user)
        self.assertEqual(program.deletion_reason, reason)
    
    def test_restore_program(self):
        """Test program restoration after soft delete."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        program.soft_delete(self.user, "Test deletion")
        
        program.restore(self.user)
        
        self.assertFalse(program.is_deleted)
        self.assertIsNone(program.deleted_at)
        self.assertIsNone(program.deleted_by)
        self.assertEqual(program.deletion_reason, '')
        self.assertEqual(program.last_modified_by, self.user)
    
    def test_approve_program(self):
        """Test program approval functionality."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        program.status = 'pending_approval'
        program.save()
        
        program.approve(self.user)
        
        self.assertEqual(program.status, 'active')
        self.assertIsNotNone(program.approved_at)
        self.assertEqual(program.approved_by, self.user)
        self.assertEqual(program.last_modified_by, self.user)
    
    def test_budget_utilization_percentage(self):
        """Test budget utilization calculation."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        
        # With allocated budget of 800,000 and utilized of 200,000
        utilization = program.get_budget_utilization_percentage()
        expected = (200000 / 800000) * 100  # 25%
        self.assertEqual(utilization, expected)
        
        # Test with zero allocated budget
        program.allocated_budget = 0
        utilization = program.get_budget_utilization_percentage()
        self.assertEqual(utilization, 0)
    
    def test_is_active(self):
        """Test is_active property."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        self.assertTrue(program.is_active())
        
        # Test inactive status
        program.status = 'completed'
        self.assertFalse(program.is_active())
        
        # Test deleted program
        program.status = 'active'
        program.is_deleted = True
        self.assertFalse(program.is_active())
    
    def test_permission_methods(self):
        """Test permission checking methods."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        
        # Test superuser permissions
        superuser = User.objects.create_superuser(
            username='super', email='super@test.com', password='pass'
        )
        self.assertTrue(program.can_edit(superuser))
        self.assertTrue(program.can_delete(superuser))
        
        # Test creator permissions
        self.assertTrue(program.can_edit(self.user))
        
        # Test draft deletion
        program.status = 'draft'
        self.assertTrue(program.can_delete(self.user))
        
        # Test MP permissions
        mp_user = User.objects.create_user(
            username='mp', email='mp@test.com', password='pass', user_type='mp'
        )
        self.assertTrue(program.can_delete(mp_user))
        
        # Test regular user (should be False)
        regular_user = User.objects.create_user(
            username='regular', email='regular@test.com', password='pass'
        )
        self.assertFalse(program.can_edit(regular_user))
        self.assertFalse(program.can_delete(regular_user))
    
    def test_string_representation(self):
        """Test the __str__ method."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        expected = f"[{program.get_ministry_display()}] {program.title}"
        self.assertEqual(str(program), expected)
    
    def test_absolute_url(self):
        """Test get_absolute_url method."""
        program = MinistryProgram.objects.create(**self.ministry_program_data)
        expected_url = reverse('ministry_program_detail', args=[program.slug])
        self.assertEqual(program.get_absolute_url(), expected_url)


class MinistryProgramFormTests(TestCase):
    """Unit tests for MinistryProgram forms."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        self.valid_form_data = {
            'title': 'Test Program Form',
            'ministry': 'mssd',
            'program_source': 'ministry',
            'ppa_type': 'program',
            'status': 'active',
            'priority_level': 'medium',
            'total_budget': '1000000.00',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'geographic_coverage': 'BARMM Region',
            'target_beneficiaries': 'All citizens',
            'description': 'Test description',
            'objectives': 'Test objectives',
            'expected_outcomes': 'Test outcomes'
        }
    
    def test_ministry_program_inline_form_valid(self):
        """Test MinistryProgramInlineForm with valid data."""
        form = MinistryProgramInlineForm(data=self.valid_form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Test saving
        program = form.save(commit=False)
        program.created_by = self.user
        program.save()
        
        self.assertEqual(program.title, 'Test Program Form')
        self.assertEqual(program.ministry, 'mssd')
        self.assertGreater(program.duration_months, 0)
    
    def test_form_auto_calculate_duration(self):
        """Test automatic duration calculation."""
        form = MinistryProgramInlineForm(data=self.valid_form_data, user=self.user)
        self.assertTrue(form.is_valid())
        
        program = form.save(commit=False)
        program.created_by = self.user
        program.save()
        
        # Should calculate approximately 12 months
        self.assertEqual(program.duration_months, 11)  # Jan 1 to Dec 31 is 11 months
    
    def test_form_required_fields(self):
        """Test form validation with missing required fields."""
        incomplete_data = self.valid_form_data.copy()
        del incomplete_data['title']
        
        form = MinistryProgramInlineForm(data=incomplete_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_date_validation(self):
        """Test form validation for date fields."""
        invalid_data = self.valid_form_data.copy()
        invalid_data['start_date'] = '2024-12-31'
        invalid_data['end_date'] = '2024-01-01'  # End before start
        
        form = MinistryProgramInlineForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
    
    def test_form_default_values(self):
        """Test form sets appropriate default values."""
        form = MinistryProgramInlineForm(user=self.user)
        
        self.assertEqual(form.fields['status'].initial, 'active')
        self.assertEqual(form.fields['priority_level'].initial, 'medium')
    
    def test_comprehensive_form_validation(self):
        """Test MinistryProgramForm comprehensive validation."""
        form_data = {
            'code': 'TEST-2024-001',
            'title': 'Comprehensive Test Program',
            'description': 'Detailed description',
            'ministry': 'mssd',
            'ppa_type': 'program',
            'status': 'active',
            'total_budget': '50000000.00',  # ₱50M - within MSSD limit
            'allocated_budget': '40000000.00',
            'estimated_beneficiaries': 1000,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'duration_months': 12,
            'geographic_coverage': 'BARMM Region',
            'implementing_units': 'MSSD Main Office',
            'expected_outcomes': 'Improved welfare',
            'priority_level': 'high',
            'implementation_strategy': 'Phased approach',
            'key_performance_indicators': 'Beneficiary satisfaction',
            'objectives': 'Provide social services',
            'partner_agencies': 'LGUs',
            'funding_source': 'national',
            'is_featured': False,
            'is_public': True
        }
        
        form = MinistryProgramForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_budget_limit_validation(self):
        """Test budget limit validation for different ministries."""
        # Test MSSD with budget over limit
        over_limit_data = self.valid_form_data.copy()
        over_limit_data['total_budget'] = '20000000000.00'  # ₱20B - over MSSD limit
        
        form = MinistryProgramInlineForm(data=over_limit_data, user=self.user)
        # Note: The inline form doesn't have budget validation, but full form does
        
        # Test with comprehensive form
        comprehensive_data = {
            'title': 'Test',
            'ministry': 'mssd',
            'total_budget': '20000000000.00',  # Over limit
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        
        form = MinistryProgramForm(data=comprehensive_data)
        self.assertFalse(form.is_valid())
        self.assertIn('total_budget', form.errors)


class DatabasePPAsViewTests(TestCase):
    """Integration tests for DatabasePPAsView."""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@test.com',
            password='testpass123'
        )
        
        self.mp_user = User.objects.create_user(
            username='mp_user',
            email='mp@test.com',
            password='testpass123',
            user_type='mp'
        )
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='testpass123',
            user_type='coordinator'
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@test.com',
            password='testpass123'
        )
        
        # Create test programs
        self.program1 = MinistryProgram.objects.create(
            title='Test Program 1',
            ministry='mssd',
            ppa_type='program',
            description='Test description 1',
            objectives='Test objectives 1',
            expected_outcomes='Test outcomes 1',
            key_performance_indicators='Test KPIs 1',
            target_beneficiaries='Citizens',
            geographic_coverage='Maguindanao',
            implementation_strategy='Direct implementation',
            implementing_units='MSSD Main',
            total_budget=Decimal('1000000.00'),
            funding_source='national',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            duration_months=12,
            status='active',
            created_by=self.superuser
        )
        
        self.program2 = MinistryProgram.objects.create(
            title='Test Program 2',
            ministry='mafar',
            ppa_type='project',
            description='Test description 2',
            objectives='Test objectives 2',
            expected_outcomes='Test outcomes 2',
            key_performance_indicators='Test KPIs 2',
            target_beneficiaries='Farmers',
            geographic_coverage='Lanao del Sur',
            implementation_strategy='Partnership approach',
            implementing_units='MAFAR Regional',
            total_budget=Decimal('2000000.00'),
            funding_source='international',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=730),
            duration_months=24,
            status='planning',
            created_by=self.mp_user,
            priority_level='high'
        )
    
    def test_database_ppas_access_control(self):
        """Test access control for database PPAs page."""
        url = reverse('database_ppas')
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test unauthorized user
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to home
        
        # Test authorized users
        authorized_users = [self.superuser, self.mp_user, self.coordinator]
        for user in authorized_users:
            self.client.login(username=user.username, password='testpass123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()
    
    def test_database_ppas_get_context(self):
        """Test GET request context data."""
        self.client.login(username='superuser', password='testpass123')
        url = reverse('database_ppas')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Database of PPAs')
        
        # Check context variables
        context = response.context
        self.assertIn('total_ppas', context)
        self.assertIn('active_count', context)
        self.assertIn('ppas', context)
        self.assertIn('ministry_stats', context)
        self.assertIn('current_filters', context)
        
        # Check statistics
        self.assertEqual(context['total_ppas'], 2)
        self.assertEqual(context['active_count'], 1)
        self.assertEqual(context['planning_count'], 1)
    
    def test_database_ppas_filtering(self):
        """Test filtering functionality."""
        self.client.login(username='superuser', password='testpass123')
        url = reverse('database_ppas')
        
        # Test ministry filter
        response = self.client.get(url, {'ministry': 'mssd'})
        self.assertEqual(response.status_code, 200)
        ppas = response.context['ppas']
        self.assertEqual(len(ppas), 1)
        self.assertEqual(ppas[0]['ministry_code'], 'mssd')
        
        # Test status filter
        response = self.client.get(url, {'status': 'active'})
        ppas = response.context['ppas']
        self.assertEqual(len(ppas), 1)
        self.assertEqual(ppas[0]['status'], 'Active')
        
        # Test search filter
        response = self.client.get(url, {'search': 'Farmers'})
        ppas = response.context['ppas']
        self.assertEqual(len(ppas), 1)
        self.assertIn('Farmers', ppas[0]['beneficiaries'])
        
        # Test budget range filter
        response = self.client.get(url, {'budget_range': '1m_10m'})
        ppas = response.context['ppas']
        # Both programs should be in 1M-10M range
        self.assertEqual(len(ppas), 2)
    
    def test_database_ppas_sorting(self):
        """Test sorting functionality."""
        self.client.login(username='superuser', password='testpass123')
        url = reverse('database_ppas')
        
        # Test sort by title A-Z
        response = self.client.get(url, {'sort_by': 'title'})
        ppas = response.context['ppas']
        self.assertEqual(ppas[0]['title'], 'Test Program 1')
        self.assertEqual(ppas[1]['title'], 'Test Program 2')
        
        # Test sort by budget high to low
        response = self.client.get(url, {'sort_by': '-total_budget'})
        ppas = response.context['ppas']
        self.assertEqual(ppas[0]['budget'], 2000000.00)
        self.assertEqual(ppas[1]['budget'], 1000000.00)
    
    def test_create_ppa_post(self):
        """Test creating a new PPA via POST."""
        self.client.login(username='superuser', password='testpass123')
        url = reverse('database_ppas')
        
        post_data = {
            'action': 'create',
            'title': 'New Test Program',
            'ministry': 'moh',
            'program_source': 'ministry',
            'ppa_type': 'activity',
            'status': 'active',
            'priority_level': 'medium',
            'total_budget': '500000.00',
            'start_date': '2024-06-01',
            'end_date': '2024-12-31',
            'geographic_coverage': 'BARMM Region',
            'target_beneficiaries': 'Patients',
            'description': 'Health program description',
            'objectives': 'Improve health outcomes',
            'expected_outcomes': 'Better health metrics'
        }
        
        # Test AJAX request
        response = self.client.post(
            url, 
            post_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify program was created
        new_program = MinistryProgram.objects.filter(title='New Test Program').first()
        self.assertIsNotNone(new_program)
        self.assertEqual(new_program.ministry, 'moh')
        self.assertEqual(new_program.created_by, self.superuser)
    
    def test_create_ppa_validation_errors(self):
        """Test PPA creation with validation errors."""
        self.client.login(username='superuser', password='testpass123')
        url = reverse('database_ppas')
        
        # Missing required fields
        post_data = {
            'action': 'create',
            'title': '',  # Required field missing
            'ministry': 'moh'
        }
        
        response = self.client.post(
            url, 
            post_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
        self.assertIn('title', response_data['errors'])
    
    def test_update_ppa_post(self):
        """Test updating an existing PPA via POST."""
        self.client.login(username='superuser', password='testpass123')
        url = reverse('database_ppas')
        
        post_data = {
            'action': 'update',
            'ppa_id': str(self.program1.id),
            'title': 'Updated Program Title',
            'ministry': self.program1.ministry,
            'program_source': self.program1.program_source,
            'ppa_type': self.program1.ppa_type,
            'status': 'completed',
            'priority_level': 'high',
            'total_budget': '1500000.00',
            'start_date': self.program1.start_date.strftime('%Y-%m-%d'),
            'end_date': self.program1.end_date.strftime('%Y-%m-%d'),
            'geographic_coverage': self.program1.geographic_coverage,
            'target_beneficiaries': self.program1.target_beneficiaries,
            'description': 'Updated description',
            'objectives': 'Updated objectives',
            'expected_outcomes': 'Updated outcomes'
        }
        
        response = self.client.post(
            url, 
            post_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify program was updated
        updated_program = MinistryProgram.objects.get(id=self.program1.id)
        self.assertEqual(updated_program.title, 'Updated Program Title')
        self.assertEqual(updated_program.status, 'completed')
        self.assertEqual(updated_program.total_budget, Decimal('1500000.00'))
    
    def test_delete_ppa_post(self):
        """Test deleting a PPA via POST."""
        self.client.login(username='superuser', password='testpass123')
        url = reverse('database_ppas')
        
        post_data = {
            'action': 'delete',
            'ppa_id': str(self.program1.id),
            'reason': 'Test deletion'
        }
        
        response = self.client.post(
            url, 
            post_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify program was soft deleted
        deleted_program = MinistryProgram.objects.get(id=self.program1.id)
        self.assertTrue(deleted_program.is_deleted)
        self.assertEqual(deleted_program.deleted_by, self.superuser)
        self.assertEqual(deleted_program.deletion_reason, 'Test deletion')
    
    def test_permission_denied_operations(self):
        """Test permission denied for unauthorized operations."""
        # Test with regular user (unauthorized)
        self.client.login(username='regular_user', password='testpass123')
        url = reverse('database_ppas')
        
        # Should be redirected before reaching POST
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # Test with coordinator (can edit but not delete)
        self.client.login(username='coordinator', password='testpass123')
        
        # Should be able to create
        post_data = {
            'action': 'create',
            'title': 'Coordinator Program',
            'ministry': 'mssd',
            'program_source': 'ministry',
            'ppa_type': 'program',
            'status': 'active',
            'priority_level': 'medium',
            'total_budget': '100000.00',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'geographic_coverage': 'Test',
            'target_beneficiaries': 'Test',
            'description': 'Test',
            'objectives': 'Test',
            'expected_outcomes': 'Test'
        }
        
        response = self.client.post(
            url, 
            post_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # But should not be able to delete (only superuser, mp, chief_of_staff, admin)
        delete_data = {
            'action': 'delete',
            'ppa_id': str(self.program1.id)
        }
        
        response = self.client.post(
            url, 
            delete_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 403)


class MinistryProgramAuditTests(TestCase):
    """Tests for audit trail functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        self.program = MinistryProgram.objects.create(
            title='Audit Test Program',
            ministry='mssd',
            ppa_type='program',
            description='Test description',
            objectives='Test objectives',
            expected_outcomes='Test outcomes',
            key_performance_indicators='Test KPIs',
            target_beneficiaries='Citizens',
            geographic_coverage='Test Area',
            implementation_strategy='Test strategy',
            implementing_units='Test units',
            total_budget=Decimal('1000000.00'),
            funding_source='national',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            duration_months=12,
            status='active',
            created_by=self.user
        )
    
    def test_audit_log_creation(self):
        """Test audit log entry creation."""
        request_mock = Mock()
        request_mock.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'Test'}
        
        MinistryProgramAuditService.log_program_action(
            program=self.program,
            action_type='create',
            user=self.user,
            request=request_mock,
            reason='Test creation'
        )
        
        # Check audit entry was created
        audit_entry = MinistryProgramHistory.objects.filter(
            program=self.program,
            action_type='create'
        ).first()
        
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.changed_by, self.user)
        self.assertEqual(audit_entry.reason, 'Test creation')
        self.assertEqual(audit_entry.ip_address, '127.0.0.1')
        self.assertEqual(audit_entry.user_agent, 'Test')
    
    def test_audit_log_with_changes(self):
        """Test audit log with field changes."""
        request_mock = Mock()
        request_mock.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'Test'}
        
        old_values = {'title': 'Old Title', 'status': 'draft'}
        new_values = {'title': 'New Title', 'status': 'active'}
        changed_fields = ['title', 'status']
        
        MinistryProgramAuditService.log_program_action(
            program=self.program,
            action_type='update',
            user=self.user,
            request=request_mock,
            reason='Test update',
            changed_fields=changed_fields,
            old_values=old_values,
            new_values=new_values
        )
        
        audit_entry = MinistryProgramHistory.objects.filter(
            program=self.program,
            action_type='update'
        ).first()
        
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.changed_fields, changed_fields)
        self.assertEqual(audit_entry.old_values, old_values)
        self.assertEqual(audit_entry.new_values, new_values)


class PpaDatabaseIntegrationTests(TransactionTestCase):
    """Integration tests simulating real user workflows."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            user_type='admin'
        )
    
    def test_complete_ppa_lifecycle(self):
        """Test complete PPA lifecycle: create, update, delete."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('database_ppas')
        
        # Step 1: Create PPA
        create_data = {
            'action': 'create',
            'title': 'Lifecycle Test Program',
            'ministry': 'mssd',
            'program_source': 'ministry',
            'ppa_type': 'program',
            'status': 'draft',
            'priority_level': 'medium',
            'total_budget': '1000000.00',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'geographic_coverage': 'BARMM Region',
            'target_beneficiaries': 'All citizens',
            'description': 'Test program for lifecycle',
            'objectives': 'Test objectives',
            'expected_outcomes': 'Test outcomes'
        }
        
        response = self.client.post(
            url, 
            create_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Get created program
        program = MinistryProgram.objects.filter(title='Lifecycle Test Program').first()
        self.assertIsNotNone(program)
        self.assertEqual(program.status, 'draft')
        
        # Step 2: Update PPA to active
        update_data = create_data.copy()
        update_data.update({
            'action': 'update',
            'ppa_id': str(program.id),
            'status': 'active',
            'priority_level': 'high',
            'total_budget': '1500000.00'
        })
        
        response = self.client.post(
            url, 
            update_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        program.refresh_from_db()
        self.assertEqual(program.status, 'active')
        self.assertEqual(program.priority_level, 'high')
        self.assertEqual(program.total_budget, Decimal('1500000.00'))
        
        # Step 3: Delete PPA
        delete_data = {
            'action': 'delete',
            'ppa_id': str(program.id),
            'reason': 'Lifecycle test completion'
        }
        
        response = self.client.post(
            url, 
            delete_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify soft delete
        program.refresh_from_db()
        self.assertTrue(program.is_deleted)
        self.assertEqual(program.deletion_reason, 'Lifecycle test completion')
        
        # Verify audit trail
        audit_entries = MinistryProgramHistory.objects.filter(program=program)
        self.assertEqual(audit_entries.count(), 3)  # create, update, delete
        
        actions = list(audit_entries.values_list('action_type', flat=True))
        self.assertIn('create', actions)
        self.assertIn('update', actions)
        self.assertIn('delete', actions)
    
    def test_bulk_operations_workflow(self):
        """Test workflow with multiple programs and filtering."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('database_ppas')
        
        # Create multiple programs
        programs_data = [
            {
                'title': f'Bulk Test Program {i}',
                'ministry': 'mssd' if i % 2 == 0 else 'mafar',
                'status': 'active' if i % 3 == 0 else 'planning',
                'total_budget': str(1000000 * (i + 1))
            }
            for i in range(5)
        ]
        
        created_programs = []
        for data in programs_data:
            create_data = {
                'action': 'create',
                'program_source': 'ministry',
                'ppa_type': 'program',
                'priority_level': 'medium',
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'geographic_coverage': 'Test Area',
                'target_beneficiaries': 'Test beneficiaries',
                'description': 'Test description',
                'objectives': 'Test objectives',
                'expected_outcomes': 'Test outcomes',
                **data
            }
            
            response = self.client.post(
                url, 
                create_data, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(response.status_code, 200)
            
            program = MinistryProgram.objects.filter(title=data['title']).first()
            created_programs.append(program)
        
        # Test filtering by ministry
        response = self.client.get(url, {'ministry': 'mssd'})
        self.assertEqual(response.status_code, 200)
        ppas = response.context['ppas']
        mssd_count = len([p for p in created_programs if p.ministry == 'mssd'])
        self.assertEqual(len(ppas), mssd_count)
        
        # Test filtering by status
        response = self.client.get(url, {'status': 'active'})
        ppas = response.context['ppas']
        active_count = len([p for p in created_programs if p.status == 'active'])
        self.assertEqual(len(ppas), active_count)
        
        # Test search functionality
        response = self.client.get(url, {'search': 'Bulk Test Program 2'})
        ppas = response.context['ppas']
        self.assertEqual(len(ppas), 1)
        self.assertEqual(ppas[0]['title'], 'Bulk Test Program 2')
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery scenarios."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('database_ppas')
        
        # Test invalid action
        response = self.client.post(
            url, 
            {'action': 'invalid_action'}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test update non-existent program
        response = self.client.post(
            url, 
            {'action': 'update', 'ppa_id': '99999'}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)
        
        # Test delete non-existent program
        response = self.client.post(
            url, 
            {'action': 'delete', 'ppa_id': '99999'}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_concurrent_access_handling(self):
        """Test handling of concurrent access scenarios."""
        # Create a program
        program = MinistryProgram.objects.create(
            title='Concurrent Test Program',
            ministry='mssd',
            ppa_type='program',
            description='Test description',
            objectives='Test objectives',
            expected_outcomes='Test outcomes',
            key_performance_indicators='Test KPIs',
            target_beneficiaries='Citizens',
            geographic_coverage='Test Area',
            implementation_strategy='Test strategy',
            implementing_units='Test units',
            total_budget=Decimal('1000000.00'),
            funding_source='national',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            duration_months=12,
            status='active',
            created_by=self.admin_user
        )
        
        # Simulate concurrent updates
        self.client.login(username='admin', password='testpass123')
        url = reverse('database_ppas')
        
        update_data = {
            'action': 'update',
            'ppa_id': str(program.id),
            'title': 'Updated Concurrent Program',
            'ministry': program.ministry,
            'program_source': program.program_source,
            'ppa_type': program.ppa_type,
            'status': 'completed',
            'priority_level': 'high',
            'total_budget': '2000000.00',
            'start_date': program.start_date.strftime('%Y-%m-%d'),
            'end_date': program.end_date.strftime('%Y-%m-%d'),
            'geographic_coverage': program.geographic_coverage,
            'target_beneficiaries': program.target_beneficiaries,
            'description': 'Updated description',
            'objectives': 'Updated objectives',
            'expected_outcomes': 'Updated outcomes'
        }
        
        # First update should succeed
        response = self.client.post(
            url, 
            update_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify the update was applied
        program.refresh_from_db()
        self.assertEqual(program.title, 'Updated Concurrent Program')
        self.assertEqual(program.status, 'completed')


class PpaApiResponseTests(TestCase):
    """Tests for API response formats and data integrity."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='apiuser',
            email='api@test.com',
            password='testpass123'
        )
        
        self.program = MinistryProgram.objects.create(
            title='API Test Program',
            ministry='mssd',
            ppa_type='program',
            description='API test description',
            objectives='API test objectives',
            expected_outcomes='API test outcomes',
            key_performance_indicators='API test KPIs',
            target_beneficiaries='Citizens',
            geographic_coverage='Test Area',
            implementation_strategy='Test strategy',
            implementing_units='Test units',
            total_budget=Decimal('1000000.00'),
            funding_source='national',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            duration_months=12,
            status='active',
            created_by=self.user
        )
    
    def test_ajax_response_format(self):
        """Test AJAX response format and structure."""
        self.client.login(username='apiuser', password='testpass123')
        url = reverse('database_ppas')
        
        # Test successful creation response
        create_data = {
            'action': 'create',
            'title': 'API Response Test',
            'ministry': 'moh',
            'program_source': 'ministry',
            'ppa_type': 'program',
            'status': 'active',
            'priority_level': 'medium',
            'total_budget': '500000.00',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'geographic_coverage': 'Test',
            'target_beneficiaries': 'Test',
            'description': 'Test',
            'objectives': 'Test',
            'expected_outcomes': 'Test'
        }
        
        response = self.client.post(
            url, 
            create_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertTrue(data['success'])
    
    def test_error_response_format(self):
        """Test error response format and structure."""
        self.client.login(username='apiuser', password='testpass123')
        url = reverse('database_ppas')
        
        # Test validation error response
        invalid_data = {
            'action': 'create',
            'title': '',  # Required field missing
            'ministry': 'moh'
        }
        
        response = self.client.post(
            url, 
            invalid_data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        
        self.assertIn('success', data)
        self.assertIn('errors', data)
        self.assertIn('message', data)
        self.assertFalse(data['success'])
        self.assertIn('title', data['errors'])
    
    def test_data_serialization(self):
        """Test proper data serialization in responses."""
        self.client.login(username='apiuser', password='testpass123')
        url = reverse('database_ppas')
        
        # Test GET response data structure
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that context data is properly structured
        ppas = response.context['ppas']
        self.assertIsInstance(ppas, list)
        
        if ppas:
            ppa = ppas[0]
            required_fields = [
                'id', 'title', 'ministry', 'ministry_code', 'ppa_type',
                'status', 'priority', 'budget', 'budget_display',
                'start_date', 'end_date', 'location', 'beneficiaries'
            ]
            
            for field in required_fields:
                self.assertIn(field, ppa)
        
        # Test statistics data
        stats_fields = [
            'total_ppas', 'active_count', 'planning_count', 
            'this_year_count', 'total_budget_display'
        ]
        
        for field in stats_fields:
            self.assertIn(field, response.context)