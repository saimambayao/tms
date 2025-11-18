"""
Comprehensive unit tests for the Search app.
Tests models, search functionality, and search analytics including saved searches,
search history tracking, and search suggestions.
"""
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import SavedSearch, SearchHistory, SearchSuggestion

User = get_user_model()


class SavedSearchModelTest(TestCase):
    """Test cases for SavedSearch model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='staff'
        )
        
        self.saved_search = SavedSearch.objects.create(
            user=self.user,
            name='High Priority Referrals',
            query='urgent medical',
            filters={
                'priority': 'high',
                'category': 'healthcare',
                'status': 'processing'
            },
            module='referrals',
            is_public=False
        )
    
    def test_saved_search_creation(self):
        """Test saved search model creation."""
        self.assertEqual(self.saved_search.user, self.user)
        self.assertEqual(self.saved_search.name, 'High Priority Referrals')
        self.assertEqual(self.saved_search.query, 'urgent medical')
        self.assertEqual(self.saved_search.module, 'referrals')
        self.assertFalse(self.saved_search.is_public)
        self.assertEqual(self.saved_search.use_count, 0)
        self.assertIsInstance(self.saved_search.id, uuid.UUID)
    
    def test_saved_search_str_method(self):
        """Test string representation."""
        expected_str = f"High Priority Referrals ({self.user.email})"
        self.assertEqual(str(self.saved_search), expected_str)
    
    def test_saved_search_uuid_generation(self):
        """Test UUID primary key generation."""
        # Create another saved search
        search2 = SavedSearch.objects.create(
            user=self.user,
            name='Another Search',
            module='constituents'
        )
        
        # Both should have different UUIDs
        self.assertNotEqual(self.saved_search.id, search2.id)
        self.assertIsInstance(search2.id, uuid.UUID)
    
    def test_saved_search_filters_json(self):
        """Test JSON field for filters."""
        complex_filters = {
            'date_range': {
                'start': '2024-01-01',
                'end': '2024-12-31'
            },
            'tags': ['urgent', 'medical', 'elderly'],
            'numeric_range': {
                'min_age': 60,
                'max_age': 100
            },
            'boolean_flags': {
                'has_documents': True,
                'is_verified': False
            }
        }
        
        self.saved_search.filters = complex_filters
        self.saved_search.save()
        
        self.saved_search.refresh_from_db()
        self.assertEqual(self.saved_search.filters, complex_filters)
        self.assertEqual(self.saved_search.filters['tags'][0], 'urgent')
        self.assertEqual(self.saved_search.filters['numeric_range']['min_age'], 60)
    
    def test_increment_use_count(self):
        """Test increment_use_count method."""
        initial_count = self.saved_search.use_count
        initial_last_used = self.saved_search.last_used
        
        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.1)
        
        self.saved_search.increment_use_count()
        
        self.saved_search.refresh_from_db()
        self.assertEqual(self.saved_search.use_count, initial_count + 1)
        self.assertGreater(self.saved_search.last_used, initial_last_used)
        
        # Test multiple increments
        self.saved_search.increment_use_count()
        self.saved_search.increment_use_count()
        
        self.saved_search.refresh_from_db()
        self.assertEqual(self.saved_search.use_count, initial_count + 3)
    
    def test_saved_search_ordering(self):
        """Test saved search ordering by last_used descending."""
        # Create another search and modify its last_used
        search2 = SavedSearch.objects.create(
            user=self.user,
            name='Older Search',
            module='constituents'
        )
        
        # Make search2 older
        older_time = timezone.now() - timedelta(hours=1)
        SavedSearch.objects.filter(pk=search2.pk).update(last_used=older_time)
        
        searches = list(SavedSearch.objects.all())
        self.assertEqual(searches[0], self.saved_search)  # Most recently used first
        self.assertEqual(searches[1], search2)
    
    def test_saved_search_module_choices(self):
        """Test module field choices."""
        valid_modules = [
            'all', 'constituents', 'referrals', 'chapters', 
            'services', 'documents', 'parliamentary'
        ]
        
        for module in valid_modules:
            search = SavedSearch.objects.create(
                user=self.user,
                name=f'Search for {module}',
                module=module
            )
            self.assertEqual(search.module, module)
    
    def test_public_vs_private_searches(self):
        """Test public and private search functionality."""
        # Create public search
        public_search = SavedSearch.objects.create(
            user=self.user,
            name='Public Search',
            query='general query',
            module='all',
            is_public=True
        )
        
        self.assertTrue(public_search.is_public)
        self.assertFalse(self.saved_search.is_public)
        
        # Test filtering public searches
        public_searches = SavedSearch.objects.filter(is_public=True)
        private_searches = SavedSearch.objects.filter(is_public=False)
        
        self.assertIn(public_search, public_searches)
        self.assertNotIn(self.saved_search, public_searches)
        self.assertIn(self.saved_search, private_searches)


class SearchHistoryModelTest(TestCase):
    """Test cases for SearchHistory model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='searcher',
            email='searcher@example.com',
            password='testpass123'
        )
        
        self.search_history = SearchHistory.objects.create(
            user=self.user,
            query='medical assistance',
            module='referrals',
            filters={'priority': 'high'},
            result_count=15,
            search_duration=0.245
        )
    
    def test_search_history_creation(self):
        """Test search history model creation."""
        self.assertEqual(self.search_history.user, self.user)
        self.assertEqual(self.search_history.query, 'medical assistance')
        self.assertEqual(self.search_history.module, 'referrals')
        self.assertEqual(self.search_history.result_count, 15)
        self.assertEqual(self.search_history.search_duration, 0.245)
        self.assertIsInstance(self.search_history.id, uuid.UUID)
    
    def test_search_history_str_method(self):
        """Test string representation."""
        expected_str = f"medical assistance by {self.user.email} at {self.search_history.created_at}"
        self.assertEqual(str(self.search_history), expected_str)
    
    def test_search_history_ordering(self):
        """Test search history ordering by created_at descending."""
        # Create older search history
        older_search = SearchHistory.objects.create(
            user=self.user,
            query='older query',
            module='constituents'
        )
        
        # Manually set older created_at
        older_time = timezone.now() - timedelta(hours=2)
        SearchHistory.objects.filter(pk=older_search.pk).update(created_at=older_time)
        
        history = list(SearchHistory.objects.all())
        self.assertEqual(history[0], self.search_history)  # Most recent first
        self.assertEqual(history[1], older_search)
    
    def test_search_history_filters_json(self):
        """Test JSON field for search filters."""
        complex_filters = {
            'text_filters': {
                'name': 'contains:medical',
                'description': 'startswith:urgent'
            },
            'date_filters': {
                'created_after': '2024-01-01',
                'updated_before': '2024-12-31'
            },
            'multi_select': ['healthcare', 'emergency', 'senior_care'],
            'ranges': {
                'age': {'min': 18, 'max': 65},
                'amount': {'min': 1000, 'max': 50000}
            }
        }
        
        self.search_history.filters = complex_filters
        self.search_history.save()
        
        self.search_history.refresh_from_db()
        self.assertEqual(self.search_history.filters, complex_filters)
        self.assertEqual(self.search_history.filters['ranges']['age']['min'], 18)
    
    def test_search_performance_tracking(self):
        """Test search performance tracking."""
        # Test various search durations
        fast_search = SearchHistory.objects.create(
            user=self.user,
            query='fast query',
            module='all',
            result_count=5,
            search_duration=0.05
        )
        
        slow_search = SearchHistory.objects.create(
            user=self.user,
            query='complex query with lots of filters',
            module='all',
            result_count=1250,
            search_duration=2.8
        )
        
        self.assertLess(fast_search.search_duration, 0.1)
        self.assertGreater(slow_search.search_duration, 2.0)
        self.assertGreater(slow_search.result_count, fast_search.result_count)
    
    def test_search_result_tracking(self):
        """Test search result count tracking."""
        # Create searches with different result counts
        no_results = SearchHistory.objects.create(
            user=self.user,
            query='nonexistent query',
            module='all',
            result_count=0
        )
        
        many_results = SearchHistory.objects.create(
            user=self.user,
            query='common query',
            module='all',
            result_count=1000
        )
        
        self.assertEqual(no_results.result_count, 0)
        self.assertEqual(many_results.result_count, 1000)
        
        # Test filtering by result count
        successful_searches = SearchHistory.objects.filter(result_count__gt=0)
        empty_searches = SearchHistory.objects.filter(result_count=0)
        
        self.assertIn(self.search_history, successful_searches)
        self.assertIn(many_results, successful_searches)
        self.assertNotIn(no_results, successful_searches)
        self.assertIn(no_results, empty_searches)


class SearchSuggestionModelTest(TestCase):
    """Test cases for SearchSuggestion model."""
    
    def setUp(self):
        """Set up test data."""
        self.suggestion = SearchSuggestion.objects.create(
            keyword='medical assistance',
            frequency=5,
            module='referrals'
        )
    
    def test_search_suggestion_creation(self):
        """Test search suggestion model creation."""
        self.assertEqual(self.suggestion.keyword, 'medical assistance')
        self.assertEqual(self.suggestion.frequency, 5)
        self.assertEqual(self.suggestion.module, 'referrals')
    
    def test_search_suggestion_str_method(self):
        """Test string representation."""
        expected_str = f"medical assistance (5)"
        self.assertEqual(str(self.suggestion), expected_str)
    
    def test_search_suggestion_ordering(self):
        """Test search suggestion ordering by frequency then last_used."""
        # Create suggestions with different frequencies
        high_freq = SearchSuggestion.objects.create(
            keyword='urgent care',
            frequency=10,
            module='referrals'
        )
        
        low_freq = SearchSuggestion.objects.create(
            keyword='general inquiry',
            frequency=2,
            module='constituents'
        )
        
        same_freq = SearchSuggestion.objects.create(
            keyword='elderly care',
            frequency=5,
            module='referrals'
        )
        
        # Manually set older last_used for same_freq
        older_time = timezone.now() - timedelta(hours=1)
        SearchSuggestion.objects.filter(pk=same_freq.pk).update(last_used=older_time)
        
        suggestions = list(SearchSuggestion.objects.all())
        self.assertEqual(suggestions[0], high_freq)  # Highest frequency first
        self.assertEqual(suggestions[1], self.suggestion)  # Same frequency, more recent
        self.assertEqual(suggestions[2], same_freq)  # Same frequency, older
        self.assertEqual(suggestions[3], low_freq)  # Lowest frequency
    
    def test_update_suggestion_new_keyword(self):
        """Test update_suggestion class method with new keyword."""
        # Create new suggestion
        new_suggestion = SearchSuggestion.update_suggestion('emergency medical', 'referrals')
        
        self.assertEqual(new_suggestion.keyword, 'emergency medical')
        self.assertEqual(new_suggestion.frequency, 1)
        self.assertEqual(new_suggestion.module, 'referrals')
        
        # Verify it was created in database
        self.assertTrue(SearchSuggestion.objects.filter(keyword='emergency medical').exists())
    
    def test_update_suggestion_existing_keyword(self):
        """Test update_suggestion class method with existing keyword."""
        initial_frequency = self.suggestion.frequency
        
        # Update existing suggestion
        updated_suggestion = SearchSuggestion.update_suggestion('Medical Assistance', 'referrals')
        
        # Should return the same object with incremented frequency
        self.assertEqual(updated_suggestion.id, self.suggestion.id)
        self.assertEqual(updated_suggestion.frequency, initial_frequency + 1)
        
        # Test case insensitive matching
        self.assertEqual(updated_suggestion.keyword, 'medical assistance')  # lowercase
    
    def test_update_suggestion_case_insensitive(self):
        """Test that update_suggestion is case insensitive."""
        variations = [
            'MEDICAL ASSISTANCE',
            'Medical Assistance',
            'medical ASSISTANCE',
            'MeDiCaL aSsIsTaNcE'
        ]
        
        initial_frequency = self.suggestion.frequency
        
        for variation in variations:
            SearchSuggestion.update_suggestion(variation)
        
        # Should all update the same suggestion
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.frequency, initial_frequency + len(variations))
        
        # Should only have one suggestion with this keyword
        count = SearchSuggestion.objects.filter(keyword__iexact='medical assistance').count()
        self.assertEqual(count, 1)
    
    def test_update_suggestion_without_module(self):
        """Test update_suggestion with empty module."""
        suggestion = SearchSuggestion.update_suggestion('general search')
        
        self.assertEqual(suggestion.keyword, 'general search')
        self.assertEqual(suggestion.module, '')
        self.assertEqual(suggestion.frequency, 1)
    
    def test_keyword_uniqueness(self):
        """Test that keywords are unique."""
        # Try to create duplicate keyword
        with self.assertRaises(Exception):
            SearchSuggestion.objects.create(
                keyword='medical assistance',  # Same as existing
                frequency=1
            )
    
    def test_suggestion_popularity_tracking(self):
        """Test tracking suggestion popularity over time."""
        # Simulate multiple uses
        for i in range(10):
            SearchSuggestion.update_suggestion('popular query')
        
        popular = SearchSuggestion.objects.get(keyword='popular query')
        self.assertEqual(popular.frequency, 10)
        
        # Create less popular suggestion
        for i in range(3):
            SearchSuggestion.update_suggestion('less popular query')
        
        # Check ordering by popularity
        suggestions = list(SearchSuggestion.objects.all()[:2])
        self.assertEqual(suggestions[0].keyword, 'popular query')
        self.assertEqual(suggestions[1].keyword, 'medical assistance')  # Original with frequency 5
    
    def test_module_specific_suggestions(self):
        """Test module-specific suggestion tracking."""
        modules = ['constituents', 'referrals', 'services', 'documents']
        
        for module in modules:
            for i in range(3):
                SearchSuggestion.update_suggestion(f'query for {module}', module)
        
        # Check each module has its suggestion
        for module in modules:
            suggestion = SearchSuggestion.objects.get(keyword=f'query for {module}')
            self.assertEqual(suggestion.module, module)
            self.assertEqual(suggestion.frequency, 3)
        
        # Test filtering by module
        referral_suggestions = SearchSuggestion.objects.filter(module='referrals')
        self.assertEqual(referral_suggestions.count(), 2)  # original + new one