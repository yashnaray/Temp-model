#!/usr/bin/env python3
"""
Minimal installation script to avoid dependency conflicts
"""
import subprocess
import sys

def install_package(package):
    """Install a single package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install packages one by one"""
    packages = [
        "numpy==1.24.3",
        "opencv-python-headless==4.8.1.78",
        "scikit-image==0.21.0",
        "pillow>=9.5.0",
        "pytest>=7.0.0",
        "requests>=2.28.0"
    ]
    
    print("Installing minimal dependencies...")
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n✅ Successfully installed {success_count}/{len(packages)} packages")
    
    if success_count >= 4:  # At least core packages
        print("✅ Minimum requirements met. You can run basic tests.")
        print("Run: python Test/test_minimal.py")
    else:
        print("❌ Too many packages failed. Check your Python environment.")

if __name__ == "__main__":
    main()