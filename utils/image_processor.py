import os
import cv2
import numpy as np
import torch
from PIL import Image
from segment_anything import sam_model_registry, SamPredictor

class ImageProcessor:
    def __init__(self, checkpoint_path, model_type="vit_h"):
        """Initialize the image processor with SAM model."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Initialize SAM
        self.model_type = model_type
        self.sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)

    def process_image(self, image_path):
        """Process an image to generate segmentation mask."""
        # Read and process image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Set image in predictor
        self.predictor.set_image(image)
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Generate automatic points for clothing detection
        # For now, we'll use center points and points around the image center
        center_x, center_y = width // 2, height // 2
        offset = min(width, height) // 4
        
        input_points = np.array([
            [center_x, center_y],  # Center
            [center_x - offset, center_y],  # Left
            [center_x + offset, center_y],  # Right
            [center_x, center_y - offset],  # Top
            [center_x, center_y + offset]   # Bottom
        ])
        
        input_labels = np.array([1, 1, 1, 1, 1])  # All points are foreground
        
        # Generate masks
        masks, scores, logits = self.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True
        )
        
        # Select best mask
        best_mask_idx = np.argmax(scores)
        best_mask = masks[best_mask_idx]
        
        return best_mask

    def save_mask(self, mask, save_path):
        """Save the generated mask as an image."""
        # Convert boolean mask to uint8
        mask_image = (mask * 255).astype(np.uint8)
        cv2.imwrite(save_path, mask_image)
        return save_path

    @staticmethod
    def apply_mask_to_image(image_path, mask_path, save_path):
        """Apply the mask to the original image and save the result."""
        # Read images
        image = cv2.imread(image_path)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        # Ensure mask is binary
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        
        # Create masked image
        masked_image = cv2.bitwise_and(image, image, mask=mask)
        
        # Save result
        cv2.imwrite(save_path, masked_image)
        return save_path

    @staticmethod
    def preprocess_for_model(image_path, target_size=(512, 512)):
        """Preprocess image for the model."""
        image = Image.open(image_path)
        # Add preprocessing steps as needed
        return image

    @staticmethod
    def postprocess_result(result_image):
        """Postprocess the model output."""
        # Add postprocessing steps as needed
        return result_image