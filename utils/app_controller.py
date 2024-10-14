import os
import subprocess
import difflib
import glob

def find_installed_apps():
    """Find installed applications on the system by scanning typical application directories."""
    app_paths = glob.glob('/usr/share/applications/*.desktop') + glob.glob('~/.local/share/applications/*.desktop')
    
    apps = {}
    
    for app_path in app_paths:
        with open(app_path, 'r') as file:
            for line in file:
                if line.startswith('Name='):
                    app_name = line.split('=', 1)[1].strip()
                if line.startswith('Exec='):
                    app_exec = line.split('=', 1)[1].strip().split()[0]  # Get the command before any arguments
                    break
            apps[app_name.lower()] = app_exec
    
    return apps

def fuzzy_find_app(apps, command):
    """Find the best matching application based on the user command."""
    matches = difflib.get_close_matches(command.lower(), apps.keys(), n=1, cutoff=0.6)
    if matches:
        return matches[0]
    else:
        return None

def open_application(command):
    """Open an application based on the user voice command."""
    apps = find_installed_apps()
    app_name = fuzzy_find_app(apps, command)
    
    if app_name:
        app_exec = apps[app_name]
        try:
            subprocess.Popen([app_exec])
            return app_name  # Return the application name
        except Exception as e:
            print(f"Failed to launch {app_name}: {str(e)}")
            return None
    else:
        print(f"Application '{command}' not recognized.")
        return None

def close_application(app_name):
    """Close an application by name using 'pkill'."""
    if not app_name:
        print("No application name provided for closing.")
        return
    
    # Fuzzy find the application name if necessary
    apps = find_installed_apps()
    app_name = fuzzy_find_app(apps, app_name)
    
    if app_name:
        try:
            os.system(f"pkill {apps[app_name]}")
            print(f"Closed {app_name}")
        except Exception as e:
            print(f"Failed to close {app_name}: {str(e)}")
    else:
        print(f"Application '{app_name}' not recognized or not running.")



