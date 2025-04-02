import os
import urllib.request
import sys
from tqdm import tqdm

def download_file(url, filename):
    """Download a file with progress bar."""
    try:
        print(f"Downloading {filename}...")
        response = urllib.request.urlopen(url)
        total_size = int(response.headers.get('Content-Length', 0))
        
        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            urllib.request.urlretrieve(
                url,
                filename,
                reporthook=lambda count, block_size, total_size: pbar.update(block_size)
            )
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

def main():
    # Create models directory
    os.makedirs('models', exist_ok=True)

    # Model URLs
    models = {
        "sam_vit_h_4b8939.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "control_v11p_sd15_inpaint.pth": "https://huggingface.co/lllyasviel/control_v11p_sd15_inpaint/resolve/main/diffusion_pytorch_model.bin"
    }

    success = True
    for filename, url in models.items():
        filepath = os.path.join('models', filename)
        if not os.path.exists(filepath):
            print(f"\nDownloading {filename}...")
            if not download_file(url, filepath):
                success = False
                break
        else:
            print(f"\n{filename} already exists in models directory")

    if success:
        print("\nAll models downloaded successfully!")
    else:
        print("\nError downloading models. Please try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()