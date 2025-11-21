"""
Comprehensive unit tests for the Referrals app.
Tests models, forms, views, and business logic including reference number generation,
status tracking, and document management.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from PIL import Image
import io

from .models import (
    Agency, ServiceCategory, Service, Referral, 
    ReferralUpdate, ReferralDocument
)

User = get_user_model()


class AgencyModelTest(TestCase):
    """Test cases for Agency model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='staff'
        )
        
        self.agency = Agency.objects.create(
            name='Department of Health',
            abbreviation='DOH',
            ministry='Health Ministry',
            description='Government health agency',
            contact_person='Dr. Health Officer',
            contact_email='contact@doh.gov.ph',
            contact_phone='+63123456789',
            address='123 Health Street, Manila',
            website='https://doh.gov.ph',
            contact_info='Additional contact details',
            created_by=self.user
        )
    
    def test_agency_creation(self):
        """Test agency model creation."""
        self.assertEqual(self.agency.name, 'Department of Health')
        self.assertEqual(self.agency.abbreviation, 'DOH')
        self.assertEqual(self.agency.ministry, 'Health Ministry')
        self.assertEqual(self.agency.contact_person, 'Dr. Health Officer')
        self.assertTrue(self.agency.is_active)
        self.assertFalse(self.agency.is_deleted)
        self.assertEqual(self.agency.created_by, self.user)
    
    def test_agency_str_method_with_abbreviation(self):
        """Test string representation with abbreviation."""
        expected_str = "DOH - Department of Health"
        self.assertEqual(str(self.agency), expected_str)
    
    def test_agency_str_method_without_abbreviation(self):
        """Test string representation without abbreviation."""
        agency_no_abbrev = Agency.objects.create(
            name='Full Agency Name',
            created_by=self.user
        )
        self.assertEqual(str(agency_no_abbrev), 'Full Agency Name')
    
    def test_agency_soft_deletion(self):
        """Test soft deletion functionality."""
        self.agency.is_deleted = True
        self.agency.deleted_at = timezone.now()
        self.agency.deleted_by = self.user
        self.agency.save()
        
        self.agency.refresh_from_db()
        self.assertTrue(self.agency.is_deleted)
        self.assertIsNotNone(self.agency.deleted_at)
        self.assertEqual(self.agency.deleted_by, self.user)
    
    def test_agency_ordering(self):
        """Test that agencies are ordered by name."""
        agency_z = Agency.objects.create(
            name='Zebra Agency',
            created_by=self.user
        )
        agency_a = Agency.objects.create(
            name='Alpha Agency',
            created_by=self.user
        )
        
        agencies = list(Agency.objects.all())
        self.assertEqual(agencies[0], agency_a)
        self.assertEqual(agencies[1], self.agency)  # Department of Health
        self.assertEqual(agencies[2], agency_z)


class ServiceCategoryModelTest(TestCase):
    """Test cases for ServiceCategory model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.parent_category = ServiceCategory.objects.create(
            name='Healthcare',
            description='All healthcare related services',
            icon='fas fa-heartbeat',
            order=1,
            created_by=self.user
        )
        
        self.sub_category = ServiceCategory.objects.create(
            name='Emergency Care',
            description='Emergency medical services',
            icon='fas fa-ambulance',
            parent=self.parent_category,
            order=1,
            created_by=self.user
        )
    
    def test_category_creation(self):
        """Test category model creation."""
        self.assertEqual(self.parent_category.name, 'Healthcare')
        self.assertEqual(self.parent_category.icon, 'fas fa-heartbeat')
        self.assertEqual(self.parent_category.order, 1)
        self.assertTrue(self.parent_category.is_active)
        self.assertIsNone(self.parent_category.parent)
    
    def test_subcategory_relationship(self):
        """Test parent-child category relationship."""
        self.assertEqual(self.sub_category.parent, self.parent_category)
        self.assertIn(self.sub_category, self.parent_category.subcategories.all())
    
    def test_category_slug_generation(self):
        """Test automatic slug generation."""
        self.assertEqual(self.parent_category.slug, 'healthcare')
        self.assertEqual(self.sub_category.slug, 'emergency-care')
    
    def test_category_str_method(self):
        """Test string representation."""
        self.assertEqual(str(self.parent_category), 'Healthcare')
        self.assertEqual(str(self.sub_category), 'Emergency Care')
    
    def test_category_ordering(self):
        """Test category ordering by order field then name."""
        category_high_order = ServiceCategory.objects.create(
            name='High Priority',
            order=0,
            created_by=self.user
        )
        category_same_order = ServiceCategory.objects.create(
            name='Another Healthcare',
            order=1,
            created_by=self.user
        )
        
        categories = list(ServiceCategory.objects.all())
        self.assertEqual(categories[0], category_high_order)  # order=0
        # order=1 should be sorted by name: Another Healthcare, Healthcare
        self.assertEqual(categories[1], category_same_order)
        self.assertEqual(categories[2], self.parent_category)


class ServiceModelTest(TestCase):
    """Test cases for Service model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.agency = Agency.objects.create(
            name='Department of Health',
            created_by=self.user
        )
        
        self.category = ServiceCategory.objects.create(
            name='Healthcare',
            created_by=self.user
        )
        
        self.service = Service.objects.create(
            name='Free Medical Checkup',
            description='Comprehensive medical examination at no cost',
            category=self.category,
            agency=self.agency,
            eligibility_criteria='Age 60+ or low income',
            required_documents=['ID', 'Proof of income'],
            application_process='Visit nearest health center',
            processing_time='1-2 weeks',
            fees='Free',
            contact_info='Call 123-456-7890',
            website_link='https://doh.gov.ph/checkup',
            form_link='https://forms.doh.gov.ph/checkup',
            is_featured=True,
            created_by=self.user
        )
    
    def test_service_creation(self):
        """Test service model creation."""
        self.assertEqual(self.service.name, 'Free Medical Checkup')
        self.assertEqual(self.service.category, self.category)
        self.assertEqual(self.service.agency, self.agency)
        self.assertEqual(self.service.processing_time, '1-2 weeks')
        self.assertTrue(self.service.is_active)
        self.assertTrue(self.service.is_featured)
        self.assertEqual(self.service.required_documents, ['ID', 'Proof of income'])
    
    def test_service_slug_generation(self):
        """Test automatic slug generation."""
        self.assertEqual(self.service.slug, 'free-medical-checkup')
    
    def test_service_str_method(self):
        """Test string representation."""
        self.assertEqual(str(self.service), 'Free Medical Checkup')
    
    def test_service_get_absolute_url(self):
        """Test get_absolute_url method."""
        expected_url = reverse('service_detail', args=[self.service.slug])
        self.assertEqual(self.service.get_absolute_url(), expected_url)
    
    def test_service_ordering(self):
        """Test service ordering by name."""
        service_z = Service.objects.create(
            name='Zebra Service',
            description='Test service',
            category=self.category,
            agency=self.agency,
            created_by=self.user
        )
        service_a = Service.objects.create(
            name='Alpha Service',
            description='Test service',
            category=self.category,
            agency=self.agency,
            created_by=self.user
        )
        
        services = list(Service.objects.all())
        self.assertEqual(services[0], service_a)
        self.assertEqual(services[1], self.service)  # Free Medical Checkup
        self.assertEqual(services[2], service_z)


class ReferralModelTest(TestCase):
    """Test cases for Referral model."""
    
    def setUp(self):
        """Set up test data."""
        self.constituent_user = User.objects.create_user(
            username='constituent',
            email='constituent@example.com',
            password='testpass123',
            user_type='member'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            user_type='staff'
        )
        
        self.agency = Agency.objects.create(
            name='Test Agency',
            created_by=self.staff_user
        )
        
        self.category = ServiceCategory.objects.create(
            name='Test Category',
            created_by=self.staff_user
        )
        
        self.service = Service.objects.create(
            name='Test Service',
            description='Test service description',
            category=self.category,
            agency=self.agency,
            created_by=self.staff_user
        )
        
        self.referral = Referral.objects.create(
            constituent=self.constituent_user,
            service=self.service,
            description='Need assistance with medical expenses',
            priority='high',
            assigned_to=self.staff_user,
            created_by=self.staff_user
        )
    
    def test_referral_creation(self):
        """Test referral model creation."""
        self.assertEqual(self.referral.constituent, self.constituent_user)
        self.assertEqual(self.referral.service, self.service)
        self.assertEqual(self.referral.priority, 'high')
        self.assertEqual(self.referral.status, 'draft')  # default
        self.assertEqual(self.referral.assigned_to, self.staff_user)
        self.assertIsNotNone(self.referral.reference_number)
    
    def test_reference_number_generation(self):
        """Test automatic reference number generation."""
        # Reference number should follow format REF-YYYYMMDD-NNNN
        import re
        pattern = r'^REF-\d{8}-\d{4}$'
        self.assertRegex(self.referral.reference_number, pattern)
        
        # Create another referral same day - should have incremented number
        referral2 = Referral.objects.create(
            constituent=self.constituent_user,
            service=self.service,
            description='Another referral',
            created_by=self.staff_user
        )
        
        # Both should have same date prefix but different sequence
        ref1_parts = self.referral.reference_number.split('-')
        ref2_parts = referral2.reference_number.split('-')
        self.assertEqual(ref1_parts[1], ref2_parts[1])  # Same date
        self.assertNotEqual(ref1_parts[2], ref2_parts[2])  # Different sequence
    
    def test_referral_str_method(self):
        """Test string representation."""
        expected_str = f"Referral {self.referral.reference_number} - {self.constituent_user.get_full_name()}"
        self.assertEqual(str(self.referral), expected_str)
    
    def test_status_change_timestamps(self):
        """Test automatic timestamp updates on status changes."""
        # Test submitted status
        self.referral.status = 'submitted'
        self.referral.save()
        self.referral.refresh_from_db()
        self.assertIsNotNone(self.referral.submitted_at)
        
        # Test referred status
        self.referral.status = 'referred'
        self.referral.save()
        self.referral.refresh_from_db()
        self.assertIsNotNone(self.referral.referred_at)
        
        # Test completed status
        self.referral.status = 'completed'
        self.referral.save()
        self.referral.refresh_from_db()
        self.assertIsNotNone(self.referral.completed_at)
    
    def test_referral_ordering(self):
        """Test referral ordering by created_at descending."""
        # Create older referral
        older_referral = Referral.objects.create(
            constituent=self.constituent_user,
            service=self.service,
            description='Older referral',
            created_by=self.staff_user
        )
        
        # Manually set older created_at
        older_time = timezone.now() - timedelta(days=1)
        Referral.objects.filter(pk=older_referral.pk).update(created_at=older_time)
        
        referrals = list(Referral.objects.all())
        self.assertEqual(referrals[0], self.referral)  # Most recent first
        self.assertEqual(referrals[1], older_referral)
    
    def test_referral_supporting_documents_json(self):
        """Test JSON field for supporting documents."""
        documents = ['id_card.pdf', 'income_certificate.pdf']
        self.referral.supporting_documents = documents
        self.referral.save()
        
        self.referral.refresh_from_db()
        self.assertEqual(self.referral.supporting_documents, documents)
    
    def test_referral_metadata_json(self):
        """Test JSON field for metadata."""
        metadata = {
            'source': 'online_form',
            'urgency_reason': 'medical_emergency',
            'family_size': 5
        }
        self.referral.metadata = metadata
        self.referral.save()
        
        self.referral.refresh_from_db()
        self.assertEqual(self.referral.metadata, metadata)


class ReferralUpdateModelTest(TestCase):
    """Test cases for ReferralUpdate model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.agency = Agency.objects.create(
            name='Test Agency',
            created_by=self.user
        )
        
        self.category = ServiceCategory.objects.create(
            name='Test Category',
            created_by=self.user
        )
        
        self.service = Service.objects.create(
            name='Test Service',
            description='Test description',
            category=self.category,
            agency=self.agency,
            created_by=self.user
        )
        
        self.referral = Referral.objects.create(
            constituent=self.user,
            service=self.service,
            description='Test referral',
            created_by=self.user
        )
        
        self.update = ReferralUpdate.objects.create(
            referral=self.referral,
            status='processing',
            notes='Application has been received and is being processed',
            update_type='status_change',
            created_by=self.user
        )
    
    def test_update_creation(self):
        """Test update model creation."""
        self.assertEqual(self.update.referral, self.referral)
        self.assertEqual(self.update.status, 'processing')
        self.assertEqual(self.update.update_type, 'status_change')
        self.assertEqual(self.update.notes, 'Application has been received and is being processed')
        self.assertEqual(self.update.created_by, self.user)
    
    def test_update_str_method(self):
        """Test string representation."""
        expected_str = f"Update for {self.referral.reference_number} - processing"
        self.assertEqual(str(self.update), expected_str)
    
    def test_update_ordering(self):
        """Test update ordering by created_at descending."""
        # Create older update
        older_update = ReferralUpdate.objects.create(
            referral=self.referral,
            status='submitted',
            notes='Initial submission',
            created_by=self.user
        )
        
        # Manually set older created_at
        older_time = timezone.now() - timedelta(hours=1)
        ReferralUpdate.objects.filter(pk=older_update.pk).update(created_at=older_time)
        
        updates = list(ReferralUpdate.objects.all())
        self.assertEqual(updates[0], self.update)  # Most recent first
        self.assertEqual(updates[1], older_update)
    
    def test_update_metadata_json(self):
        """Test JSON field for update metadata."""
        metadata = {
            'previous_status': 'submitted',
            'reason': 'document_verification_complete',
            'next_steps': ['assign_caseworker', 'schedule_interview']
        }
        self.update.metadata = metadata
        self.update.save()
        
        self.update.refresh_from_db()
        self.assertEqual(self.update.metadata, metadata)
    
    def test_update_types(self):
        """Test different update types."""
        update_types = [
            'status_change', 'comment', 'document_added', 
            'assignment', 'follow_up'
        ]
        
        for update_type in update_types:
            update = ReferralUpdate.objects.create(
                referral=self.referral,
                status='processing',
                notes=f'Test {update_type}',
                update_type=update_type,
                created_by=self.user
            )
            self.assertEqual(update.update_type, update_type)


class ReferralDocumentModelTest(TestCase):
    """Test cases for ReferralDocument model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.verifier = User.objects.create_user(
            username='verifier',
            email='verifier@example.com',
            password='testpass123',
            user_type='staff'
        )
        
        self.agency = Agency.objects.create(
            name='Test Agency',
            created_by=self.user
        )
        
        self.category = ServiceCategory.objects.create(
            name='Test Category',
            created_by=self.user
        )
        
        self.service = Service.objects.create(
            name='Test Service',
            description='Test description',
            category=self.category,
            agency=self.agency,
            created_by=self.user
        )
        
        self.referral = Referral.objects.create(
            constituent=self.user,
            service=self.service,
            description='Test referral',
            created_by=self.user
        )
    
    def create_test_file(self):
        """Create a test file for upload."""
        content = b'This is a test document content'
        return SimpleUploadedFile(
            'test_document.pdf',
            content,
            content_type='application/pdf'
        )
    
    def test_document_creation(self):
        """Test document model creation."""
        test_file = self.create_test_file()
        
        document = ReferralDocument.objects.create(
            referral=self.referral,
            name='Identity Document',
            file=test_file,
            file_size=len(test_file.read()),
            file_type='application/pdf',
            document_type='id_document',
            created_by=self.user
        )
        
        self.assertEqual(document.referral, self.referral)
        self.assertEqual(document.name, 'Identity Document')
        self.assertEqual(document.document_type, 'id_document')
        self.assertEqual(document.file_type, 'application/pdf')
        self.assertFalse(document.is_verified)
        self.assertEqual(document.created_by, self.user)
    
    def test_document_str_method(self):
        """Test string representation."""
        test_file = self.create_test_file()
        
        document = ReferralDocument.objects.create(
            referral=self.referral,
            name='Test Document',
            file=test_file,
            created_by=self.user
        )
        
        expected_str = f"Document for {self.referral.reference_number} - Test Document"
        self.assertEqual(str(document), expected_str)
    
    def test_document_verification(self):
        """Test document verification functionality."""
        test_file = self.create_test_file()
        
        document = ReferralDocument.objects.create(
            referral=self.referral,
            name='Proof of Income',
            file=test_file,
            document_type='proof_of_income',
            created_by=self.user
        )
        
        # Verify document
        document.is_verified = True
        document.verified_at = timezone.now()
        document.verified_by = self.verifier
        document.save()
        
        document.refresh_from_db()
        self.assertTrue(document.is_verified)
        self.assertIsNotNone(document.verified_at)
        self.assertEqual(document.verified_by, self.verifier)
    
    def test_document_types(self):
        """Test different document types."""
        document_types = [
            'id_document', 'proof_of_income', 'medical_certificate',
            'barangay_certificate', 'application_form', 'supporting_document', 'other'
        ]
        
        for doc_type in document_types:
            test_file = self.create_test_file()
            document = ReferralDocument.objects.create(
                referral=self.referral,
                name=f'Test {doc_type}',
                file=test_file,
                document_type=doc_type,
                created_by=self.user
            )
            self.assertEqual(document.document_type, doc_type)
    
    def test_document_ordering(self):
        """Test document ordering by created_at descending."""
        test_file1 = self.create_test_file()
        test_file2 = self.create_test_file()
        
        doc1 = ReferralDocument.objects.create(
            referral=self.referral,
            name='First Document',
            file=test_file1,
            created_by=self.user
        )
        
        doc2 = ReferralDocument.objects.create(
            referral=self.referral,
            name='Second Document',
            file=test_file2,
            created_by=self.user
        )
        
        documents = list(ReferralDocument.objects.all())
        self.assertEqual(documents[0], doc2)  # Most recent first
        self.assertEqual(documents[1], doc1)
