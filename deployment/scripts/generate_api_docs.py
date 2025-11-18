#!/usr/bin/env python3

"""
#FahanieCares Platform - API Documentation Generator
Automatically generates comprehensive API documentation from Django REST API
"""

import os
import sys
import json
import datetime
from pathlib import Path
import django
from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.utils.module_loading import import_string


def setup_django():
    """Initialize Django environment."""
    # Add the project directory to the Python path
    project_dir = Path(__file__).parent.parent.parent / 'src'
    sys.path.insert(0, str(project_dir))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    try:
        django.setup()
        return True
    except Exception as e:
        print(f"Failed to setup Django: {e}")
        return False


def extract_url_patterns(urlpatterns, prefix=''):
    """Extract URL patterns recursively."""
    patterns = []
    
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            # Handle include() patterns
            if hasattr(pattern, 'url_patterns'):
                sub_patterns = extract_url_patterns(
                    pattern.url_patterns, 
                    prefix + str(pattern.pattern)
                )
                patterns.extend(sub_patterns)
        elif isinstance(pattern, URLPattern):
            # Handle direct URL patterns
            view_info = extract_view_info(pattern)
            if view_info:
                view_info['url'] = prefix + str(pattern.pattern)
                patterns.append(view_info)
    
    return patterns


def extract_view_info(pattern):
    """Extract information about a view."""
    try:
        callback = pattern.callback
        
        # Get view class or function
        if hasattr(callback, 'view_class'):
            # Class-based view
            view_class = callback.view_class
            view_info = {
                'name': pattern.name or 'unnamed',
                'type': 'class-based',
                'class_name': view_class.__name__,
                'module': view_class.__module__,
                'methods': get_allowed_methods(view_class),
                'docstring': view_class.__doc__ or '',
                'description': extract_description(view_class),
                'authentication': extract_authentication_info(view_class),
                'permissions': extract_permission_info(view_class)
            }
        else:
            # Function-based view
            view_info = {
                'name': pattern.name or 'unnamed',
                'type': 'function-based',
                'function_name': callback.__name__,
                'module': callback.__module__,
                'methods': ['GET'],  # Default assumption
                'docstring': callback.__doc__ or '',
                'description': extract_description(callback),
                'authentication': 'Default',
                'permissions': 'Default'
            }
        
        return view_info
        
    except Exception as e:
        print(f"Error extracting view info for {pattern}: {e}")
        return None


def get_allowed_methods(view_class):
    """Get allowed HTTP methods for a view class."""
    methods = []
    
    # Check for common HTTP method handlers
    http_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    
    for method in http_methods:
        if hasattr(view_class, method) and callable(getattr(view_class, method)):
            methods.append(method.upper())
    
    # Check for REST framework viewsets
    if hasattr(view_class, 'action_map'):
        for action in view_class.action_map.values():
            if action in ['list', 'retrieve']:
                methods.append('GET')
            elif action in ['create']:
                methods.append('POST')
            elif action in ['update', 'partial_update']:
                methods.extend(['PUT', 'PATCH'])
            elif action in ['destroy']:
                methods.append('DELETE')
    
    return list(set(methods)) if methods else ['GET']


def extract_description(view_or_function):
    """Extract description from view docstring."""
    docstring = view_or_function.__doc__ or ''
    
    # Extract first line or paragraph as description
    lines = docstring.strip().split('\n')
    if lines:
        return lines[0].strip().strip('"').strip("'")
    
    return 'No description available'


def extract_authentication_info(view_class):
    """Extract authentication requirements."""
    auth_info = []
    
    if hasattr(view_class, 'authentication_classes'):
        for auth_class in view_class.authentication_classes:
            auth_info.append(auth_class.__name__)
    
    return ', '.join(auth_info) if auth_info else 'Default Django Authentication'


def extract_permission_info(view_class):
    """Extract permission requirements."""
    perm_info = []
    
    if hasattr(view_class, 'permission_classes'):
        for perm_class in view_class.permission_classes:
            perm_info.append(perm_class.__name__)
    
    return ', '.join(perm_info) if perm_info else 'Default Permissions'


def generate_openapi_spec(patterns):
    """Generate OpenAPI 3.0 specification."""
    
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "#FahanieCares API",
            "description": "API documentation for the #FahanieCares platform - Bringing Bangsamoro Public Service Closer to You",
            "version": "1.0.0",
            "contact": {
                "name": "#FahanieCares Development Team",
                "email": "dev@fahaniecares.ph"
            },
            "license": {
                "name": "Proprietary",
                "url": "#"
            }
        },
        "servers": [
            {
                "url": "http://localhost:3000",
                "description": "Development server"
            },
            {
                "url": "https://fahaniecares.ph",
                "description": "Production server"
            }
        ],
        "paths": {},
        "components": {
            "securitySchemes": {
                "SessionAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "sessionid"
                },
                "CSRFToken": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-CSRFToken"
                }
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "description": "Error message"
                        },
                        "detail": {
                            "type": "string",
                            "description": "Detailed error information"
                        }
                    }
                }
            }
        },
        "security": [
            {
                "SessionAuth": [],
                "CSRFToken": []
            }
        ]
    }
    
    # Process patterns into paths
    for pattern in patterns:
        path = clean_url_pattern(pattern['url'])
        
        if path not in openapi_spec['paths']:
            openapi_spec['paths'][path] = {}
        
        for method in pattern['methods']:
            openapi_spec['paths'][path][method.lower()] = {
                "summary": pattern['description'],
                "description": pattern['docstring'] or pattern['description'],
                "tags": [extract_tag_from_module(pattern['module'])],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            },
                            "text/html": {
                                "schema": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Error"
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized"
                    },
                    "403": {
                        "description": "Forbidden"
                    },
                    "404": {
                        "description": "Not found"
                    },
                    "500": {
                        "description": "Internal server error"
                    }
                }
            }
            
            # Add authentication info if required
            if 'login' in pattern['authentication'].lower() or 'staff' in pattern['permissions'].lower():
                openapi_spec['paths'][path][method.lower()]['security'] = [
                    {"SessionAuth": [], "CSRFToken": []}
                ]
    
    return openapi_spec


def clean_url_pattern(url_pattern):
    """Clean URL pattern for OpenAPI."""
    # Remove Django regex patterns and convert to OpenAPI format
    pattern = str(url_pattern)
    
    # Handle common Django patterns
    pattern = pattern.replace('^', '').replace('$', '')
    pattern = pattern.replace('(?P<pk>[^/.]+)', '{id}')
    pattern = pattern.replace('(?P<id>[^/.]+)', '{id}')
    pattern = pattern.replace('(?P<slug>[^/.]+)', '{slug}')
    
    # Ensure starts with /
    if not pattern.startswith('/'):
        pattern = '/' + pattern
    
    # Remove trailing / if not root
    if pattern != '/' and pattern.endswith('/'):
        pattern = pattern.rstrip('/')
    
    return pattern


def extract_tag_from_module(module_name):
    """Extract tag from module name for OpenAPI grouping."""
    if 'apps.' in module_name:
        app_name = module_name.split('.')[1]
        return app_name.title()
    return 'General'


def generate_markdown_docs(patterns):
    """Generate Markdown documentation."""
    
    docs = f"""# #FahanieCares API Documentation

Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document provides comprehensive API documentation for the #FahanieCares platform.

### Base URLs
- Development: `http://localhost:3000`
- Production: `https://fahaniecares.ph`

### Authentication
Most endpoints require Django session authentication with CSRF protection.

## Endpoints

"""
    
    # Group patterns by app/module
    grouped_patterns = {}
    for pattern in patterns:
        tag = extract_tag_from_module(pattern['module'])
        if tag not in grouped_patterns:
            grouped_patterns[tag] = []
        grouped_patterns[tag].append(pattern)
    
    # Generate documentation for each group
    for tag, tag_patterns in sorted(grouped_patterns.items()):
        docs += f"### {tag}\n\n"
        
        for pattern in sorted(tag_patterns, key=lambda x: x['url']):
            docs += f"#### {pattern['name']}\n\n"
            docs += f"**URL:** `{clean_url_pattern(pattern['url'])}`\n\n"
            docs += f"**Methods:** {', '.join(pattern['methods'])}\n\n"
            docs += f"**Description:** {pattern['description']}\n\n"
            
            if pattern['authentication'] != 'Default Django Authentication':
                docs += f"**Authentication:** {pattern['authentication']}\n\n"
            
            if pattern['permissions'] != 'Default Permissions':
                docs += f"**Permissions:** {pattern['permissions']}\n\n"
            
            if pattern['docstring']:
                docs += f"**Details:**\n```\n{pattern['docstring']}\n```\n\n"
            
            docs += "---\n\n"
    
    return docs


def generate_postman_collection(patterns):
    """Generate Postman collection for API testing."""
    
    collection = {
        "info": {
            "name": "#FahanieCares API",
            "description": "API collection for #FahanieCares platform testing",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:3000",
                "type": "string"
            },
            {
                "key": "csrfToken",
                "value": "",
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Group patterns by app
    grouped_patterns = {}
    for pattern in patterns:
        tag = extract_tag_from_module(pattern['module'])
        if tag not in grouped_patterns:
            grouped_patterns[tag] = []
        grouped_patterns[tag].append(pattern)
    
    # Create Postman folders and requests
    for tag, tag_patterns in sorted(grouped_patterns.items()):
        folder = {
            "name": tag,
            "item": []
        }
        
        for pattern in sorted(tag_patterns, key=lambda x: x['url']):
            for method in pattern['methods']:
                request = {
                    "name": f"{pattern['name']} ({method})",
                    "request": {
                        "method": method,
                        "header": [
                            {
                                "key": "X-CSRFToken",
                                "value": "{{csrfToken}}",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": "{{baseUrl}}" + clean_url_pattern(pattern['url']),
                            "host": ["{{baseUrl}}"],
                            "path": clean_url_pattern(pattern['url']).split('/')[1:]
                        }
                    },
                    "response": []
                }
                
                # Add body for POST/PUT/PATCH requests
                if method in ['POST', 'PUT', 'PATCH']:
                    request['request']['body'] = {
                        "mode": "raw",
                        "raw": "{}",
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }
                
                folder['item'].append(request)
        
        collection['item'].append(folder)
    
    return collection


def main():
    """Main function to generate API documentation."""
    print("🚀 Generating #FahanieCares API Documentation...")
    
    # Setup Django
    if not setup_django():
        print("❌ Failed to setup Django environment")
        return 1
    
    try:
        # Import URL configuration
        from config.urls import urlpatterns
        
        print("📋 Extracting URL patterns...")
        patterns = extract_url_patterns(urlpatterns)
        
        print(f"✅ Found {len(patterns)} API endpoints")
        
        # Create docs directory
        docs_dir = Path(__file__).parent.parent / 'docs' / 'api'
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate OpenAPI specification
        print("📝 Generating OpenAPI specification...")
        openapi_spec = generate_openapi_spec(patterns)
        
        with open(docs_dir / 'openapi.json', 'w') as f:
            json.dump(openapi_spec, f, indent=2)
        
        # Generate Markdown documentation
        print("📚 Generating Markdown documentation...")
        markdown_docs = generate_markdown_docs(patterns)
        
        with open(docs_dir / 'api_documentation.md', 'w') as f:
            f.write(markdown_docs)
        
        # Generate Postman collection
        print("📮 Generating Postman collection...")
        postman_collection = generate_postman_collection(patterns)
        
        with open(docs_dir / 'postman_collection.json', 'w') as f:
            json.dump(postman_collection, f, indent=2)
        
        # Generate summary report
        summary = {
            "generated_at": datetime.datetime.now().isoformat(),
            "total_endpoints": len(patterns),
            "apps_documented": len(set(extract_tag_from_module(p['module']) for p in patterns)),
            "files_generated": [
                "openapi.json",
                "api_documentation.md", 
                "postman_collection.json"
            ],
            "endpoints_by_app": {}
        }
        
        # Count endpoints by app
        for pattern in patterns:
            app = extract_tag_from_module(pattern['module'])
            summary["endpoints_by_app"][app] = summary["endpoints_by_app"].get(app, 0) + 1
        
        with open(docs_dir / 'generation_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("✅ API documentation generated successfully!")
        print(f"📁 Documentation files saved to: {docs_dir}")
        print(f"📊 Total endpoints documented: {len(patterns)}")
        print(f"🎯 Apps covered: {len(summary['endpoints_by_app'])}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())