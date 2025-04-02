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
        try:
            self.model_type = model_type
            if not os.path.exists(checkpoint_path):
                raise FileNotFoundError(f"SAM checkpoint not found at: {checkpoint_path}")
                
            self.sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
            self.sam.to(device=self.device)
            self.predictor = SamPredictor(self.sam)
            logger.info("Successfully initialized SAM model")
        except Exception as e:
            logger.error(f"Error initializing SAM model: {str(e)}")
            raise
        
        # Initialize Stable Diffusion with ControlNet
        self.init_stable_diffusion()

    def init_stable_diffusion(self):
        """Initialize Stable Diffusion with ControlNet for inpainting and generation."""
        try:
            # Load ControlNet for processing
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/control_v11p_sd15_inpaint",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                cache_dir="models"
            )

            # Load Stable Diffusion pipeline
            self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                safety_checker=None,
                cache_dir="models"
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
        try:
            # Read and process image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
                
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
            
            if not best_mask.any():
                raise ValueError("Generated mask is empty")
            
            return best_mask
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise

    def save_mask(self, mask, save_path):
        """Save the generated mask as an image."""
        try:
            # Convert boolean mask to uint8
            mask_image = (mask * 255).astype(np.uint8)
            # Ensure mask is binary
            _, mask_image = cv2.threshold(mask_image, 127, 255, cv2.THRESH_BINARY)
            
            # Save mask
            success = cv2.imwrite(save_path, mask_image)
            if not success:
                raise IOError(f"Failed to save mask to {save_path}")
            
            return save_path
        except Exception as e:
            logger.error(f"Error saving mask: {str(e)}")
            raise

    def generate_try_on(self, original_image_path, mask_path, prompt):
        """Generate try-on image using Stable Diffusion with ControlNet."""
        try:
            # Load and preprocess original image
            if not os.path.exists(original_image_path):
                raise FileNotFoundError(f"Original image not found: {original_image_path}")
            if not os.path.exists(mask_path):
                raise FileNotFoundError(f"Mask image not found: {mask_path}")
                
            init_image = Image.open(original_image_path).convert("RGB")
            init_image = self._resize_and_pad(init_image, (512, 512))

            # Load and preprocess mask
            mask_raw = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask_raw is None:
                raise ValueError(f"Failed to load mask: {mask_path}")
                
            # Ensure mask is binary and properly scaled
            _, mask_binary = cv2.threshold(mask_raw, 127, 255, cv2.THRESH_BINARY)
            mask_binary = cv2.resize(mask_binary, (512, 512), interpolation=cv2.INTER_NEAREST)
            
            # Create proper mask for inpainting
            mask_invert = cv2.bitwise_not(mask_binary)
            mask_image = Image.fromarray(mask_invert)

            # Create control image (masked original image)
            init_array = np.array(init_image)
            mask_array = np.array(mask_image)
            control_array = init_array.copy()
            control_array[mask_array == 0] = 255  # White background
            control_image = Image.fromarray(control_array)

            # Prepare negative prompt
            negative_prompt = (
                "low quality, blurry, bad anatomy, bad proportions, deformed, "
                "disfigured, distorted, wrong pose, duplicate, morbid, mutilated, "
                "poorly drawn face, poorly drawn hands, floating limbs"
            )

            # Generate image
            output = self.pipe(
                prompt=prompt,
                image=init_image,
                control_image=control_image,
                mask_image=mask_image,
                negative_prompt=negative_prompt,
                num_inference_steps=30,
                guidance_scale=7.5,
                controlnet_conditioning_scale=0.8
            ).images[0]

            return output

        except Exception as e:
            logger.error(f"Error generating try-on image: {str(e)}")
            raise

    def _resize_and_pad(self, image, target_size):
        """Resize image maintaining aspect ratio and pad if necessary."""
        try:
            target_width, target_height = target_size
            
            # Convert to PIL Image if necessary
            if not isinstance(image, Image.Image):
                image = Image.fromarray(image)

            # Get current dimensions
            width, height = image.size
            aspect_ratio = width / height

            if aspect_ratio > 1:
                # Image is wider than tall
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
                pad_top = (target_height - new_height) // 2
                pad_bottom = target_height - new_height - pad_top
                pad_left = 0
                pad_right = 0
            else:
                # Image is taller than wide
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
                pad_left = (target_width - new_width) // 2
                pad_right = target_width - new_width - pad_left
                pad_top = 0
                pad_bottom = 0

            # Resize
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create new image with padding
            mode = image.mode
            padded_image = Image.new(mode, target_size, (255, 255, 255))
            padded_image.paste(image, (pad_left, pad_top))

            return padded_image
            
        except Exception as e:
            logger.error(f"Error in resize_and_pad: {str(e)}")
            raise

    @staticmethod
    def apply_mask_to_image(image_path, mask_path, save_path):
        """Apply the mask to the original image and save the result."""
        try:
            # Read images
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
                
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                raise ValueError(f"Failed to load mask: {mask_path}")
            
            # Ensure mask is binary
            _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
            
            # Resize mask to match image if needed
            if mask.shape[:2] != image.shape[:2]:
                mask = cv2.resize(mask, (image.shape[1], image.shape[0]), 
                                interpolation=cv2.INTER_NEAREST)
            
            # Create masked image
            masked_image = cv2.bitwise_and(image, image, mask=mask)
            
            # Fill masked area with white
            masked_image[mask == 0] = 255
            
            # Save result
            success = cv2.imwrite(save_path, masked_image)
            if not success:
                raise IOError(f"Failed to save masked image to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error applying mask to image: {str(e)}")
            raise

    @staticmethod
    def postprocess_result(result_image, save_path):
        """Save the generated image."""
        try:
            if isinstance(result_image, Image.Image):
                result_image.save(save_path, quality=95)
            else:
                result_image = Image.fromarray(result_image)
                result_image.save(save_path, quality=95)
            
            if not os.path.exists(save_path):
                raise IOError(f"Failed to save result image to {save_path}")
                
        except Exception as e:
            logger.error(f"Error saving result image: {str(e)}")
            raise