"""
Comprehensive unit tests for the Dashboards app.
Tests models, reporting functionality, and dashboard configuration including
reports, scheduled reports, custom dashboards, and widgets.
"""
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime

from .models import Report, ScheduledReport, Dashboard, DashboardWidget

User = get_user_model()


class ReportModelTest(TestCase):
    """Test cases for Report model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='reporter',
            email='reporter@example.com',
            password='testpass123',
            user_type='staff'
        )
        
        self.report = Report.objects.create(
            name='Monthly Referrals Report',
            report_type='referrals',
            created_by=self.user,
            parameters={
                'date_range': {
                    'start': '2024-01-01',
                    'end': '2024-01-31'
                },
                'filters': {
                    'status': 'completed',
                    'priority': 'high'
                },
                'grouping': 'by_service_type'
            },
            file_path='/reports/2024/jan_referrals.pdf',
            format='pdf',
            is_scheduled=False
        )
    
    def test_report_creation(self):
        """Test report model creation."""
        self.assertEqual(self.report.name, 'Monthly Referrals Report')
        self.assertEqual(self.report.report_type, 'referrals')
        self.assertEqual(self.report.created_by, self.user)
        self.assertEqual(self.report.format, 'pdf')
        self.assertFalse(self.report.is_scheduled)
        self.assertIsInstance(self.report.id, uuid.UUID)
    
    def test_report_str_method(self):
        """Test string representation."""
        expected_str = "Monthly Referrals Report (Referrals Report)"
        self.assertEqual(str(self.report), expected_str)
    
    def test_report_uuid_generation(self):
        """Test UUID primary key generation."""
        report2 = Report.objects.create(
            name='Another Report',
            report_type='constituents',
            created_by=self.user
        )
        
        self.assertNotEqual(self.report.id, report2.id)
        self.assertIsInstance(report2.id, uuid.UUID)
    
    def test_report_parameters_json(self):
        """Test JSON field for report parameters."""
        complex_params = {
            'metrics': ['total_count', 'avg_processing_time', 'completion_rate'],
            'filters': {
                'date_range': {
                    'type': 'relative',
                    'period': 'last_30_days'
                },
                'categories': ['healthcare', 'education', 'social_services'],
                'geographic': {
                    'municipalities': ['Cotabato City', 'Maguindanao'],
                    'barangays': ['Central', 'North', 'South']
                }
            },
            'visualization': {
                'charts': [
                    {'type': 'bar', 'data': 'status_breakdown'},
                    {'type': 'line', 'data': 'trend_over_time'},
                    {'type': 'pie', 'data': 'category_distribution'}
                ]
            },
            'export_options': {
                'include_raw_data': True,
                'anonymize_personal_data': True,
                'compress_images': False
            }
        }
        
        self.report.parameters = complex_params
        self.report.save()
        
        self.report.refresh_from_db()
        self.assertEqual(self.report.parameters, complex_params)
        self.assertEqual(self.report.parameters['metrics'][0], 'total_count')
        self.assertEqual(self.report.parameters['filters']['geographic']['municipalities'][0], 'Cotabato City')
    
    def test_report_types(self):
        """Test different report types."""
        report_types = ['referrals', 'constituents', 'chapters', 'services', 'custom']
        
        for report_type in report_types:
            report = Report.objects.create(
                name=f'Test {report_type} Report',
                report_type=report_type,
                created_by=self.user
            )
            self.assertEqual(report.report_type, report_type)
    
    def test_report_formats(self):
        """Test different report formats."""
        formats = ['pdf', 'excel', 'csv']
        
        for format_type in formats:
            report = Report.objects.create(
                name=f'Test {format_type} Report',
                report_type='referrals',
                created_by=self.user,
                format=format_type
            )
            self.assertEqual(report.format, format_type)
    
    def test_report_ordering(self):
        """Test report ordering by created_at descending."""
        older_report = Report.objects.create(
            name='Older Report',
            report_type='constituents',
            created_by=self.user
        )
        
        # Manually set older created_at
        older_time = timezone.now() - timedelta(days=1)
        Report.objects.filter(pk=older_report.pk).update(created_at=older_time)
        
        reports = list(Report.objects.all())
        self.assertEqual(reports[0], self.report)  # Most recent first
        self.assertEqual(reports[1], older_report)
    
    def test_scheduled_vs_manual_reports(self):
        """Test scheduled and manual report functionality."""
        scheduled_report = Report.objects.create(
            name='Scheduled Weekly Report',
            report_type='referrals',
            created_by=self.user,
            is_scheduled=True
        )
        
        self.assertTrue(scheduled_report.is_scheduled)
        self.assertFalse(self.report.is_scheduled)
        
        # Test filtering
        scheduled_reports = Report.objects.filter(is_scheduled=True)
        manual_reports = Report.objects.filter(is_scheduled=False)
        
        self.assertIn(scheduled_report, scheduled_reports)
        self.assertIn(self.report, manual_reports)


class ScheduledReportModelTest(TestCase):
    """Test cases for ScheduledReport model."""
    
    def setUp(self):
        """Set up test data."""
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123',
            user_type='coordinator'
        )
        
        self.recipient1 = User.objects.create_user(
            username='recipient1',
            email='recipient1@example.com',
            password='testpass123',
            user_type='mp'
        )
        
        self.recipient2 = User.objects.create_user(
            username='recipient2',
            email='recipient2@example.com',
            password='testpass123',
            user_type='information_officer'
        )
        
        next_run_time = timezone.now() + timedelta(days=7)
        
        self.scheduled_report = ScheduledReport.objects.create(
            name='Weekly Constituency Update',
            report_type='constituents',
            frequency='weekly',
            parameters={
                'include_new_registrations': True,
                'include_activity_summary': True,
                'geographic_breakdown': True
            },
            next_run=next_run_time,
            created_by=self.creator
        )
        
        # Add recipients
        self.scheduled_report.recipients.add(self.recipient1, self.recipient2)
    
    def test_scheduled_report_creation(self):
        """Test scheduled report model creation."""
        self.assertEqual(self.scheduled_report.name, 'Weekly Constituency Update')
        self.assertEqual(self.scheduled_report.report_type, 'constituents')
        self.assertEqual(self.scheduled_report.frequency, 'weekly')
        self.assertEqual(self.scheduled_report.created_by, self.creator)
        self.assertTrue(self.scheduled_report.is_active)
        self.assertIsNone(self.scheduled_report.last_run)
        self.assertIsInstance(self.scheduled_report.id, uuid.UUID)
    
    def test_scheduled_report_str_method(self):
        """Test string representation."""
        expected_str = "Weekly Constituency Update (Weekly)"
        self.assertEqual(str(self.scheduled_report), expected_str)
    
    def test_scheduled_report_recipients(self):
        """Test many-to-many relationship with recipients."""
        recipients = list(self.scheduled_report.recipients.all())
        self.assertEqual(len(recipients), 2)
        self.assertIn(self.recipient1, recipients)
        self.assertIn(self.recipient2, recipients)
        
        # Test adding/removing recipients
        new_recipient = User.objects.create_user(
            username='new_recipient',
            email='new@example.com',
            password='testpass123'
        )
        
        self.scheduled_report.recipients.add(new_recipient)
        self.assertEqual(self.scheduled_report.recipients.count(), 3)
        
        self.scheduled_report.recipients.remove(self.recipient1)
        self.assertEqual(self.scheduled_report.recipients.count(), 2)
        self.assertNotIn(self.recipient1, self.scheduled_report.recipients.all())
    
    def test_frequency_choices(self):
        """Test different frequency options."""
        frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        
        for freq in frequencies:
            next_run = timezone.now() + timedelta(days=1)
            report = ScheduledReport.objects.create(
                name=f'{freq.title()} Report',
                report_type='referrals',
                frequency=freq,
                next_run=next_run,
                created_by=self.creator
            )
            self.assertEqual(report.frequency, freq)
    
    def test_scheduled_report_parameters_json(self):
        """Test JSON field for scheduled report parameters."""
        complex_params = {
            'schedule_config': {
                'day_of_week': 1,  # Monday
                'time_of_day': '09:00',
                'timezone': 'Asia/Manila'
            },
            'content_config': {
                'sections': ['summary', 'metrics', 'trends', 'recommendations'],
                'detail_level': 'executive',
                'include_charts': True,
                'include_raw_data': False
            },
            'delivery_config': {
                'email_template': 'executive_report',
                'attachment_format': 'pdf',
                'inline_summary': True,
                'priority': 'normal'
            },
            'data_filters': {
                'date_range': 'auto',
                'exclude_draft_items': True,
                'minimum_activity_threshold': 5
            }
        }
        
        self.scheduled_report.parameters = complex_params
        self.scheduled_report.save()
        
        self.scheduled_report.refresh_from_db()
        self.assertEqual(self.scheduled_report.parameters, complex_params)
        self.assertEqual(self.scheduled_report.parameters['schedule_config']['day_of_week'], 1)
    
    def test_last_run_tracking(self):
        """Test last run timestamp tracking."""
        self.assertIsNone(self.scheduled_report.last_run)
        
        # Simulate report execution
        run_time = timezone.now()
        self.scheduled_report.last_run = run_time
        self.scheduled_report.save()
        
        self.scheduled_report.refresh_from_db()
        self.assertEqual(self.scheduled_report.last_run, run_time)
    
    def test_active_inactive_reports(self):
        """Test active/inactive scheduled reports."""
        # Create inactive report
        inactive_report = ScheduledReport.objects.create(
            name='Inactive Report',
            report_type='services',
            frequency='monthly',
            next_run=timezone.now() + timedelta(days=30),
            created_by=self.creator,
            is_active=False
        )
        
        self.assertTrue(self.scheduled_report.is_active)
        self.assertFalse(inactive_report.is_active)
        
        # Test filtering active reports
        active_reports = ScheduledReport.objects.filter(is_active=True)
        inactive_reports = ScheduledReport.objects.filter(is_active=False)
        
        self.assertIn(self.scheduled_report, active_reports)
        self.assertIn(inactive_report, inactive_reports)
    
    def test_scheduled_report_ordering(self):
        """Test ordering by next_run."""
        # Create report with earlier next_run
        earlier_report = ScheduledReport.objects.create(
            name='Earlier Report',
            report_type='chapters',
            frequency='daily',
            next_run=timezone.now() + timedelta(days=1),
            created_by=self.creator
        )
        
        reports = list(ScheduledReport.objects.all())
        self.assertEqual(reports[0], earlier_report)  # Earlier next_run first
        self.assertEqual(reports[1], self.scheduled_report)


class DashboardModelTest(TestCase):
    """Test cases for Dashboard model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='dashboard_user',
            email='dashboard@example.com',
            password='testpass123',
            user_type='coordinator'
        )
        
        self.dashboard = Dashboard.objects.create(
            name='Executive Overview',
            dashboard_type='executive',
            is_public=False,
            created_by=self.user,
            config={
                'layout': 'grid',
                'columns': 12,
                'theme': 'light',
                'auto_refresh': True,
                'refresh_interval': 300
            }
        )
    
    def test_dashboard_creation(self):
        """Test dashboard model creation."""
        self.assertEqual(self.dashboard.name, 'Executive Overview')
        self.assertEqual(self.dashboard.dashboard_type, 'executive')
        self.assertEqual(self.dashboard.created_by, self.user)
        self.assertFalse(self.dashboard.is_public)
        self.assertIsInstance(self.dashboard.id, uuid.UUID)
    
    def test_dashboard_str_method(self):
        """Test string representation."""
        expected_str = "Executive Overview (Executive Dashboard)"
        self.assertEqual(str(self.dashboard), expected_str)
    
    def test_dashboard_types(self):
        """Test different dashboard types."""
        dashboard_types = ['executive', 'operational', 'chapter', 'custom']
        
        for dash_type in dashboard_types:
            dashboard = Dashboard.objects.create(
                name=f'{dash_type.title()} Dashboard',
                dashboard_type=dash_type,
                created_by=self.user
            )
            self.assertEqual(dashboard.dashboard_type, dash_type)
    
    def test_dashboard_config_json(self):
        """Test JSON field for dashboard configuration."""
        complex_config = {
            'layout': {
                'type': 'responsive_grid',
                'breakpoints': {
                    'lg': 1200,
                    'md': 996,
                    'sm': 768,
                    'xs': 480
                },
                'columns': {'lg': 12, 'md': 10, 'sm': 6, 'xs': 4}
            },
            'styling': {
                'theme': 'dark',
                'primary_color': '#1e3a8a',
                'secondary_color': '#64748b',
                'font_family': 'Inter, sans-serif'
            },
            'behavior': {
                'auto_refresh': True,
                'refresh_interval': 60,
                'lazy_load_widgets': True,
                'enable_exports': True
            },
            'permissions': {
                'edit_allowed': ['coordinator', 'mp'],
                'view_allowed': ['all_authenticated'],
                'share_allowed': True
            }
        }
        
        self.dashboard.config = complex_config
        self.dashboard.save()
        
        self.dashboard.refresh_from_db()
        self.assertEqual(self.dashboard.config, complex_config)
        self.assertEqual(self.dashboard.config['layout']['columns']['lg'], 12)
    
    def test_public_private_dashboards(self):
        """Test public and private dashboard functionality."""
        public_dashboard = Dashboard.objects.create(
            name='Public Health Dashboard',
            dashboard_type='operational',
            is_public=True,
            created_by=self.user
        )
        
        self.assertTrue(public_dashboard.is_public)
        self.assertFalse(self.dashboard.is_public)
        
        # Test filtering
        public_dashboards = Dashboard.objects.filter(is_public=True)
        private_dashboards = Dashboard.objects.filter(is_public=False)
        
        self.assertIn(public_dashboard, public_dashboards)
        self.assertIn(self.dashboard, private_dashboards)
    
    def test_dashboard_ordering(self):
        """Test dashboard ordering by name."""
        zebra_dashboard = Dashboard.objects.create(
            name='Zebra Dashboard',
            dashboard_type='custom',
            created_by=self.user
        )
        
        alpha_dashboard = Dashboard.objects.create(
            name='Alpha Dashboard',
            dashboard_type='chapter',
            created_by=self.user
        )
        
        dashboards = list(Dashboard.objects.all())
        self.assertEqual(dashboards[0], alpha_dashboard)
        self.assertEqual(dashboards[1], self.dashboard)  # Executive Overview
        self.assertEqual(dashboards[2], zebra_dashboard)


class DashboardWidgetModelTest(TestCase):
    """Test cases for DashboardWidget model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='widget_user',
            email='widget@example.com',
            password='testpass123'
        )
        
        self.dashboard = Dashboard.objects.create(
            name='Test Dashboard',
            dashboard_type='operational',
            created_by=self.user
        )
        
        self.widget = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            title='Referrals by Status',
            widget_type='chart',
            chart_type='pie',
            data_source='referrals',
            filters={
                'date_range': 'last_30_days',
                'status': ['processing', 'completed', 'cancelled']
            },
            position=1,
            width=6,
            height=400,
            config={
                'show_legend': True,
                'show_labels': True,
                'color_scheme': 'blue',
                'animation': 'smooth'
            }
        )
    
    def test_widget_creation(self):
        """Test widget model creation."""
        self.assertEqual(self.widget.dashboard, self.dashboard)
        self.assertEqual(self.widget.title, 'Referrals by Status')
        self.assertEqual(self.widget.widget_type, 'chart')
        self.assertEqual(self.widget.chart_type, 'pie')
        self.assertEqual(self.widget.data_source, 'referrals')
        self.assertEqual(self.widget.position, 1)
        self.assertEqual(self.widget.width, 6)
        self.assertEqual(self.widget.height, 400)
        self.assertIsInstance(self.widget.id, uuid.UUID)
    
    def test_widget_str_method(self):
        """Test string representation."""
        expected_str = "Referrals by Status (Chart)"
        self.assertEqual(str(self.widget), expected_str)
    
    def test_widget_types(self):
        """Test different widget types."""
        widget_types = ['chart', 'metric', 'table', 'map', 'timeline']
        
        for widget_type in widget_types:
            widget = DashboardWidget.objects.create(
                dashboard=self.dashboard,
                title=f'Test {widget_type}',
                widget_type=widget_type,
                data_source='constituents'
            )
            self.assertEqual(widget.widget_type, widget_type)
    
    def test_chart_types(self):
        """Test different chart types."""
        chart_types = ['bar', 'line', 'pie', 'doughnut', 'area']
        
        for chart_type in chart_types:
            widget = DashboardWidget.objects.create(
                dashboard=self.dashboard,
                title=f'Test {chart_type} Chart',
                widget_type='chart',
                chart_type=chart_type,
                data_source='services'
            )
            self.assertEqual(widget.chart_type, chart_type)
    
    def test_widget_filters_json(self):
        """Test JSON field for widget filters."""
        complex_filters = {
            'time_range': {
                'type': 'relative',
                'value': 90,
                'unit': 'days'
            },
            'geographic': {
                'municipalities': ['Cotabato City'],
                'exclude_inactive': True
            },
            'categorical': {
                'service_types': ['healthcare', 'education'],
                'priority_levels': ['high', 'urgent']
            },
            'numeric': {
                'age_range': {'min': 18, 'max': 65},
                'amount_range': {'min': 1000, 'max': 100000}
            },
            'boolean': {
                'is_completed': True,
                'has_documents': None
            }
        }
        
        self.widget.filters = complex_filters
        self.widget.save()
        
        self.widget.refresh_from_db()
        self.assertEqual(self.widget.filters, complex_filters)
        self.assertEqual(self.widget.filters['time_range']['value'], 90)
    
    def test_widget_config_json(self):
        """Test JSON field for widget configuration."""
        complex_config = {
            'chart_options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'display': True,
                        'position': 'bottom'
                    },
                    'tooltip': {
                        'enabled': True,
                        'mode': 'nearest'
                    }
                }
            },
            'colors': {
                'primary': '#3b82f6',
                'secondary': '#64748b',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444'
            },
            'data_refresh': {
                'enabled': True,
                'interval': 30,
                'show_last_updated': True
            },
            'interactions': {
                'click_action': 'drill_down',
                'hover_effects': True,
                'export_enabled': True
            }
        }
        
        self.widget.config = complex_config
        self.widget.save()
        
        self.widget.refresh_from_db()
        self.assertEqual(self.widget.config, complex_config)
        self.assertEqual(self.widget.config['chart_options']['plugins']['legend']['position'], 'bottom')
    
    def test_widget_positioning(self):
        """Test widget positioning and ordering."""
        # Create widgets with different positions
        widget2 = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            title='Second Widget',
            widget_type='metric',
            data_source='constituents',
            position=0
        )
        
        widget3 = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            title='Third Widget',
            widget_type='table',
            data_source='chapters',
            position=2
        )
        
        widgets = list(DashboardWidget.objects.all())
        self.assertEqual(widgets[0], widget2)  # position 0
        self.assertEqual(widgets[1], self.widget)  # position 1
        self.assertEqual(widgets[2], widget3)  # position 2
    
    def test_widget_grid_system(self):
        """Test widget grid system (width/height)."""
        # Test different widths (1-12 grid system)
        widths = [3, 6, 9, 12]
        for width in widths:
            widget = DashboardWidget.objects.create(
                dashboard=self.dashboard,
                title=f'Widget Width {width}',
                widget_type='chart',
                data_source='referrals',
                width=width
            )
            self.assertEqual(widget.width, width)
        
        # Test different heights
        heights = [200, 300, 400, 600]
        for height in heights:
            widget = DashboardWidget.objects.create(
                dashboard=self.dashboard,
                title=f'Widget Height {height}',
                widget_type='metric',
                data_source='services',
                height=height
            )
            self.assertEqual(widget.height, height)
    
    def test_dashboard_widget_relationship(self):
        """Test relationship between dashboard and widgets."""
        # Create another widget for the same dashboard
        widget2 = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            title='Another Widget',
            widget_type='table',
            data_source='constituents'
        )
        
        # Test reverse relationship
        dashboard_widgets = list(self.dashboard.widgets.all())
        self.assertEqual(len(dashboard_widgets), 2)
        self.assertIn(self.widget, dashboard_widgets)
        self.assertIn(widget2, dashboard_widgets)
        
        # Test cascade deletion
        widget_count_before = DashboardWidget.objects.count()
        self.dashboard.delete()
        widget_count_after = DashboardWidget.objects.count()
        
        # All widgets should be deleted with dashboard
        self.assertEqual(widget_count_after, widget_count_before - 2)