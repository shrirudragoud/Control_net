import os
import cv2
import numpy as np
import torch
from PIL import Image
from segment_anything import sam_model_registry, SamPredictor
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, checkpoint_path, model_type="vit_h"):
        """Initialize the image processor with SAM and Stable Diffusion models."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize SAM
        self.model_type = model_type
        self.sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)
        
        # Initialize Stable Diffusion with ControlNet
        self.init_stable_diffusion()

    def init_stable_diffusion(self):
        """Initialize Stable Diffusion with ControlNet for inpainting and generation."""
        try:
            # Load ControlNet for processing
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11p_sd15_inpaint",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )

            # Load Stable Diffusion pipeline
            self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                safety_checker=None
            ).to(self.device)

            # Use more efficient attention processor if available
            if hasattr(self.pipe, 'enable_xformers_memory_efficient_attention'):
                self.pipe.enable_xformers_memory_efficient_attention()

            # Use better scheduler
            self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
            
            logger.info("Successfully initialized Stable Diffusion with ControlNet")
        except Exception as e:
            logger.error(f"Error initializing Stable Diffusion: {str(e)}")
            raise

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
        mask_image = (mask * 255).astype(np.uint8)
        cv2.imwrite(save_path, mask_image)
        return save_path

    def generate_try_on(self, original_image_path, mask_path, prompt):
        """Generate try-on image using Stable Diffusion with ControlNet."""
        try:
            # Load original image and mask
            init_image = Image.open(original_image_path).convert("RGB")
            mask_image = Image.open(mask_path).convert("RGB")

            # Resize images if needed
            target_size = (512, 512)
            init_image = init_image.resize(target_size)
            mask_image = mask_image.resize(target_size)

            # Prepare control image (masked area)
            control_image = Image.new('RGB', target_size, 'white')
            control_image.paste(init_image, (0, 0), mask_image)

            # Generate image
            output = self.pipe(
                prompt=prompt,
                image=init_image,
                control_image=control_image,
                num_inference_steps=30,
                guidance_scale=7.5,
                controlnet_conditioning_scale=0.8
            ).images[0]

            return output

        except Exception as e:
            logger.error(f"Error generating try-on image: {str(e)}")
            raise

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
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        return image

    @staticmethod
    def postprocess_result(result_image, save_path):
        """Save the generated image."""
        if isinstance(result_image, Image.Image):
            result_image.save(save_path)
        else:
            result_image = Image.fromarray(result_image)
            result_image.save(save_path)