"""Install DeepFace for production-grade face recognition.

This script installs DeepFace library which provides:
- 99.65% accuracy with Facenet512
- No compilation required (works on Windows)
- Multiple model options
- Industry-standard face recognition
"""

import subprocess
import sys

def install_deepface():
    """Install DeepFace and required dependencies."""
    
    print("=" * 60)
    print("Installing DeepFace - Production Face Recognition")
    print("=" * 60)
    print()
    
    packages = [
        'deepface',      # Main library
        'tf-keras',      # Keras compatibility
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed successfully\n")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}\n")
            return False
    
    print("=" * 60)
    print("✓ DeepFace installation complete!")
    print("=" * 60)
    print()
    print("Available Models:")
    print("  - Facenet512  : 99.65% accuracy (RECOMMENDED)")
    print("  - ArcFace     : 99.41% accuracy")
    print("  - Facenet     : 99.20% accuracy")
    print("  - VGG-Face    : 98.95% accuracy")
    print()
    print("Model will be downloaded automatically on first use (~100MB)")
    print()
    print("Next steps:")
    print("  1. Restart your backend: python run.py")
    print("  2. Add a criminal with photo")
    print("  3. Upload detection - see 99%+ accuracy!")
    print()
    
    return True


if __name__ == '__main__':
    success = install_deepface()
    sys.exit(0 if success else 1)
