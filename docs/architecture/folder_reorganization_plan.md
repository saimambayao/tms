# BM Parliament Folder Reorganization Plan

## Overview

This document outlines the reorganization of the BM Parliament project structure to improve maintainability, follow Django best practices, and create a cleaner development experience.

## Current Issues with Existing Structure

1. **Django project in subdirectory**: The main Django code is located in `src/` instead of following the standard practice of having it closer to the root.

2. **Duplicate documentation**: Multiple README files and documentation scattered across various folders without clear organization.

3. **Mixed deployment files**: Deployment configurations are split between the root directory and a deployment folder, making it difficult to manage.

4. **Legacy prototype code**: Old prototype code (`bm parliament_cares_prototype/`) is mixed with production code in the root directory.

5. **Redundant Docker files**: Multiple docker-compose files for different environments are scattered in various locations.

6. **Task management artifacts**: TaskMaster files (`tasks/`) are mixed with core project files, adding clutter.

## Proposed New Structure

```
bm-parliament/
├── src/                              # All Django source code (renamed from src)
│   ├── apps/                         # Django applications
│   │   ├── analytics/
│   │   ├── chapters/
│   │   ├── communications/
│   │   ├── constituents/
│   │   ├── core/
│   │   ├── dashboards/
│   │   ├── documents/
│   │   ├── notifications/
│   │   ├── parliamentary/
│   │   ├── referrals/
│   │   ├── search/
│   │   ├── services/
│   │   ├── staff/
│   │   └── users/
│   ├── config/                       # Django settings and configuration
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── templates/                    # HTML templates
│   ├── static/                       # Static assets (CSS, JS, images)
│   ├── media/                        # User uploads
│   ├── utils/                        # Utility modules
│   ├── manage.py                     
│   └── requirements.txt              
├── deployment/                       # All deployment configurations
│   ├── docker/                       # Docker-related files
│   │   ├── Dockerfile               
│   │   ├── Dockerfile.frontend      
│   │   ├── Dockerfile.production    
│   │   └── docker-compose/          # Environment-specific compose files
│   │       ├── development.yml      
│   │       ├── production.yml       
│   │       ├── test.yml            
│   │       └── coolify.yml         
│   ├── nginx/                        # Nginx configurations
│   │   ├── nginx.conf               
│   │   ├── nginx-dev.conf          
│   │   └── nginx-coolify.conf      
│   ├── scripts/                      # Deployment scripts
│   │   ├── deploy.sh
│   │   ├── backup_database.sh
│   │   └── ssl_monitor.py
│   └── ssl/                          # SSL configurations
├── docs/                             # All documentation
│   ├── architecture/                 # Architecture documentation
│   │   ├── folder_reorganization_plan.md
│   │   ├── technical_architecture.md
│   │   └── system_design.md
│   ├── user/                         # User documentation
│   ├── developer/                    # Developer documentation
│   ├── deployment/                   # Deployment guides
│   └── project-management/           # Project planning docs
├── scripts/                          # Development scripts
│   ├── local/                        # Local development scripts
│   │   ├── run_local.sh            
│   │   └── run_local_windows.sh    
│   └── setup/                        # Setup and data scripts
├── tests/                            # Test configurations
├── archive/                          # Archived/deprecated code
├── .github/                          # GitHub Actions workflows
├── .env.example                      # Environment variable template
├── .gitignore                       
├── CLAUDE.md                         # AI assistant instructions
├── README.md                         # Main project documentation
└── docker-compose.yml                # Default development compose file
```

## Migration Plan

### Phase 1: Rename Core Django Directory
1. Rename `src/` to `src/`
2. Update all path references in Docker files, shell scripts, and configurations

### Phase 2: Consolidate Docker Files
1. Move all Dockerfiles to `deployment/docker/`
2. Move environment-specific docker-compose files to `deployment/docker/docker-compose/`
3. Update all docker build contexts

### Phase 3: Organize Documentation
1. Create subdirectories under `docs/` for different documentation types
2. Move existing documentation to appropriate subdirectories
3. Remove duplicate files

### Phase 4: Clean Up Root Directory
1. Archive old prototype code
2. Move TaskMaster files to documentation or separate repository
3. Move deployment scripts to proper locations

### Phase 5: Update All References
1. Update all Docker files with new paths
2. Update shell scripts with new directory structure
3. Update nginx configurations
4. Update CI/CD pipelines if any

### Phase 6: Testing
1. Test Docker builds
2. Verify local development environment
3. Test deployment scripts
4. Ensure all imports and paths work correctly

## Benefits

1. **Cleaner root directory**: Only essential files at the root level
2. **Better organization**: Clear separation of concerns between code, deployment, and documentation
3. **Industry standard**: Follows Django and Python best practices
4. **Easier navigation**: Logical grouping makes finding files intuitive
5. **Simplified deployment**: All deployment configurations in one place
6. **Better documentation structure**: Organized docs are easier to maintain and navigate

## Files Requiring Updates

### Docker Files
- `Dockerfile`: Update `COPY src/ /app/` to `COPY src/ /app/`
- `deployment/Dockerfile`: Same update as above
- All docker-compose files: Update build contexts from `./src` to `./src`

### Shell Scripts
- `run_local.sh`: Update `DJANGO_PROJECT_PATH` to point to `src/`
- `run_local_windows.sh`: Similar path update
- Deployment scripts: Update all path references

### Configuration Files
- Nginx configs: Verify static and media paths
- Any CI/CD configurations
- CLAUDE.md: Update all directory references

## Rollback Plan

If issues arise during reorganization:

1. Use git to revert to the previous commit:
   ```bash
   git reset --hard HEAD~1
   ```

2. Manually restore directory structure:
   ```bash
   mv src src
   # Move other files back to original locations
   ```

3. Restore original path references in all configuration files

## Implementation Timeline

1. **Documentation Phase** (Current): Document the plan and get approval
2. **Preparation Phase**: Create new directory structure, prepare scripts
3. **Migration Phase**: Execute the reorganization in order of phases
4. **Testing Phase**: Comprehensive testing of all functionality
5. **Cleanup Phase**: Remove old files, update documentation

## Success Criteria

- All Docker containers build and run successfully
- Local development environment works without issues
- All tests pass
- Deployment scripts execute without errors
- Documentation is properly organized and accessible
- No broken imports or path references

## Notes

- This reorganization should be done in a dedicated branch
- Each phase should be committed separately for easy rollback
- Comprehensive testing after each phase is crucial
- Team should be notified before starting the reorganization