# verify_installation.py
# Script to verify all required packages are installed correctly

import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed and can be imported."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"[OK] {package_name}")
        return True
    except ImportError as e:
        print(f"[MISSING] {package_name}: {e}")
        return False

def main():
    """Verify all required packages."""
    print("=" * 70)
    print("Verifying Package Installation")
    print("=" * 70)
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # Core packages
    print("Core Packages:")
    all_ok &= check_package("kesslergame", "kesslergame")
    all_ok &= check_package("numpy", "numpy")
    all_ok &= check_package("scikit-fuzzy", "skfuzzy")
    print()
    
    # Check versions
    print("Package Versions:")
    try:
        import numpy
        print(f"  numpy: {numpy.__version__}")
    except:
        pass
    
    try:
        import skfuzzy
        print(f"  scikit-fuzzy: installed")
    except:
        pass
    
    try:
        import kesslergame
        version = getattr(kesslergame, '__version__', 'unknown')
        if version == 'unknown':
            # Try to get version from package metadata
            try:
                import pkg_resources
                version = pkg_resources.get_distribution('kesslergame').version
            except:
                pass
        print(f"  kesslergame: {version}")
    except:
        pass
    print()
    
    # Test imports used in our code
    print("Testing Project Imports:")
    try:
        from kesslergame import KesslerController, Scenario, KesslerGame, GraphicsType
        print("[OK] kesslergame imports")
    except Exception as e:
        print(f"[FAILED] kesslergame imports: {e}")
        all_ok = False
    
    try:
        import numpy as np
        print("[OK] numpy import")
    except Exception as e:
        print(f"[FAILED] numpy import: {e}")
        all_ok = False
    
    try:
        import skfuzzy as fuzz
        from skfuzzy import control as ctrl
        print("[OK] scikit-fuzzy imports")
    except Exception as e:
        print(f"[FAILED] scikit-fuzzy imports: {e}")
        all_ok = False
    
    print()
    print("=" * 70)
    if all_ok:
        print("[SUCCESS] All packages installed and working correctly!")
        print("=" * 70)
        return 0
    else:
        print("[ERROR] Some packages are missing or not working correctly.")
        print("  Run: venv\\Scripts\\python.exe -m pip install -r requirements.txt")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

