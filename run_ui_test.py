#!/usr/bin/env python3
"""
Easy test runner for Spoonfed UI
"""

import os
import sys
import subprocess

def main():
    print("=== Spoonfed UI Test Runner ===")
    print()
    
    # Change to src directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, "src")
    
    if not os.path.exists(src_dir):
        print("❌ src directory not found!")
        return 1
    
    os.chdir(src_dir)
    print(f"📁 Working directory: {src_dir}")
    
    # Test options
    print("\nChoose what to test:")
    print("1. Minimal UI Test (recommended)")
    print("2. Original Application with New Styling")
    print("3. Component Debug Test")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Running Minimal UI Test...")
        run_test("simple_ui_test.py")
    elif choice == "2":
        print("\n🚀 Running Updated Main Application...")
        run_test("main_updated.py")
    elif choice == "3":
        print("\n🚀 Running Debug Test...")
        run_test("debug_ui.py", ["--show-window"])
    elif choice == "4":
        print("👋 Goodbye!")
        return 0
    else:
        print("❌ Invalid choice!")
        return 1

def run_test(script_name, args=None):
    """Run a test script"""
    if not os.path.exists(script_name):
        print(f"❌ Script not found: {script_name}")
        return
    
    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)
    
    try:
        print(f"   Command: {' '.join(cmd)}")
        print("   Press Ctrl+C to stop the application")
        print("-" * 50)
        
        result = subprocess.run(cmd, check=False)
        
        print("-" * 50)
        if result.returncode == 0:
            print("✅ Test completed successfully!")
        else:
            print(f"⚠️  Test exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)