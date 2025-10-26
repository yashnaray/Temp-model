#!/usr/bin/env python3
"""
Clean setup script - installs only core dependencies
"""
import subprocess
import sys
import os

def run_command(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Clean installation process"""
    print("🧹 Setting up clean environment...")
    
    # Step 1: Upgrade pip
    print("\n📦 Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Step 2: Install core packages one by one
    core_packages = [
        "numpy==1.26.4",
        "opencv-python-headless==4.10.0.84", 
        "scikit-image==0.22.0",
        "pillow==10.0.0",
        "pytest==7.4.0"
    ]
    
    print("\n📦 Installing core packages...")
    success_count = 0
    for package in core_packages:
        if run_command(f"{sys.executable} -m pip install {package}"):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(core_packages)} packages installed")
    
    # Step 3: Test installation
    if success_count >= 3:
        print("\n🧪 Testing installation...")
        if run_command(f"{sys.executable} Test/test_minimal.py"):
            print("\n🎉 Setup complete! Core functionality working.")
            print("\nNext steps:")
            print("1. Run: python Test/test_minimal.py")
            print("2. Run: python Test/test_vision.py")
        else:
            print("\n⚠️  Setup complete but tests failed. Check dependencies.")
    else:
        print("\n❌ Too many packages failed. Check your Python environment.")

if __name__ == "__main__":
    main()