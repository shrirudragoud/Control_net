import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path to import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_processor import ImageProcessor
from app import app

class TestSetup(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def test_required_directories_exist(self):
        """Test that all required directories exist"""
        required_dirs = [
            'static',
            'static/css',
            'static/js',
            'templates',
            'uploads',
            'utils'
        ]
        
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            self.assertTrue(
                full_path.exists(), 
                f"Required directory {dir_path} does not exist"
            )

    def test_required_files_exist(self):
        """Test that all required files exist"""
        required_files = [
            'app.py',
            'setup.py',
            'requirements.txt',
            'static/css/style.css',
            'static/js/main.js',
            'templates/index.html',
            'utils/image_processor.py'
        ]
        
        for file_path in required_files:
            full_path = self.base_dir / file_path
            self.assertTrue(
                full_path.exists(), 
                f"Required file {file_path} does not exist"
            )

    def test_flask_app_runs(self):
        """Test that Flask application runs and returns 200 for homepage"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_upload_endpoint_exists(self):
        """Test that upload endpoint exists and accepts POST"""
        response = self.app.post('/upload')
        self.assertNotEqual(response.status_code, 404, "Upload endpoint not found")

    @unittest.skipIf(not os.path.exists("sam_vit_h_4b8939.pth"), "SAM checkpoint not found")
    def test_image_processor_initialization(self):
        """Test ImageProcessor initialization (skip if checkpoint not found)"""
        try:
            processor = ImageProcessor("sam_vit_h_4b8939.pth")
            self.assertIsNotNone(processor, "ImageProcessor failed to initialize")
        except Exception as e:
            self.fail(f"ImageProcessor initialization failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()