import os
import urllib.request
import subprocess

def download_sam_checkpoint():
    """Download the SAM checkpoint file if it doesn't exist."""
    checkpoint_url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    checkpoint_path = "sam_vit_h_4b8939.pth"
    
    if not os.path.exists(checkpoint_path):
        print(f"Downloading SAM checkpoint from {checkpoint_url}")
        urllib.request.urlretrieve(checkpoint_url, checkpoint_path)
        print("Download complete!")
    else:
        print("SAM checkpoint already exists")

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ['uploads', 'static/css', 'static/js', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def install_requirements():
    """Install required packages."""
    try:
        subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
        print("Successfully installed requirements")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")

def main():
    print("Setting up Virtual Try-On System...")
    
    # Create necessary directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    # Download SAM checkpoint
    download_sam_checkpoint()
    
    print("\nSetup complete! You can now run the application using:")
    print("python app.py")

if __name__ == "__main__":
    main()