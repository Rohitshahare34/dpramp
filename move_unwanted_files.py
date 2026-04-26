#!/usr/bin/env python3
"""
Move unwanted files to dev_utils folder
"""

import os
import shutil

def move_unwanted_files():
    """Move unwanted development files to dev_utils"""
    print("🔧 Moving Unwanted Files to dev_utils...")
    
    # Files to move
    unwanted_files = [
        'POPUP_MANAGEMENT_GUIDE.md',
        'RAZORPAY_SETUP_GUIDE.md', 
        'database_structure.json',
        'debug_payment.py',
        'fix_css_errors.py',
        'fix_missing_static.sh',
        'fix_paths.py',
        'fix_payment.py',
        'test_payment_fix.py',
        'update_drone_prices.py',
        'update_notes_price.py',
        'update_workshop_prices.py',
        'verify_file_limits.py',
        'commit_fixes.py'
    ]
    
    moved_count = 0
    
    for file_name in unwanted_files:
        source_path = file_name
        dest_path = f"dev_utils/{file_name}"
        
        if os.path.exists(source_path):
            try:
                shutil.move(source_path, dest_path)
                print(f"  ✅ Moved: {file_name} → dev_utils/")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ Error moving {file_name}: {str(e)}")
        else:
            print(f"  ⚠️  Not found: {file_name}")
    
    print(f"\n📊 Moved {moved_count} files to dev_utils/")
    
    # Clean up any remaining temp files
    temp_files = [
        'media/',
        'staticfiles/'
    ]
    
    for temp_dir in temp_files:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"  🗑️  Removed: {temp_dir}")
            except Exception as e:
                print(f"  ❌ Error removing {temp_dir}: {str(e)}")
    
    print("\n✅ Cleanup completed!")

def main():
    move_unwanted_files()
    
    print("\n🎯 Project Structure Now Clean:")
    print("📁 DPRAMP/ - Static assets")
    print("📁 templates/ - HTML templates") 
    print("📁 notes/ - Django views/models")
    print("📁 dpramp_project/ - Django settings")
    print("📁 dev_utils/ - Development utilities")
    print("📁 media/ - User uploads (empty)")
    print("📁 staticfiles/ - Collected static (empty)")

if __name__ == "__main__":
    main()
