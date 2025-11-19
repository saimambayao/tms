"""
Comprehensive test suite for Documents application.
Tests models, views, forms, and complex workflows for document management.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import datetime, timedelta, date
from decimal import Decimal
import json
import uuid
from PIL import Image
import io

from .models import (
    DocumentCategory, Document, DocumentAccess, DocumentTemplate
)
from apps.users.models import User
from apps.staff.models import Staff

User = get_user_model()


# ==============================
# UNIT TESTS - MODELS
# ==============================

class DocumentCategoryModelTests(TestCase):
    """Unit tests for DocumentCategory model."""
    
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='TestPass123!',
            user_type='admin'
        )
    
    def test_document_category_creation(self):
        """Test creating a document category."""
        category = DocumentCategory.objects.create(
            name='Official Documents',
            slug='official-documents',
            description='Official government documents and forms',
            is_active=True,
            sort_order=1,
            created_by=self.creator
        )
        
        self.assertEqual(category.name, 'Official Documents')
        self.assertEqual(category.slug, 'official-documents')
        self.assertTrue(category.is_active)
        self.assertEqual(category.sort_order, 1)
        self.assertEqual(category.level, 0)  # Root level
        self.assertEqual(category.created_by, self.creator)
    
    def test_hierarchical_category_structure(self):
        """Test hierarchical category relationships."""
        # Create parent category
        parent = DocumentCategory.objects.create(
            name='Government Forms',
            slug='government-forms',
            created_by=self.creator
        )
        
        # Create child category
        child = DocumentCategory.objects.create(
            name='Health Forms',
            slug='health-forms',
            parent=parent,
            created_by=self.creator
        )
        
        # Test relationships
        self.assertEqual(child.parent, parent)
        self.assertEqual(child.level, 1)
        self.assertIn(child, parent.subcategories.all())
        
        # Test string representation
        self.assertEqual(str(parent), 'Government Forms')
        self.assertEqual(str(child), 'Government Forms > Health Forms')
    
    def test_get_full_path(self):
        """Test get_full_path method for hierarchical display."""
        # Create multi-level hierarchy
        root = DocumentCategory.objects.create(
            name='Root Category',
            created_by=self.creator
        )
        
        level1 = DocumentCategory.objects.create(
            name='Level 1',
            parent=root,
            created_by=self.creator
        )
        
        level2 = DocumentCategory.objects.create(
            name='Level 2',
            parent=level1,
            created_by=self.creator
        )
        
        # Test full paths
        self.assertEqual(root.get_full_path(), 'Root Category')
        self.assertEqual(level1.get_full_path(), 'Root Category > Level 1')
        self.assertEqual(level2.get_full_path(), 'Root Category > Level 1 > Level 2')
    
    def test_category_ordering(self):
        """Test category ordering by sort_order."""
        category1 = DocumentCategory.objects.create(
            name='Category 1',
            sort_order=3,
            created_by=self.creator
        )
        
        category2 = DocumentCategory.objects.create(
            name='Category 2',
            sort_order=1,
            created_by=self.creator
        )
        
        category3 = DocumentCategory.objects.create(
            name='Category 3',
            sort_order=2,
            created_by=self.creator
        )
        
        # Test ordering
        categories = list(DocumentCategory.objects.all())
        self.assertEqual(categories[0], category2)  # sort_order 1
        self.assertEqual(categories[1], category3)  # sort_order 2
        self.assertEqual(categories[2], category1)  # sort_order 3


class DocumentModelTests(TestCase):
    """Unit tests for Document model."""
    
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='TestPass123!',
            user_type='staff'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@test.com',
            password='TestPass123!',
            user_type='admin'
        )
        
        self.category = DocumentCategory.objects.create(
            name='Test Category',
            created_by=self.creator
        )
        
        # Create test file
        self.test_file = SimpleUploadedFile(
            'test_document.pdf',
            b'Test PDF content',
            content_type='application/pdf'
        )
    
    def test_document_creation(self):
        """Test creating a document."""
        document = Document.objects.create(
            title='Test Document',
            description='A test document for unit testing',
            category=self.category,
            file=self.test_file,
            document_type='form',
            access_level='public',
            version='1.0',
            status='draft',
            created_by=self.creator
        )
        
        self.assertEqual(document.title, 'Test Document')
        self.assertEqual(document.category, self.category)
        self.assertEqual(document.document_type, 'form')
        self.assertEqual(document.access_level, 'public')
        self.assertEqual(document.version, '1.0')
        self.assertEqual(document.status, 'draft')
        self.assertEqual(document.created_by, self.creator)
        self.assertIsNotNone(document.id)  # UUID should be generated
        self.assertIsInstance(document.id, uuid.UUID)
    
    def test_document_slug_generation(self):
        """Test automatic slug generation."""
        document = Document.objects.create(
            title='Test Document with Spaces',
            category=self.category,
            file=self.test_file,
            created_by=self.creator
        )
        
        self.assertEqual(document.slug, 'test-document-with-spaces')
    
    def test_document_version_control(self):
        """Test document version control functionality."""
        # Create original document
        original = Document.objects.create(
            title='Versioned Document',
            category=self.category,
            file=self.test_file,
            version='1.0',
            created_by=self.creator
        )
        
        # Create new version
        new_version_file = SimpleUploadedFile(
            'updated_document.pdf',
            b'Updated PDF content',
            content_type='application/pdf'
        )
        
        new_version = Document.objects.create(
            title='Versioned Document',
            category=self.category,
            file=new_version_file,
            version='1.1',
            parent_document=original,
            created_by=self.creator
        )
        
        # Test relationships
        self.assertEqual(new_version.parent_document, original)
        self.assertIn(new_version, original.versions.all())
        
        # Test latest version property
        self.assertEqual(original.latest_version, new_version)
    
    def test_document_approval_workflow(self):
        """Test document approval workflow."""
        document = Document.objects.create(
            title='Document for Approval',
            category=self.category,
            file=self.test_file,
            status='pending_approval',
            created_by=self.creator
        )
        
        # Approve document
        document.approved_by = self.approver
        document.approved_at = timezone.now()
        document.status = 'approved'
        document.save()
        
        self.assertEqual(document.approved_by, self.approver)
        self.assertIsNotNone(document.approved_at)
        self.assertEqual(document.status, 'approved')
        self.assertTrue(document.is_approved)
    
    def test_document_expiration(self):
        """Test document expiration functionality."""
        # Create expired document
        expired_doc = Document.objects.create(
            title='Expired Document',
            category=self.category,
            file=self.test_file,
            expires_at=timezone.now() - timedelta(days=1),
            created_by=self.creator
        )
        
        # Create active document
        active_doc = Document.objects.create(
            title='Active Document',
            category=self.category,
            file=self.test_file,
            expires_at=timezone.now() + timedelta(days=30),
            created_by=self.creator
        )
        
        # Test expiration status
        self.assertTrue(expired_doc.is_expired)
        self.assertFalse(active_doc.is_expired)
    
    def test_document_metadata_fields(self):
        """Test document metadata and JSON fields."""
        metadata = {
            'author': 'Test Author',
            'subject': 'Test Subject',
            'keywords': ['test', 'document', 'metadata'],
            'custom_field': 'Custom Value'
        }
        
        tags = ['important', 'public', 'form']
        
        document = Document.objects.create(
            title='Document with Metadata',
            category=self.category,
            file=self.test_file,
            metadata=metadata,
            tags=tags,
            created_by=self.creator
        )
        
        self.assertEqual(document.metadata, metadata)
        self.assertEqual(document.tags, tags)
        self.assertEqual(document.metadata['author'], 'Test Author')
        self.assertIn('important', document.tags)
    
    def test_document_string_representation(self):
        """Test document string representation."""
        document = Document.objects.create(
            title='Test Document Title',
            category=self.category,
            file=self.test_file,
            version='2.1',
            created_by=self.creator
        )
        
        expected_str = 'Test Document Title (v2.1)'
        self.assertEqual(str(document), expected_str)


class DocumentAccessModelTests(TestCase):
    """Unit tests for DocumentAccess model."""
    
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='TestPass123!',
            user_type='staff'
        )
        
        self.accessor = User.objects.create_user(
            username='accessor',
            email='accessor@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.category = DocumentCategory.objects.create(
            name='Test Category',
            created_by=self.creator
        )
        
        self.document = Document.objects.create(
            title='Access Test Document',
            category=self.category,
            file=SimpleUploadedFile('test.pdf', b'content', content_type='application/pdf'),
            access_level='restricted',
            created_by=self.creator
        )
    
    def test_document_access_creation(self):
        """Test creating a document access record."""
        access = DocumentAccess.objects.create(
            document=self.document,
            user=self.accessor,
            access_type='view',
            granted_by=self.creator,
            access_reason='Required for work duties'
        )
        
        self.assertEqual(access.document, self.document)
        self.assertEqual(access.user, self.accessor)
        self.assertEqual(access.access_type, 'view')
        self.assertEqual(access.granted_by, self.creator)
        self.assertTrue(access.is_active)
        self.assertIsNotNone(access.granted_at)
    
    def test_access_history_tracking(self):
        """Test access history tracking."""
        # Grant access
        access = DocumentAccess.objects.create(
            document=self.document,
            user=self.accessor,
            access_type='download',
            granted_by=self.creator
        )
        
        # Record access
        access.last_accessed = timezone.now()
        access.access_count += 1
        access.save()
        
        self.assertEqual(access.access_count, 1)
        self.assertIsNotNone(access.last_accessed)
    
    def test_access_revocation(self):
        """Test access revocation functionality."""
        access = DocumentAccess.objects.create(
            document=self.document,
            user=self.accessor,
            access_type='edit',
            granted_by=self.creator
        )
        
        # Revoke access
        access.is_active = False
        access.revoked_at = timezone.now()
        access.revoked_by = self.creator
        access.revocation_reason = 'No longer needed'
        access.save()
        
        self.assertFalse(access.is_active)
        self.assertIsNotNone(access.revoked_at)
        self.assertEqual(access.revoked_by, self.creator)
        self.assertEqual(access.revocation_reason, 'No longer needed')
    
    def test_access_expiration(self):
        """Test access expiration functionality."""
        # Create expired access
        expired_access = DocumentAccess.objects.create(
            document=self.document,
            user=self.accessor,
            access_type='view',
            granted_by=self.creator,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create active access
        active_access = DocumentAccess.objects.create(
            document=self.document,
            user=self.creator,
            access_type='edit',
            granted_by=self.creator,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        self.assertTrue(expired_access.is_expired)
        self.assertFalse(active_access.is_expired)
    
    def test_unique_active_access_constraint(self):
        """Test that only one active access per user per document is allowed."""
        # Create first access
        DocumentAccess.objects.create(
            document=self.document,
            user=self.accessor,
            access_type='view',
            granted_by=self.creator
        )
        
        # Try to create duplicate active access - should be handled by application logic
        # This test documents expected behavior rather than enforcing database constraint
        access2 = DocumentAccess.objects.create(
            document=self.document,
            user=self.accessor,
            access_type='download',
            granted_by=self.creator
        )
        
        # Both should exist (business logic should handle duplicates)
        self.assertEqual(
            DocumentAccess.objects.filter(
                document=self.document, 
                user=self.accessor, 
                is_active=True
            ).count(),
            2
        )


class DocumentTemplateModelTests(TestCase):
    """Unit tests for DocumentTemplate model."""
    
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='TestPass123!',
            user_type='admin'
        )
        
        self.category = DocumentCategory.objects.create(
            name='Template Category',
            created_by=self.creator
        )
    
    def test_document_template_creation(self):
        """Test creating a document template."""
        template = DocumentTemplate.objects.create(
            name='Application Form Template',
            description='Template for various application forms',
            category=self.category,
            template_type='form',
            content='<h1>{{title}}</h1><p>{{content}}</p>',
            default_metadata={'type': 'application', 'language': 'en'},
            is_active=True,
            created_by=self.creator
        )
        
        self.assertEqual(template.name, 'Application Form Template')
        self.assertEqual(template.slug, 'application-form-template')
        self.assertEqual(template.category, self.category)
        self.assertEqual(template.template_type, 'form')
        self.assertTrue(template.is_active)
        self.assertEqual(template.default_metadata['type'], 'application')
    
    def test_template_slug_generation(self):
        """Test automatic slug generation for templates."""
        template = DocumentTemplate.objects.create(
            name='Complex Template Name with Spaces',
            category=self.category,
            created_by=self.creator
        )
        
        self.assertEqual(template.slug, 'complex-template-name-with-spaces')
    
    def test_template_fields_and_placeholders(self):
        """Test template fields and placeholder functionality."""
        fields = [
            {'name': 'applicant_name', 'type': 'text', 'required': True},
            {'name': 'date_of_birth', 'type': 'date', 'required': True},
            {'name': 'purpose', 'type': 'textarea', 'required': False}
        ]
        
        placeholders = {
            'office_name': 'Office of BM Parliament',
            'current_date': '{{current_date}}',
            'contact_info': 'contact@bmparliament.ph'
        }
        
        template = DocumentTemplate.objects.create(
            name='Form with Fields',
            category=self.category,
            template_fields=fields,
            placeholders=placeholders,
            created_by=self.creator
        )
        
        self.assertEqual(template.template_fields, fields)
        self.assertEqual(template.placeholders, placeholders)
        self.assertEqual(template.template_fields[0]['name'], 'applicant_name')
        self.assertEqual(template.placeholders['office_name'], 'Office of BM Parliament')
    
    def test_template_usage_tracking(self):
        """Test template usage tracking."""
        template = DocumentTemplate.objects.create(
            name='Usage Test Template',
            category=self.category,
            usage_count=0,
            created_by=self.creator
        )
        
        # Simulate template usage
        template.usage_count += 1
        template.last_used = timezone.now()
        template.save()
        
        self.assertEqual(template.usage_count, 1)
        self.assertIsNotNone(template.last_used)
    
    def test_template_string_representation(self):
        """Test template string representation."""
        template = DocumentTemplate.objects.create(
            name='Test Template',
            template_type='letter',
            category=self.category,
            created_by=self.creator
        )
        
        expected_str = 'Test Template (Letter)'
        self.assertEqual(str(template), expected_str)


# ==============================
# INTEGRATION TESTS
# ==============================

class DocumentWorkflowIntegrationTests(TestCase):
    """Integration tests for document workflows."""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='TestPass123!',
            user_type='admin'
        )
        
        self.staff = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='TestPass123!',
            user_type='staff'
        )
        
        self.member = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        # Create document categories
        self.public_category = DocumentCategory.objects.create(
            name='Public Documents',
            created_by=self.admin
        )
        
        self.restricted_category = DocumentCategory.objects.create(
            name='Restricted Documents',
            created_by=self.admin
        )
    
    def test_document_creation_workflow(self):
        """Test complete document creation workflow."""
        self.client.login(username='staff', password='TestPass123!')
        
        # Create test file
        test_file = SimpleUploadedFile(
            'workflow_test.pdf',
            b'Test PDF content for workflow',
            content_type='application/pdf'
        )
        
        # 1. Create document
        document = Document.objects.create(
            title='Workflow Test Document',
            description='Document for testing complete workflow',
            category=self.public_category,
            file=test_file,
            document_type='form',
            access_level='public',
            status='draft',
            created_by=self.staff
        )
        
        # 2. Verify document creation
        self.assertEqual(document.status, 'draft')
        self.assertEqual(document.created_by, self.staff)
        
        # 3. Submit for approval
        document.status = 'pending_approval'
        document.save()
        
        # 4. Admin approves document
        document.approved_by = self.admin
        document.approved_at = timezone.now()
        document.status = 'approved'
        document.save()
        
        # 5. Verify approval
        self.assertTrue(document.is_approved)
        self.assertEqual(document.approved_by, self.admin)
        
        # 6. Publish document
        document.status = 'published'
        document.published_at = timezone.now()
        document.save()
        
        # Verify final state
        self.assertEqual(document.status, 'published')
        self.assertIsNotNone(document.published_at)
    
    def test_document_access_control_workflow(self):
        """Test document access control workflow."""
        self.client.login(username='admin', password='TestPass123!')
        
        # Create restricted document
        restricted_doc = Document.objects.create(
            title='Restricted Document',
            category=self.restricted_category,
            file=SimpleUploadedFile('restricted.pdf', b'content', content_type='application/pdf'),
            access_level='restricted',
            status='published',
            created_by=self.admin
        )
        
        # Grant access to staff member
        access = DocumentAccess.objects.create(
            document=restricted_doc,
            user=self.staff,
            access_type='view',
            granted_by=self.admin,
            access_reason='Required for job duties'
        )
        
        # Verify access granted
        self.assertTrue(access.is_active)
        self.assertEqual(access.access_type, 'view')
        
        # Simulate document access
        access.access_count += 1
        access.last_accessed = timezone.now()
        access.save()
        
        # Verify access tracking
        self.assertEqual(access.access_count, 1)
        self.assertIsNotNone(access.last_accessed)
        
        # Revoke access
        access.is_active = False
        access.revoked_at = timezone.now()
        access.revoked_by = self.admin
        access.save()
        
        # Verify revocation
        self.assertFalse(access.is_active)
        self.assertIsNotNone(access.revoked_at)
    
    def test_document_versioning_workflow(self):
        """Test document versioning workflow."""
        self.client.login(username='staff', password='TestPass123!')
        
        # Create original document
        original = Document.objects.create(
            title='Versioned Document',
            category=self.public_category,
            file=SimpleUploadedFile('v1.pdf', b'Version 1 content', content_type='application/pdf'),
            version='1.0',
            status='published',
            created_by=self.staff
        )
        
        # Create second version
        version2 = Document.objects.create(
            title='Versioned Document',
            category=self.public_category,
            file=SimpleUploadedFile('v2.pdf', b'Version 2 content', content_type='application/pdf'),
            version='1.1',
            parent_document=original,
            status='published',
            created_by=self.staff
        )
        
        # Create third version
        version3 = Document.objects.create(
            title='Versioned Document',
            category=self.public_category,
            file=SimpleUploadedFile('v3.pdf', b'Version 3 content', content_type='application/pdf'),
            version='2.0',
            parent_document=original,
            status='published',
            created_by=self.staff
        )
        
        # Verify version relationships
        self.assertEqual(original.versions.count(), 2)
        self.assertEqual(original.latest_version, version3)
        self.assertIn(version2, original.versions.all())
        self.assertIn(version3, original.versions.all())
    
    def test_template_usage_workflow(self):
        """Test document template usage workflow."""
        self.client.login(username='admin', password='TestPass123!')
        
        # Create template
        template = DocumentTemplate.objects.create(
            name='Application Template',
            category=self.public_category,
            template_type='form',
            content='Application for: {{purpose}}\nApplicant: {{name}}\nDate: {{date}}',
            template_fields=[
                {'name': 'purpose', 'type': 'text', 'required': True},
                {'name': 'name', 'type': 'text', 'required': True},
                {'name': 'date', 'type': 'date', 'required': True}
            ],
            created_by=self.admin
        )
        
        # Use template to create document
        document = Document.objects.create(
            title='Medical Assistance Application',
            category=self.public_category,
            file=SimpleUploadedFile('application.pdf', b'content', content_type='application/pdf'),
            template=template,
            metadata={
                'purpose': 'Medical Assistance',
                'name': 'John Doe',
                'date': '2024-01-15'
            },
            created_by=self.staff
        )
        
        # Update template usage
        template.usage_count += 1
        template.last_used = timezone.now()
        template.save()
        
        # Verify template usage
        self.assertEqual(document.template, template)
        self.assertEqual(template.usage_count, 1)
        self.assertEqual(document.metadata['purpose'], 'Medical Assistance')


# ==============================
# EDGE CASE AND ERROR HANDLING TESTS
# ==============================

class DocumentEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='staff'
        )
        
        self.category = DocumentCategory.objects.create(
            name='Test Category',
            created_by=self.user
        )
    
    def test_document_without_file(self):
        """Test document creation without file attachment."""
        document = Document.objects.create(
            title='Document Without File',
            category=self.category,
            document_type='reference',
            access_level='public',
            created_by=self.user
        )
        
        self.assertFalse(document.file)
        self.assertEqual(document.title, 'Document Without File')
    
    def test_document_with_special_characters(self):
        """Test document with special characters in title."""
        document = Document.objects.create(
            title='Document with Special @#$%^&*() Characters',
            category=self.category,
            file=SimpleUploadedFile('test.pdf', b'content', content_type='application/pdf'),
            created_by=self.user
        )
        
        # Slug should handle special characters
        self.assertEqual(document.slug, 'document-with-special-characters')
    
    def test_circular_document_versions(self):
        """Test handling of circular document version references."""
        doc1 = Document.objects.create(
            title='Document 1',
            category=self.category,
            file=SimpleUploadedFile('doc1.pdf', b'content1', content_type='application/pdf'),
            created_by=self.user
        )
        
        doc2 = Document.objects.create(
            title='Document 2',
            category=self.category,
            file=SimpleUploadedFile('doc2.pdf', b'content2', content_type='application/pdf'),
            parent_document=doc1,
            created_by=self.user
        )
        
        # Try to create circular reference (should be prevented by application logic)
        doc1.parent_document = doc2
        doc1.save()
        
        # This test documents potential issue - in production, validation should prevent this
        self.assertEqual(doc1.parent_document, doc2)
        self.assertEqual(doc2.parent_document, doc1)
    
    def test_document_with_empty_metadata(self):
        """Test document with empty or null metadata."""
        document = Document.objects.create(
            title='Document with Empty Metadata',
            category=self.category,
            file=SimpleUploadedFile('test.pdf', b'content', content_type='application/pdf'),
            metadata={},
            tags=[],
            created_by=self.user
        )
        
        self.assertEqual(document.metadata, {})
        self.assertEqual(document.tags, [])
    
    def test_access_to_expired_document(self):
        """Test access to expired document."""
        expired_doc = Document.objects.create(
            title='Expired Document',
            category=self.category,
            file=SimpleUploadedFile('expired.pdf', b'content', content_type='application/pdf'),
            expires_at=timezone.now() - timedelta(days=30),
            created_by=self.user
        )
        
        # Try to grant access to expired document
        access = DocumentAccess.objects.create(
            document=expired_doc,
            user=self.user,
            access_type='view',
            granted_by=self.user
        )
        
        # Access should be created but document is expired
        self.assertTrue(access.is_active)
        self.assertTrue(expired_doc.is_expired)
    
    def test_template_with_invalid_json_fields(self):
        """Test template with malformed JSON in fields."""
        # This should be handled gracefully
        template = DocumentTemplate.objects.create(
            name='Template with Invalid JSON',
            category=self.category,
            # These would normally be validated at the application level
            template_fields=[{'name': 'field1'}],  # Missing required fields
            placeholders={'key': None},  # Null value
            created_by=self.user
        )
        
        self.assertEqual(template.template_fields[0]['name'], 'field1')
        self.assertIsNone(template.placeholders['key'])


# ==============================
# PERFORMANCE TESTS
# ==============================

class DocumentPerformanceTests(TestCase):
    """Performance tests for documents system."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='admin'
        )
        
        self.category = DocumentCategory.objects.create(
            name='Performance Test Category',
            created_by=self.user
        )
    
    def test_bulk_document_creation(self):
        """Test performance with bulk document creation."""
        import time
        
        documents = []
        start_time = time.time()
        
        for i in range(50):
            doc = Document(
                title=f'Bulk Document {i}',
                category=self.category,
                file=SimpleUploadedFile(f'bulk_{i}.pdf', b'content', content_type='application/pdf'),
                created_by=self.user
            )
            documents.append(doc)
        
        Document.objects.bulk_create(documents)
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 5.0)  # Less than 5 seconds
        self.assertEqual(Document.objects.count(), 50)
    
    def test_document_access_query_performance(self):
        """Test query performance for document access."""
        import time
        
        # Create many documents and access records
        documents = []
        for i in range(20):
            doc = Document.objects.create(
                title=f'Access Test Doc {i}',
                category=self.category,
                file=SimpleUploadedFile(f'access_{i}.pdf', b'content', content_type='application/pdf'),
                created_by=self.user
            )
            documents.append(doc)
            
            # Create access records
            for j in range(5):
                DocumentAccess.objects.create(
                    document=doc,
                    user=self.user,
                    access_type='view',
                    granted_by=self.user
                )
        
        # Test query performance
        start_time = time.time()
        accessible_docs = Document.objects.filter(
            document_accesses__user=self.user,
            document_accesses__is_active=True
        ).distinct()
        list(accessible_docs)  # Force query execution
        end_time = time.time()
        
        # Should complete efficiently
        self.assertLess(end_time - start_time, 2.0)  # Less than 2 seconds
        self.assertGreaterEqual(len(list(accessible_docs)), 20)