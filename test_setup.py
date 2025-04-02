import os
import sys
import unittest
import torch
from PIL import Image
import numpy as np

class TestSetup(unittest.TestCase):
    def setUp(self):
        self.model_dir = 'models'
        self.required_models = [
            'sam_vit_h_4b8939.pth',
            'control_v11p_sd15_inpaint.pth'
        ]

    def test_python_version(self):
        """Test Python version is 3.8 or higher"""
        major, minor = sys.version_info[:2]
        self.assertGreaterEqual(
            (major, minor), 
            (3, 8), 
            f"Python version 3.8 or higher required. Found: {major}.{minor}"
        )

    def test_cuda_availability(self):
        """Test CUDA availability (warning if not available)"""
        if not torch.cuda.is_available():
            print("\nWarning: CUDA is not available. The application will run on CPU (slower).")
        else:
            print(f"\nCUDA is available: {torch.cuda.get_device_name(0)}")

    def test_required_directories(self):
        """Test required directories exist"""
        required_dirs = ['models', 'uploads', 'static', 'templates']
        for dir_name in required_dirs:
            self.assertTrue(
                os.path.exists(dir_name), 
                f"Required directory missing: {dir_name}"
            )

    def test_model_files(self):
        """Test required model files exist"""
        for model in self.required_models:
            model_path = os.path.join(self.model_dir, model)
            self.assertTrue(
                os.path.exists(model_path), 
                f"Required model missing: {model}"
            )

    def test_disk_space(self):
        """Test available disk space"""
        required_space = 5 * 1024 * 1024 * 1024  # 5GB in bytes
        
        if sys.platform == 'win32':
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p('.'), None, None, ctypes.pointer(free_bytes)
            )
            free_space = free_bytes.value
        else:
            import os
            st = os.statvfs('.')
            free_space = st.f_bavail * st.f_frsize

        self.assertGreaterEqual(
            free_space,
            required_space,
            f"Insufficient disk space. Required: 5GB, Available: {free_space / (1024**3):.1f}GB"
        )

    def test_torch_installation(self):
        """Test PyTorch installation"""
        self.assertTrue(torch.__version__, "PyTorch not properly installed")
        print(f"\nPyTorch version: {torch.__version__}")
        print(f"Torchvision version: {torch.vision.__version__ if hasattr(torch, 'vision') else 'Not found'}")

def main():
    """Run tests with clear output formatting"""
    print("\n=== Virtual Try-On System Setup Test ===\n")
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()