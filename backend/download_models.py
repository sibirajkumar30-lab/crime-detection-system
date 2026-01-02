"""Download deep learning models for face recognition.

Run this script to download pre-trained AI models:
- Face Detection: res10_300x300 SSD Caffe model (10MB)
- Face Recognition: OpenFace NN4.small2.v1 (31MB)

Total: ~41MB
"""

import urllib.request
import os
import sys


def download_with_progress(url, filepath):
    """Download file with progress bar."""
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r{os.path.basename(filepath)}: {percent}% ")
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, filepath, reporthook)
    sys.stdout.write("\n")


def main():
    print("=" * 60)
    print(" Downloading Deep Learning Face Recognition Models")
    print("=" * 60)
    print()
    
    # Create models directory
    model_dir = 'models'
    os.makedirs(model_dir, exist_ok=True)
    print(f"✓ Models directory: {os.path.abspath(model_dir)}\n")
    
    # Download face detection prototxt
    print("1/3 Downloading face detection prototxt...")
    prototxt_path = os.path.join(model_dir, 'deploy.prototxt')
    if os.path.exists(prototxt_path):
        print("   Already exists, skipping.")
    else:
        url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
        try:
            download_with_progress(url, prototxt_path)
            print("   ✓ Downloaded successfully!")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return
    
    # Download face detection model
    print("\n2/3 Downloading face detection model (10MB)...")
    detector_path = os.path.join(model_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
    if os.path.exists(detector_path):
        print("   Already exists, skipping.")
    else:
        url = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
        try:
            download_with_progress(url, detector_path)
            print("   ✓ Downloaded successfully!")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return
    
    # Download face recognition model
    print("\n3/3 Downloading face recognition model (31MB)...")
    recognizer_path = os.path.join(model_dir, 'openface_nn4.small2.v1.t7')
    if os.path.exists(recognizer_path):
        print("   Already exists, skipping.")
    else:
        # Try first URL
        url = "https://storage.cmusatyalab.org/openface-models/nn4.small2.v1.t7"
        try:
            download_with_progress(url, recognizer_path)
            print("   ✓ Downloaded successfully!")
        except Exception as e:
            print(f"   ✗ Failed from first source: {e}")
            print("   Trying alternative source...")
            # Try alternative URL
            url = "https://github.com/cmusatyalab/openface/raw/master/models/openface/nn4.small2.v1.t7"
            try:
                download_with_progress(url, recognizer_path)
                print("   ✓ Downloaded successfully!")
            except Exception as e2:
                print(f"   ✗ Failed: {e2}")
                print("\n   Manual download required:")
                print(f"   Download from: {url}")
                print(f"   Save to: {os.path.abspath(recognizer_path)}")
                return
    
    print("\n" + "=" * 60)
    print(" ✓ ALL MODELS DOWNLOADED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart the backend server:")
    print("   cd backend")
    print("   python run.py")
    print()
    print("2. You'll see: '✓ Face recognition model loaded (Deep Learning 128-D embeddings)'")
    print()
    print("3. Test with face detection - it will now use AI!")
    print()


if __name__ == "__main__":
    main()
