import time
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from typing import Dict, List, Optional, Any
from .models import SearchHistory, SearchSuggestion
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for handling global and module-specific searches using Django models."""
    
    def __init__(self):
        # Define available search modules
        self.modules = [
            'constituents', 'referrals', 'chapters', 
            'services', 'documents', 'staff'
        ]
    
    def global_search(self, query: str, user=None, limit: int = 10) -> Dict[str, List]:
        """Perform a global search across all modules using Django models."""
        start_time = time.time()
        results = {}
        total_results = 0
        
        # Check cache first
        cache_key = f"global_search:{query.lower()}:{limit}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results
        
        # Search each module using Django models
        for module in self.modules:
            try:
                module_results = self._search_django_models(module, query, limit)
                if module_results:
                    results[module] = module_results
                    total_results += len(module_results)
            except Exception as e:
                logger.error(f"Error searching {module}: {str(e)}")
        
        # Store search history
        search_duration = time.time() - start_time
        if user and user.is_authenticated:
            SearchHistory.objects.create(
                user=user,
                query=query,
                module='all',
                result_count=total_results,
                search_duration=search_duration
            )
        
        # Update search suggestions
        SearchSuggestion.update_suggestion(query, 'all')
        
        # Cache results
        cache.set(cache_key, results, 300)  # Cache for 5 minutes
        
        return results
    
    def search_module(self, module: str, query: str = None, filters: Dict = None, 
                      sort: Dict = None, limit: int = None, user=None) -> List:
        """Search within a specific module using Django models."""
        if module not in self.modules:
            raise ValueError(f"Unknown module: {module}")
        
        start_time = time.time()
        
        try:
            results = self._search_django_models(module, query, limit, filters, sort)
            
            # Store search history
            search_duration = time.time() - start_time
            if user and user.is_authenticated:
                SearchHistory.objects.create(
                    user=user,
                    query=query or '',
                    module=module,
                    filters=filters or {},
                    result_count=len(results),
                    search_duration=search_duration
                )
            
            # Update search suggestions if query provided
            if query:
                SearchSuggestion.update_suggestion(query, module)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching {module}: {str(e)}")
            raise
    
    def _search_django_models(self, module: str, query: str = None, 
                              limit: int = None, filters: Dict = None, sort: Dict = None) -> List:
        """Search Django models based on module type."""
        results = []
        
        try:
            if module == 'constituents':
                from apps.constituents.models import ConstituentProfile
                queryset = ConstituentProfile.objects.all()
                if query:
                    queryset = queryset.filter(
                        Q(full_name__icontains=query) |
                        Q(contact_number__icontains=query) |
                        Q(email__icontains=query) |
                        Q(complete_address__icontains=query)
                    )
                results = self._format_constituent_results(queryset[:limit])
                
            elif module == 'referrals':
                from apps.referrals.models import Referral
                queryset = Referral.objects.all()
                if query:
                    queryset = queryset.filter(
                        Q(title__icontains=query) |
                        Q(description__icontains=query) |
                        Q(reference_number__icontains=query)
                    )
                results = self._format_referral_results(queryset[:limit])
                
            elif module == 'chapters':
                from apps.chapters.models import Chapter
                queryset = Chapter.objects.all()
                if query:
                    queryset = queryset.filter(
                        Q(name__icontains=query) |
                        Q(municipality__icontains=query) |
                        Q(province__icontains=query)
                    )
                results = self._format_chapter_results(queryset[:limit])
                
            elif module == 'staff':
                from apps.staff.models import Staff
                queryset = Staff.objects.filter(is_active=True)
                if query:
                    queryset = queryset.filter(
                        Q(full_name__icontains=query) |
                        Q(position__icontains=query) |
                        Q(email__icontains=query)
                    )
                results = self._format_staff_results(queryset[:limit])
                
            elif module == 'documents':
                from apps.documents.models import Document
                queryset = Document.objects.filter(status='approved')
                if query:
                    queryset = queryset.filter(
                        Q(title__icontains=query) |
                        Q(description__icontains=query)
                    )
                results = self._format_document_results(queryset[:limit])
                
            elif module == 'services':
                from apps.services.models import ServiceProgram
                queryset = ServiceProgram.objects.filter(status='active')
                if query:
                    queryset = queryset.filter(
                        Q(title__icontains=query) |
                        Q(description__icontains=query)
                    )
                results = self._format_service_results(queryset[:limit])
            
        except Exception as e:
            logger.error(f"Error searching Django models for {module}: {str(e)}")
            return []
        
        return results
    
    def _format_constituent_results(self, queryset) -> List:
        """Format constituent search results."""
        results = []
        for obj in queryset:
            results.append({
                'id': obj.id,
                'module': 'constituents',
                'display_title': obj.full_name,
                'properties': {
                    'name': obj.full_name,
                    'contact_number': obj.contact_number,
                    'email': obj.email,
                    'municipality': obj.municipality,
                    'barangay': obj.barangay,
                },
                'created_time': obj.created_at.isoformat() if obj.created_at else None,
                'last_edited_time': obj.updated_at.isoformat() if obj.updated_at else None,
            })
        return results
    
    def _format_referral_results(self, queryset) -> List:
        """Format referral search results."""
        results = []
        for obj in queryset:
            results.append({
                'id': obj.id,
                'module': 'referrals',
                'display_title': obj.title or f"Referral #{obj.reference_number}",
                'properties': {
                    'title': obj.title,
                    'reference_number': obj.reference_number,
                    'status': obj.status,
                    'urgency_level': obj.urgency_level,
                },
                'created_time': obj.created_at.isoformat() if obj.created_at else None,
                'last_edited_time': obj.updated_at.isoformat() if obj.updated_at else None,
            })
        return results
    
    def _format_chapter_results(self, queryset) -> List:
        """Format chapter search results."""
        results = []
        for obj in queryset:
            results.append({
                'id': obj.id,
                'module': 'chapters',
                'display_title': obj.name,
                'properties': {
                    'name': obj.name,
                    'municipality': obj.municipality,
                    'province': obj.province,
                    'tier': obj.tier,
                    'status': obj.status,
                },
                'created_time': obj.created_at.isoformat() if obj.created_at else None,
                'last_edited_time': obj.updated_at.isoformat() if obj.updated_at else None,
            })
        return results
    
    def _format_staff_results(self, queryset) -> List:
        """Format staff search results."""
        results = []
        for obj in queryset:
            results.append({
                'id': obj.id,
                'module': 'staff',
                'display_title': obj.full_name,
                'properties': {
                    'name': obj.full_name,
                    'position': obj.position,
                    'email': obj.email,
                    'division': obj.division,
                    'employment_status': obj.employment_status,
                },
                'created_time': obj.created_at.isoformat() if obj.created_at else None,
                'last_edited_time': obj.updated_at.isoformat() if obj.updated_at else None,
            })
        return results
    
    def _format_document_results(self, queryset) -> List:
        """Format document search results."""
        results = []
        for obj in queryset:
            results.append({
                'id': obj.id,
                'module': 'documents',
                'display_title': obj.title,
                'properties': {
                    'title': obj.title,
                    'description': obj.description,
                    'document_type': obj.document_type,
                    'status': obj.status,
                },
                'created_time': obj.created_at.isoformat() if obj.created_at else None,
                'last_edited_time': obj.updated_at.isoformat() if obj.updated_at else None,
            })
        return results
    
    def _format_service_results(self, queryset) -> List:
        """Format service search results."""
        results = []
        for obj in queryset:
            results.append({
                'id': obj.id,
                'module': 'services',
                'display_title': obj.title,
                'properties': {
                    'title': obj.title,
                    'description': obj.description,
                    'status': obj.status,
                    'category': getattr(obj, 'category', ''),
                },
                'created_time': obj.created_at.isoformat() if obj.created_at else None,
                'last_edited_time': obj.updated_at.isoformat() if obj.updated_at else None,
            })
        return results
    
    def get_search_suggestions(self, query: str, module: str = None, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query."""
        suggestions = SearchSuggestion.objects.filter(
            keyword__istartswith=query.lower()
        )
        
        if module:
            suggestions = suggestions.filter(
                Q(module=module) | Q(module='')
            )
        
        suggestions = suggestions[:limit]
        
        return [s.keyword for s in suggestions]
    
    def get_popular_searches(self, module: str = None, limit: int = 5) -> List[str]:
        """Get popular searches for a module."""
        suggestions = SearchSuggestion.objects.all()
        
        if module:
            suggestions = suggestions.filter(
                Q(module=module) | Q(module='')
            )
        
        suggestions = suggestions[:limit]
        
        return [s.keyword for s in suggestions]