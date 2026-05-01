#!/usr/bin/env python3
"""
Commit static files fix
"""

import subprocess
import sys

def run_command(cmd):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, str(e), ""

def main():
    print("🔧 Committing Static Files Fix...")
    
    # Add files
    success, stdout, stderr = run_command("git add dpramp_project/settings.py move_unwanted_files.py")
    if success:
        print("✅ Files added successfully")
    else:
        print(f"❌ Error adding files: {stderr}")
        return
    
    # Commit changes
    success, stdout, stderr = run_command('git commit -m "Fix static files 404 errors and clean project structure"')
    if success:
        print("✅ Changes committed successfully")
    else:
        print(f"❌ Error committing: {stderr}")
        return
    
    # Push changes
    success, stdout, stderr = run_command("git push origin main")
    if success:
        print("✅ Changes pushed successfully")
    else:
        print(f"❌ Error pushing: {stderr}")
        return
    
    print("🚀 Static files fix deployed!")

if __name__ == "__main__":
    main()
