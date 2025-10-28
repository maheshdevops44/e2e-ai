#!/usr/bin/env python3
"""
Simple Session Management Utility
Clears browser sessions using only built-in Python modules.
"""

import os
import subprocess
import time
import shutil

def kill_browser_processes():
    """Kill browser processes using taskkill."""
    print("🔪 Killing browser processes...")
    
    # Use taskkill to kill browser processes
    try:
        # Kill Chrome
        subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                      capture_output=True, shell=True)
        print("✅ Attempted to kill Chrome")
    except:
        pass
    
    try:
        # Kill Edge
        subprocess.run(['taskkill', '/f', '/im', 'msedge.exe'], 
                      capture_output=True, shell=True)
        print("✅ Attempted to kill Edge")
    except:
        pass
    
    try:
        # Kill Firefox
        subprocess.run(['taskkill', '/f', '/im', 'firefox.exe'], 
                      capture_output=True, shell=True)
        print("✅ Attempted to kill Firefox")
    except:
        pass
    
    print("🎯 Browser process cleanup attempted")

def clear_chrome_data():
    """Clear Chrome browser data."""
    print("🧹 Clearing Chrome data...")
    
    chrome_paths = [
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Session Storage"),
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Local Storage"),
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies"),
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies-journal")
    ]
    
    cleared_count = 0
    for path in chrome_paths:
        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                cleared_count += 1
                print(f"✅ Cleared Chrome: {os.path.basename(path)}")
        except Exception as e:
            print(f"⚠️ Could not clear Chrome {os.path.basename(path)}: {e}")
    
    return cleared_count

def clear_edge_data():
    """Clear Edge browser data."""
    print("🧹 Clearing Edge data...")
    
    edge_paths = [
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Session Storage"),
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Local Storage"),
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cookies"),
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cookies-journal")
    ]
    
    cleared_count = 0
    for path in edge_paths:
        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                cleared_count += 1
                print(f"✅ Cleared Edge: {os.path.basename(path)}")
        except Exception as e:
            print(f"⚠️ Could not clear Edge {os.path.basename(path)}: {e}")
    
    return cleared_count

def clear_temp_files():
    """Clear temporary files."""
    print("🗑️ Clearing temporary files...")
    
    temp_dir = os.environ.get('TEMP', '')
    if not temp_dir:
        temp_dir = os.path.expanduser("~\\AppData\\Local\\Temp")
    
    cleared_count = 0
    if temp_dir and os.path.exists(temp_dir):
        try:
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                try:
                    # Only delete browser-related temp files
                    if any(browser in item.lower() for browser in ['chrome', 'edge', 'firefox', 'playwright']):
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        cleared_count += 1
                except Exception:
                    continue
        except Exception as e:
            print(f"⚠️ Could not clear temp dir: {e}")
    
    print(f"🗑️ Cleared {cleared_count} temporary files")
    return cleared_count

def wait_for_cleanup():
    """Wait for cleanup to complete."""
    print("⏳ Waiting for cleanup to complete...")
    time.sleep(3)
    print("✅ Cleanup wait completed")

def main():
    """Main session clearing function."""
    print("🚀 SIMPLE SESSION CLEANUP")
    print("=" * 40)
    
    try:
        # Step 1: Kill browser processes
        kill_browser_processes()
        
        # Step 2: Wait a moment
        time.sleep(2)
        
        # Step 3: Clear Chrome data
        chrome_cleared = clear_chrome_data()
        
        # Step 4: Clear Edge data
        edge_cleared = clear_edge_data()
        
        # Step 5: Clear temp files
        temp_cleared = clear_temp_files()
        
        # Step 6: Wait for cleanup
        wait_for_cleanup()
        
        print("\n" + "=" * 40)
        print("🎉 SESSION CLEANUP COMPLETED")
        print("=" * 40)
        print(f"📊 Summary:")
        print(f"   - Chrome data locations cleared: {chrome_cleared}")
        print(f"   - Edge data locations cleared: {edge_cleared}")
        print(f"   - Temporary files cleared: {temp_cleared}")
        print(f"\n💡 You can now run your automation!")
        
    except Exception as e:
        print(f"❌ Session cleanup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Session cleanup successful!")
    else:
        print("\n❌ Session cleanup failed!") 