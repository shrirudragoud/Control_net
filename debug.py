import os
import sys
import platform
import torch
import psutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log')
    ]
)
logger = logging.getLogger(__name__)

class SystemDebugger:
    def __init__(self):
        self.issues_found = []
        self.warnings = []

    def check_system(self):
        """Run all system checks and log results."""
        logger.info("Starting system diagnostics...")
        
        # System Information
        self.log_system_info()
        
        # Python Environment
        self.check_python()
        
        # GPU/CUDA
        self.check_gpu()
        
        # Disk Space
        self.check_disk_space()
        
        # Required Files
        self.check_required_files()
        
        # Memory
        self.check_memory()
        
        # Report Results
        self.report_results()

    def log_system_info(self):
        """Log basic system information."""
        logger.info("=== System Information ===")
        logger.info(f"OS: {platform.system()} {platform.version()}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"CPU: {platform.processor()}")
        logger.info(f"CPU Cores: {psutil.cpu_count()}")
        logger.info(f"Working Directory: {os.getcwd()}")

    def check_python(self):
        """Check Python version and packages."""
        logger.info("\n=== Python Environment ===")
        
        # Check Python version
        major, minor = sys.version_info[:2]
        if (major, minor) < (3, 8):
            self.issues_found.append(f"Python version {major}.{minor} is below required 3.8")
        
        # Check required packages
        required_packages = [
            'torch', 'flask', 'numpy', 'opencv-python', 'pillow',
            'diffusers', 'transformers', 'segment-anything'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ {package} is installed")
            except ImportError:
                self.issues_found.append(f"Missing required package: {package}")

    def check_gpu(self):
        """Check GPU and CUDA availability."""
        logger.info("\n=== GPU/CUDA Status ===")
        
        if torch.cuda.is_available():
            logger.info(f"CUDA is available: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA version: {torch.version.cuda}")
            
            # Check GPU memory
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"GPU Memory: {gpu_memory:.2f}GB")
            
            if gpu_memory < 4:
                self.warnings.append("GPU has less than 4GB memory, performance may be affected")
        else:
            self.warnings.append("CUDA is not available - running on CPU will be slower")

    def check_disk_space(self):
        """Check available disk space."""
        logger.info("\n=== Disk Space ===")
        
        try:
            if platform.system() == 'Windows':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p('.'), None, None, ctypes.pointer(free_bytes)
                )
                free_gb = free_bytes.value / (1024**3)
            else:
                st = os.statvfs('.')
                free_gb = (st.f_bavail * st.f_frsize) / (1024**3)

            logger.info(f"Free disk space: {free_gb:.1f}GB")
            
            if free_gb < 5:
                self.issues_found.append(f"Low disk space: {free_gb:.1f}GB (minimum 5GB required)")
            elif free_gb < 10:
                self.warnings.append(f"Limited disk space: {free_gb:.1f}GB")
                
        except Exception as e:
            self.issues_found.append(f"Failed to check disk space: {str(e)}")

    def check_required_files(self):
        """Check for required files and directories."""
        logger.info("\n=== Required Files ===")
        
        required_files = [
            ('models/sam_vit_h_4b8939.pth', "SAM model"),
            ('models/control_v11p_sd15_inpaint.pth', "ControlNet model"),
            ('requirements.txt', "Requirements file"),
            ('app.py', "Main application"),
        ]
        
        required_dirs = ['models', 'uploads', 'static', 'templates']
        
        for path, name in required_files:
            if not os.path.exists(path):
                self.issues_found.append(f"Missing {name} at {path}")
            else:
                size_mb = os.path.getsize(path) / (1024*1024)
                logger.info(f"✓ {name} found ({size_mb:.1f}MB)")
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                self.issues_found.append(f"Missing required directory: {directory}")
            else:
                logger.info(f"✓ Directory {directory} exists")

    def check_memory(self):
        """Check system memory."""
        logger.info("\n=== System Memory ===")
        
        vm = psutil.virtual_memory()
        total_gb = vm.total / (1024**3)
        available_gb = vm.available / (1024**3)
        
        logger.info(f"Total RAM: {total_gb:.1f}GB")
        logger.info(f"Available RAM: {available_gb:.1f}GB")
        
        if available_gb < 4:
            self.issues_found.append(f"Low memory: {available_gb:.1f}GB available")
        elif available_gb < 8:
            self.warnings.append(f"Limited memory: {available_gb:.1f}GB available")

    def report_results(self):
        """Report all findings."""
        logger.info("\n=== Diagnostic Results ===")
        
        if not self.issues_found and not self.warnings:
            logger.info("✅ No issues found! System is ready to run.")
            return
        
        if self.warnings:
            logger.warning("\nWarnings:")
            for warning in self.warnings:
                logger.warning(f"⚠️  {warning}")
                
        if self.issues_found:
            logger.error("\nIssues Found:")
            for issue in self.issues_found:
                logger.error(f"❌ {issue}")
            
            logger.info("\nPlease fix the above issues before running the application.")
        else:
            logger.info("\nSystem can run but some features may be limited.")

def main():
    """Run the debugger."""
    try:
        debugger = SystemDebugger()
        debugger.check_system()
    except Exception as e:
        logger.error(f"Debug process failed: {str(e)}")
        return 1
    return 0 if not debugger.issues_found else 1

if __name__ == "__main__":
    sys.exit(main())