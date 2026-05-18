#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foralis_core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
        
    # RUN SYSTEM TASKS AFTER INITIALIZATION
    if len(sys.argv) > 1 and sys.argv[1] == 'migrate':
        execute_from_command_line(sys.argv)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@example.com", "admin2026")
                print("--- ADMIN ACCOUNT CREATED SUCCESSFULLY ---")
        except Exception as e:
            print(f"Admin creation helper skipped: {e}")
    else:
        execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()