import os
import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

# Add parent directory to path to import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_processor import ImageProcessor

class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('test_data')
        self.test_dir.mkdir(exist_ok=True)
        self.checkpoint_path = "sam_vit_h_4b8939.pth"
        
        # Create a test image
        self.test_image_path = self.test_dir / 'test_image.png'
        self.create_test_image()
        
        # Initialize processor if checkpoint exists
        if os.path.exists(self.checkpoint_path):
            self.processor = ImageProcessor(self.checkpoint_path)
        else:
            print(f"Warning: SAM checkpoint not found at {self.checkpoint_path}")
            self.processor = None

    def tearDown(self):
        # Clean up test files
        if self.test_dir.exists():
            for file in self.test_dir.glob('*'):
                file.unlink()
            self.test_dir.rmdir()

    def create_test_image(self):
        """Create a simple test image with a shape on white background."""
        image = Image.new('RGB', (512, 512), 'white')
        # Draw a simple rectangle in the middle
        pixels = np.array(image)
        pixels[156:356, 156:356] = [0, 0, 0]  # Black rectangle
        test_image = Image.fromarray(pixels)
        test_image.save(self.test_image_path)

    @unittest.skipIf(not os.path.exists("sam_vit_h_4b8939.pth"), "SAM checkpoint not found")
    def test_process_image(self):
        """Test the basic image processing pipeline."""
        # Process image to generate mask
        mask = self.processor.process_image(str(self.test_image_path))
        self.assertIsNotNone(mask)
        self.assertTrue(isinstance(mask, np.ndarray))
        self.assertEqual(mask.dtype, bool)

    @unittest.skipIf(not os.path.exists("sam_vit_h_4b8939.pth"), "SAM checkpoint not found")
    def test_save_mask(self):
        """Test mask saving functionality."""
        mask_path = self.test_dir / 'test_mask.png'
        # Create a simple test mask
        mask = np.zeros((512, 512), dtype=bool)
        mask[156:356, 156:356] = True
        
        saved_path = self.processor.save_mask(mask, str(mask_path))
        self.assertTrue(os.path.exists(saved_path))
        
        # Verify the saved mask
        loaded_mask = Image.open(saved_path).convert('L')
        self.assertEqual(loaded_mask.size, (512, 512))

    @unittest.skipIf(not os.path.exists("sam_vit_h_4b8939.pth"), "SAM checkpoint not found")
    def test_generate_try_on(self):
        """Test the try-on generation pipeline."""
        if self.processor is None:
            self.skipTest("Processor not initialized")

        # First generate a mask
        mask = self.processor.process_image(str(self.test_image_path))
        mask_path = self.test_dir / 'test_mask.png'
        self.processor.save_mask(mask, str(mask_path))

        # Test try-on generation
        try:
            result = self.processor.generate_try_on(
                str(self.test_image_path),
                str(mask_path),
                "a photo of a person wearing a black shirt"
            )
            self.assertIsNotNone(result)
            self.assertTrue(isinstance(result, Image.Image))
            self.assertEqual(result.size, (512, 512))
        except Exception as e:
            self.fail(f"generate_try_on raised an exception: {str(e)}")

    def test_preprocess_for_model(self):
        """Test image preprocessing."""
        processed_image = ImageProcessor.preprocess_for_model(str(self.test_image_path))
        self.assertIsNotNone(processed_image)
        self.assertTrue(isinstance(processed_image, Image.Image))
        self.assertEqual(processed_image.size, (512, 512))

    def test_resize_and_pad(self):
        """Test image resizing and padding."""
        if self.processor is None:
            self.skipTest("Processor not initialized")

        # Test with different aspect ratios
        sizes = [(800, 600), (600, 800), (512, 512)]
        for size in sizes:
            image = Image.new('RGB', size, 'white')
            resized = self.processor._resize_and_pad(image, (512, 512))
            self.assertEqual(resized.size, (512, 512))

if __name__ == '__main__':
    unittest.main()