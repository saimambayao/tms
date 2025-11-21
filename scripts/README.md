# Scripts Directory

This directory contains utility and helper scripts for the BM Parliament portal.

## Structure

- **`utilities/`** - Python utility scripts for database and system management
- **`windows/`** - PowerShell scripts for Windows development environments
- **`local/`** - Local development helper scripts (bash)

## Utilities Scripts

### Database & Member Management
- **`update_member_status.py`** - Update member status in bulk
- **`update_program_public_status.py`** - Toggle program visibility
- **`execute_unified_interface.py`** - Execute unified interface operations

## Windows Scripts

PowerShell scripts for Windows developers:
- **`install-pyenv-win.ps1`** - Install Python version manager for Windows
- **`local_setup.ps1`** - Initial local environment setup
- **`activate_and_run.ps1`** - Activate virtual environment and run server
- **`run_server.ps1`** - Start Django development server
- **`run_migrations.ps1`** - Run Django database migrations
- **`start_local.ps1`** - Complete local startup script

## Usage

### Python Utilities
```bash
# From project root
cd scripts/utilities
python3 update_member_status.py
```

### Windows PowerShell
```powershell
# From project root
.\scripts\windows\start_local.ps1
```

### Local Bash Scripts
```bash
# From project root
./scripts/local/run_local.sh
```
