"""
Management command to analyze and optimize database performance.
"""

from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Analyze and optimize database performance'

    def add_arguments(self, parser):
        parser.add_argument('--analyze', action='store_true', help='Run ANALYZE on all tables')
        parser.add_argument('--vacuum', action='store_true', help='Run VACUUM on all tables (PostgreSQL only)')
        parser.add_argument('--check-indexes', action='store_true', help='Check index usage statistics')
        parser.add_argument('--slow-queries', action='store_true', help='Show slow queries')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database optimization...'))
        
        db_backend = connection.settings_dict['ENGINE']
        is_postgres = 'postgresql' in db_backend

        if options['analyze']:
            self.run_analyze()
        if options['vacuum'] and is_postgres:
            self.run_vacuum()
        if options['check_indexes'] and is_postgres:
            self.check_index_usage()
        if options['slow_queries'] and is_postgres:
            self.show_slow_queries()

        if not any([options['analyze'], options['vacuum'], options['check_indexes'], options['slow_queries']]):
            self.run_analyze()
            if is_postgres:
                self.run_vacuum()
                self.check_index_usage()
                self.show_slow_queries()

        self.stdout.write(self.style.SUCCESS('Database optimization completed!'))

    def run_analyze(self):
        self.stdout.write('Running ANALYZE on all tables...')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT relname FROM pg_stat_user_tables
                ORDER BY relname;
            """)
            tables = cursor.fetchall()
            for (table,) in tables:
                try:
                    cursor.execute(f'ANALYZE {table};')
                    self.stdout.write(f'  ✓ Analyzed {table}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to analyze {table}: {e}'))

    def run_vacuum(self):
        self.stdout.write('Running VACUUM on all tables...')
        connection.ensure_connection()
        connection.set_autocommit(True)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT relname FROM pg_stat_user_tables
                ORDER BY relname;
            """)
            tables = cursor.fetchall()
            for (table,) in tables:
                try:
                    cursor.execute(f'VACUUM ANALYZE {table};')
                    self.stdout.write(f'  ✓ Vacuumed {table}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to vacuum {table}: {e}'))

        connection.set_autocommit(False)

    def check_index_usage(self):
        self.stdout.write('\nChecking index usage statistics...')
        with connection.cursor() as cursor:
            # Unused indexes
            cursor.execute("""
                SELECT 
                    s.schemaname,
                    s.relname,
                    s.indexrelname,
                    s.idx_scan,
                    pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size
                FROM pg_stat_user_indexes s
                JOIN pg_index i ON s.indexrelid = i.indexrelid
                WHERE s.idx_scan = 0
                AND s.indexrelname NOT LIKE 'pg_toast%'
                ORDER BY pg_relation_size(s.indexrelid) DESC;
            """)
            unused = cursor.fetchall()

            if unused:
                self.stdout.write(self.style.WARNING('\nUnused indexes:'))
                for idx in unused:
                    self.stdout.write(f'  - {idx[2]} on {idx[1]} (size: {idx[4]})')
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ All indexes are being used'))

            # Most used indexes
            cursor.execute("""
                SELECT 
                    s.schemaname,
                    s.relname,
                    s.indexrelname,
                    s.idx_scan,
                    pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size
                FROM pg_stat_user_indexes s
                ORDER BY s.idx_scan DESC
                LIMIT 10;
            """)
            top_used = cursor.fetchall()
            self.stdout.write('\nMost used indexes:')
            for idx in top_used:
                self.stdout.write(f'  - {idx[2]} on {idx[1]} (scans: {idx[3]:,}, size: {idx[4]})')

    def show_slow_queries(self):
        self.stdout.write('\nChecking for slow queries...')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                );
            """)
            has_pg_stat_statements = cursor.fetchone()[0]
            if not has_pg_stat_statements:
                self.stdout.write(self.style.WARNING('  pg_stat_statements extension not installed'))
                return

            cursor.execute("""
                SELECT 
                    round(total_exec_time::numeric, 2),
                    calls,
                    round(mean_exec_time::numeric, 2),
                    round(stddev_exec_time::numeric, 2),
                    regexp_replace(query, '\\s+', ' ', 'g')
                FROM pg_stat_statements
                WHERE query NOT LIKE '%pg_stat_statements%'
                AND mean_exec_time > 100
                ORDER BY mean_exec_time DESC
                LIMIT 10;
            """)
            slow_queries = cursor.fetchall()
            if slow_queries:
                self.stdout.write(self.style.WARNING('\nSlow queries (avg > 100ms):'))
                for i, q in enumerate(slow_queries, 1):
                    self.stdout.write(f'\n{i}. Avg: {q[2]}ms, Calls: {q[1]:,}')
                    self.stdout.write(f'   Query: {q[4][:100]}...')
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ No slow queries found'))

            cursor.execute("""
                SELECT 
                    sum(calls),
                    round(sum(total_exec_time)::numeric / 1000, 2),
                    round(avg(mean_exec_time)::numeric, 2)
                FROM pg_stat_statements
                WHERE query NOT LIKE '%pg_stat_statements%';
            """)
            summary = cursor.fetchone()
            self.stdout.write('\nQuery summary:')
            self.stdout.write(f'  - Total queries: {summary[0]:,}')
            self.stdout.write(f'  - Total time: {summary[1]} seconds')
            self.stdout.write(f'  - Avg query time: {summary[2]} ms')
