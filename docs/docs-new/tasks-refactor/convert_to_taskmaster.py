#!/usr/bin/env python3
"""
Convert task files from current format to taskmaster-ai MCP format.

Usage:
    # Convert single task
    python3 convert_to_taskmaster.py --input phase-03-madaris/task_026.txt --output task_026_converted.txt

    # Convert single phase (batch mode)
    python3 convert_to_taskmaster.py --batch --input-dir phase-03-madaris --output-dir converted/phase-03-madaris

    # Convert all phases (130 tasks)
    python3 convert_to_taskmaster.py --all --output-dir converted/

    # Dry run (validate without writing)
    python3 convert_to_taskmaster.py --all --dry-run
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime


class ConversionError(Exception):
    """Custom exception for conversion errors."""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class TaskConverter:
    """Converts task files from custom format to taskmaster-ai format."""

    # Priority mapping based on task characteristics
    PRIORITY_KEYWORDS = {
        'high': ['database', 'migration', 'backup', 'rollback', 'role', 'security', 'critical',
                 'risk', 'production', 'data loss', 'authentication', 'authorization'],
        'medium': ['model', 'admin', 'form', 'template', 'api', 'view', 'url', 'endpoint',
                   'validation', 'testing', 'configuration'],
        'low': ['documentation', 'style', 'css', 'ui', 'optimization', 'refactor',
                'cleanup', 'formatting', 'comment'],
    }

    def __init__(self, input_file: str):
        """Initialize converter with input file."""
        self.input_file = Path(input_file)
        self.errors = []
        self.warnings = []

        try:
            self.content = self.input_file.read_text()
        except FileNotFoundError:
            raise ConversionError(f"Input file not found: {input_file}")
        except Exception as e:
            raise ConversionError(f"Error reading file {input_file}: {e}")

        self.parsed = self._parse_current_format()

    def _parse_current_format(self) -> Dict:
        """Parse current task format."""
        task = {}

        # Extract Task ID and Title from first line
        title_match = re.match(r'#\s+Task\s+(\d+[a-z]?):\s+(.+)', self.content)
        if title_match:
            task['id'] = title_match.group(1)
            task['title'] = title_match.group(2).strip()
        else:
            self.errors.append("Could not parse task ID and title from first line")
            task['id'] = 'UNKNOWN'
            task['title'] = 'UNKNOWN'

        # Extract Phase
        phase_match = re.search(r'^## Phase:\s*(.+)$', self.content, re.MULTILINE)
        if phase_match:
            task['phase'] = phase_match.group(1).strip()
        else:
            self.warnings.append("No phase found")
            task['phase'] = None

        # Extract Status
        status_match = re.search(r'^## Status:\s*(.+)$', self.content, re.MULTILINE)
        if status_match:
            status = status_match.group(1).strip()
            if status not in ['pending', 'in_progress', 'done']:
                self.warnings.append(f"Unknown status '{status}', defaulting to 'pending'")
                task['status'] = 'pending'
            else:
                task['status'] = status
        else:
            self.warnings.append("No status found, defaulting to 'pending'")
            task['status'] = 'pending'

        # Extract Dependencies
        deps_section = re.search(
            r'^## Dependencies:\s*\n(.+?)(?=\n## |\nEOF|\Z)',
            self.content,
            re.MULTILINE | re.DOTALL
        )
        task['dependencies'] = self._parse_dependencies(deps_section.group(1) if deps_section else '')

        # Extract Description
        desc_match = re.search(r'^## Description:\s*\n(.+?)(?=\n## )', self.content, re.MULTILINE | re.DOTALL)
        task['description'] = desc_match.group(1).strip() if desc_match else ''

        # Extract Acceptance Criteria
        criteria_match = re.search(
            r'^## Acceptance Criteria:\s*\n(.+?)(?=\n## )',
            self.content,
            re.MULTILINE | re.DOTALL
        )
        task['acceptance_criteria'] = self._parse_criteria(criteria_match.group(1) if criteria_match else '')

        # Extract Steps
        steps_match = re.search(r'^## Steps:\s*\n(.+?)(?=\n## )', self.content, re.MULTILINE | re.DOTALL)
        task['steps'] = steps_match.group(1).strip() if steps_match else ''

        # Extract Files Affected
        files_match = re.search(
            r'^## Files Affected:\s*\n(.+?)(?=\n## |\nEOF|\Z)',
            self.content,
            re.MULTILINE | re.DOTALL
        )
        task['files_affected'] = self._parse_files(files_match.group(1) if files_match else '')

        # Extract Notes
        notes_match = re.search(r'^## Notes:\s*\n(.+?)(?=\Z)', self.content, re.MULTILINE | re.DOTALL)
        task['notes'] = notes_match.group(1).strip() if notes_match else ''

        return task

    def _parse_dependencies(self, deps_text: str) -> List[str]:
        """Parse dependencies from text."""
        if 'none' in deps_text.lower() or not deps_text.strip():
            return []

        # Extract task IDs from dependency lines
        task_ids = re.findall(r'task_(\d+)', deps_text, re.IGNORECASE)
        # Also try to extract from "task_XXX.txt" format
        if not task_ids:
            task_ids = re.findall(r'(\d+)', deps_text)

        # Remove duplicates and return as sorted list
        return sorted(list(set(task_ids)))

    def _parse_criteria(self, criteria_text: str) -> List[str]:
        """Parse acceptance criteria checklist."""
        # Extract items from checkbox format: - [ ] or - [x]
        items = re.findall(r'-\s*\[.\]\s*(.+)', criteria_text)
        return [item.strip() for item in items if item.strip()]

    def _parse_files(self, files_text: str) -> List[str]:
        """Parse files affected list."""
        # Extract file paths
        lines = files_text.strip().split('\n')
        files = []
        for line in lines:
            # Remove bullet points and clean up
            cleaned = re.sub(r'^[-*]\s+', '', line).strip()
            if cleaned:
                files.append(cleaned)
        return files

    def _determine_priority(self) -> str:
        """Determine priority based on task content."""
        combined_text = (self.parsed.get('description', '') + ' ' +
                        self.parsed.get('title', '') + ' ' +
                        self.parsed.get('notes', '')).lower()

        # Check for high priority keywords
        for keyword in self.PRIORITY_KEYWORDS.get('high', []):
            if keyword in combined_text:
                return 'high'

        # Check for medium priority keywords
        for keyword in self.PRIORITY_KEYWORDS.get('medium', []):
            if keyword in combined_text:
                return 'medium'

        # Default to medium
        return 'medium'

    def _build_details_section(self) -> str:
        """Build the Details section from parsed components."""
        details = []

        # Start with description
        if self.parsed.get('description'):
            details.append(self.parsed['description'])
            details.append('')

        # Add implementation steps
        if self.parsed.get('steps'):
            details.append('## Implementation Steps:')
            details.append(self.parsed['steps'])
            details.append('')

        # Add acceptance criteria
        if self.parsed.get('acceptance_criteria'):
            details.append('## Acceptance Criteria:')
            for criterion in self.parsed['acceptance_criteria']:
                details.append(f'- {criterion}')
            details.append('')

        # Add files modified
        if self.parsed.get('files_affected'):
            details.append('## Files Modified:')
            for file in self.parsed['files_affected']:
                details.append(f'- `{file}`')
            details.append('')

        # Add notes
        if self.parsed.get('notes'):
            details.append('## Important Notes:')
            # Clean up the notes section
            notes = self.parsed['notes']
            # If notes are in bullet format, keep them; otherwise, add as is
            if not notes.startswith('-'):
                details.append(notes)
            else:
                details.append(notes)

        return '\n'.join(details)

    def _build_test_strategy(self) -> str:
        """Build Test Strategy section (inferred from task type)."""
        task_type = self.parsed.get('title', '').lower()
        description = self.parsed.get('description', '').lower()
        combined_text = f"{task_type} {description}"

        strategies = {
            'backup': [
                'Verify backup file exists and has reasonable size',
                'Restore on test database to verify integrity',
                'Confirm all tables present in restored database',
                'Compare row counts with original database',
            ],
            'migration': [
                'Verify migration file syntax with `python manage.py sqlmigrate`',
                'Test forward migration on staging database',
                'Test reverse migration to ensure rollback works',
                'Verify no data loss during migration',
                'Run full test suite to catch regressions',
            ],
            'template': [
                'Load page in browser and verify visual changes',
                'Test responsive design on mobile and desktop',
                'Verify no console errors in browser DevTools',
                'Test form submissions if applicable',
            ],
            'model': [
                'Run migrations and verify schema changes',
                'Create test instances to verify new fields',
                'Test admin interface with new fields',
                'Verify backward compatibility with existing data',
            ],
            'role': [
                'Verify new roles appear in Django admin dropdown',
                'Create test users with new roles',
                'Verify permissions work correctly',
                'Test role-based access control',
            ],
            'app': [
                'Verify app appears in INSTALLED_APPS',
                'Run migrations successfully',
                'Import app models without errors',
                'Verify app shows in Django admin',
            ],
            'api': [
                'Test all API endpoints with curl or Postman',
                'Verify authentication and authorization',
                'Test error responses (400, 401, 403, 404, 500)',
                'Verify JSON response format matches spec',
                'Test pagination if applicable',
            ],
            'form': [
                'Test form validation with valid data',
                'Test form validation with invalid data',
                'Verify error messages display correctly',
                'Test form submission and data persistence',
                'Test CSRF protection',
            ],
            'admin': [
                'Login to Django admin as superuser',
                'Verify models appear in admin interface',
                'Test create, read, update, delete operations',
                'Verify list display, filters, and search work',
            ],
            'view': [
                'Access view URL and verify HTTP 200 response',
                'Test with different user permissions',
                'Verify context data passed to template',
                'Test any query parameters or filters',
            ],
            'plan': [
                'Review planning documentation',
                'Verify all risks identified',
                'Confirm rollback procedures documented',
                'Ensure dependencies are mapped',
            ],
            'test': [
                'Run test suite with `python manage.py test`',
                'Verify test coverage meets requirements',
                'Check for any failing tests',
                'Verify test assertions are correct',
            ],
        }

        # Find matching strategy (check for multiple keywords)
        matched_strategies = []
        for key, steps in strategies.items():
            if key in combined_text:
                matched_strategies.extend(steps)

        if matched_strategies:
            # Remove duplicates while preserving order
            seen = set()
            unique_steps = []
            for step in matched_strategies:
                if step not in seen:
                    seen.add(step)
                    unique_steps.append(step)
            return '\n'.join([f'{i+1}. {step}' for i, step in enumerate(unique_steps)])

        # Default generic strategy
        return '\n'.join([
            '1. Verify all acceptance criteria are met',
            '2. Test the implemented functionality',
            '3. Verify no regressions in related features',
            '4. Confirm all files were properly modified',
        ])

    def convert(self) -> str:
        """Convert to taskmaster-ai format."""
        output_lines = []

        # Header fields
        output_lines.append(f"# Task ID: {self.parsed['id']}")
        output_lines.append(f"# Title: {self.parsed['title']}")
        output_lines.append(f"# Status: {self.parsed['status']}")

        # Dependencies
        deps = self.parsed.get('dependencies', [])
        deps_str = ', '.join(deps) if deps else 'none'
        output_lines.append(f"# Dependencies: {deps_str}")

        # Priority
        priority = self._determine_priority()
        output_lines.append(f"# Priority: {priority}")

        # Description (brief)
        description = self.parsed.get('description', '').split('\n')[0][:150]
        output_lines.append(f"# Description: {description}")

        output_lines.append('')

        # Details section
        output_lines.append('# Details:')
        output_lines.append(self._build_details_section())

        output_lines.append('')

        # Test Strategy section
        output_lines.append('# Test Strategy:')
        output_lines.append(self._build_test_strategy())

        return '\n'.join(output_lines)

    def validate(self) -> bool:
        """Validate the converted output."""
        converted = self.convert()

        # Check for required fields
        required_fields = ['# Task ID:', '# Title:', '# Status:', '# Dependencies:', '# Priority:']
        for field in required_fields:
            if field not in converted:
                self.errors.append(f"Missing required field: {field}")

        # Check for required sections
        required_sections = ['# Details:', '# Test Strategy:']
        for section in required_sections:
            if section not in converted:
                self.errors.append(f"Missing required section: {section}")

        # Check that task ID is valid
        if self.parsed['id'] == 'UNKNOWN':
            self.errors.append("Task ID could not be parsed")

        # Warn if no acceptance criteria
        if not self.parsed.get('acceptance_criteria'):
            self.warnings.append("No acceptance criteria found")

        # Warn if no steps
        if not self.parsed.get('steps'):
            self.warnings.append("No implementation steps found")

        return len(self.errors) == 0

    def save(self, output_file: str, dry_run: bool = False):
        """Save converted task to file."""
        converted = self.convert()

        if dry_run:
            print(f"[DRY RUN] Would convert: {self.input_file} → {output_file}")
            if self.warnings:
                for warning in self.warnings:
                    print(f"  ⚠ Warning: {warning}")
            return

        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(converted)
            print(f"✓ Converted: {self.input_file.name} → {output_file}")
            if self.warnings:
                for warning in self.warnings:
                    print(f"  ⚠ {warning}")
        except Exception as e:
            raise ConversionError(f"Error saving file {output_file}: {e}")


def batch_convert(input_dir: str, output_dir: str, dry_run: bool = False):
    """Convert all task files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    task_files = sorted(input_path.glob('task_*.txt'))

    if not task_files:
        print(f"✗ No task files found in {input_dir}")
        return 0, 0

    print(f"\n{'='*60}")
    print(f"Converting phase: {input_path.name}")
    print(f"Found {len(task_files)} task files...")
    print(f"{'='*60}\n")

    success_count = 0
    error_count = 0

    for i, task_file in enumerate(task_files, 1):
        try:
            print(f"[{i}/{len(task_files)}] ", end="")
            converter = TaskConverter(str(task_file))

            # Validate before converting
            if not converter.validate():
                print(f"✗ Validation failed for {task_file.name}")
                for error in converter.errors:
                    print(f"    ERROR: {error}")
                error_count += 1
                continue

            output_file = output_path / task_file.name
            converter.save(str(output_file), dry_run=dry_run)
            success_count += 1

        except ConversionError as e:
            print(f"✗ Conversion error for {task_file.name}: {e}")
            error_count += 1
        except Exception as e:
            print(f"✗ Unexpected error for {task_file.name}: {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Phase conversion complete!")
    print(f"  ✓ Success: {success_count}")
    print(f"  ✗ Errors:  {error_count}")
    print(f"{'='*60}\n")

    return success_count, error_count


def convert_all_phases(base_dir: str, output_dir: str, dry_run: bool = False):
    """Convert all task files in all phase directories."""
    base_path = Path(base_dir)
    output_path = Path(output_dir)

    # Find all phase directories
    phase_dirs = sorted([d for d in base_path.iterdir() if d.is_dir() and d.name.startswith('phase-')])

    if not phase_dirs:
        print(f"✗ No phase directories found in {base_dir}")
        return

    total_success = 0
    total_errors = 0
    phase_results = []

    start_time = datetime.now()

    print(f"\n{'#'*60}")
    print(f"# CONVERTING ALL PHASES")
    print(f"# Base directory: {base_dir}")
    print(f"# Output directory: {output_dir}")
    print(f"# Found {len(phase_dirs)} phases")
    print(f"# Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'#'*60}\n")

    for phase_dir in phase_dirs:
        phase_output_dir = output_path / phase_dir.name
        success, errors = batch_convert(str(phase_dir), str(phase_output_dir), dry_run=dry_run)
        total_success += success
        total_errors += errors
        phase_results.append({
            'phase': phase_dir.name,
            'success': success,
            'errors': errors
        })

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Print summary
    print(f"\n{'#'*60}")
    print(f"# CONVERSION SUMMARY")
    print(f"{'#'*60}\n")

    print(f"Phase Results:")
    for result in phase_results:
        status_icon = "✓" if result['errors'] == 0 else "⚠"
        print(f"  {status_icon} {result['phase']}: {result['success']} succeeded, {result['errors']} failed")

    print(f"\n{'='*60}")
    print(f"Total Statistics:")
    print(f"  Total tasks processed: {total_success + total_errors}")
    print(f"  ✓ Successful conversions: {total_success}")
    print(f"  ✗ Failed conversions: {total_errors}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Average: {duration/(total_success + total_errors):.2f} seconds per task")
    print(f"{'='*60}\n")

    if not dry_run:
        print(f"✓ All converted files saved to: {output_dir}\n")
    else:
        print(f"[DRY RUN] No files were written\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert task files to taskmaster-ai MCP format',
        epilog='''
Examples:
  # Convert single task
  %(prog)s --input phase-03-madaris/task_026.txt --output task_026_converted.txt

  # Convert single phase
  %(prog)s --batch --input-dir phase-03-madaris --output-dir converted/phase-03-madaris

  # Convert all phases (130 tasks)
  %(prog)s --all --output-dir converted/

  # Dry run (validate without writing)
  %(prog)s --all --dry-run
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Single file conversion
    parser.add_argument('--input', help='Single task file to convert')
    parser.add_argument('--output', help='Output file path for single conversion')

    # Batch conversion
    parser.add_argument('--batch', action='store_true',
                        help='Batch convert all tasks in a directory')
    parser.add_argument('--input-dir', help='Input directory for batch conversion')
    parser.add_argument('--output-dir', help='Output directory for conversions')

    # Convert all phases
    parser.add_argument('--all', action='store_true',
                        help='Convert all tasks in all phase directories')

    # Options
    parser.add_argument('--dry-run', action='store_true',
                        help='Validate tasks without writing output files')
    parser.add_argument('--validate-only', action='store_true',
                        help='Only validate task format, don\'t convert')

    args = parser.parse_args()

    try:
        # Convert all phases
        if args.all:
            if not args.output_dir:
                print("✗ Error: --output-dir is required with --all")
                parser.print_help()
                sys.exit(1)

            # Use current directory as base
            base_dir = Path.cwd()
            convert_all_phases(str(base_dir), args.output_dir, dry_run=args.dry_run)

        # Batch convert single phase
        elif args.batch:
            if not args.input_dir or not args.output_dir:
                print("✗ Error: Both --input-dir and --output-dir are required with --batch")
                parser.print_help()
                sys.exit(1)

            batch_convert(args.input_dir, args.output_dir, dry_run=args.dry_run)

        # Convert single file
        elif args.input:
            if not args.output and not args.validate_only:
                print("✗ Error: --output is required for single file conversion")
                parser.print_help()
                sys.exit(1)

            converter = TaskConverter(args.input)

            # Validate
            is_valid = converter.validate()

            if args.validate_only:
                print(f"\nValidating: {args.input}")
                if is_valid:
                    print("✓ Task file is valid")
                else:
                    print("✗ Task file has errors:")
                    for error in converter.errors:
                        print(f"  - {error}")

                if converter.warnings:
                    print("\nWarnings:")
                    for warning in converter.warnings:
                        print(f"  - {warning}")

                sys.exit(0 if is_valid else 1)

            # Convert
            if not is_valid:
                print(f"✗ Validation failed for {args.input}")
                for error in converter.errors:
                    print(f"  ERROR: {error}")
                sys.exit(1)

            converter.save(args.output, dry_run=args.dry_run)

            if not args.dry_run:
                print(f"\n✓ Conversion complete!")
                print(f"  Input:  {args.input}")
                print(f"  Output: {args.output}")

        else:
            parser.print_help()

    except ConversionError as e:
        print(f"\n✗ Conversion error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
