document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const originalImage = document.getElementById('originalImage');
    const maskImage = document.getElementById('maskImage');
    const maskedImage = document.getElementById('maskedImage');
    const tryonImage = document.getElementById('tryonImage');
    const promptInfo = document.getElementById('promptInfo');
    const usedPrompt = document.getElementById('usedPrompt');
    const generateSection = document.getElementById('generateSection');
    const generateForm = document.getElementById('generateForm');

    let currentFilename = null;

    // File size validation (16MB)
    const MAX_FILE_SIZE = 16 * 1024 * 1024;

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('clothingImage');
        const file = fileInput.files[0];
        
        if (!file) {
            showError('Please select an image file.');
            return;
        }

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            showError('File size exceeds 16MB limit.');
            return;
        }

        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            showError('Please upload a valid image file (JPEG, PNG).');
            return;
        }

        // Show progress section
        progressSection.classList.remove('d-none');
        updateProgress(10, 'Starting image upload...');

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Upload and process image for segmentation
            updateProgress(30, 'Uploading image...');
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            if (data.error) {
                throw new Error(data.error);
            }

            // Update progress for different stages
            updateProgress(70, 'Processing segmentation...');

            // Display results
            originalImage.src = `/uploads/${data.original_image}`;
            originalImage.alt = 'Original clothing';

            maskImage.src = `/uploads/${data.mask_image}`;
            maskImage.alt = 'Segmented mask';

            if (data.masked_image) {
                maskedImage.src = `/uploads/${data.masked_image}`;
                maskedImage.alt = 'Masked result';
            }

            // Store current filename
            currentFilename = data.original_image;

            // Show generate section
            generateSection.classList.remove('d-none');
            
            updateProgress(100, 'Segmentation complete! Ready for try-on generation.');
            showSuccess('Image segmented successfully! You can now generate the try-on.');

        } catch (error) {
            console.error('Error:', error);
            showError(`Error: ${error.message}`);
            updateProgress(0, 'Processing failed');
            
            // Clear images on error
            clearImages();
        }
    });

    generateForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!currentFilename) {
            showError('Please upload and segment an image first.');
            return;
        }

        const clothingType = document.getElementById('clothingType').value;
        const customPrompt = document.getElementById('customPrompt').value.trim();

        updateProgress(30, 'Generating try-on image...');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: currentFilename,
                    clothing_type: clothingType,
                    prompt: customPrompt
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            if (data.error) {
                throw new Error(data.error);
            }

            // Display try-on result
            tryonImage.src = `/uploads/${data.tryon_image}`;
            tryonImage.alt = 'Try-on result';

            if (data.prompt_used) {
                usedPrompt.textContent = data.prompt_used;
                promptInfo.classList.remove('d-none');
            }

            updateProgress(100, 'Try-on generation complete!');
            showSuccess('Try-on image generated successfully!');

        } catch (error) {
            console.error('Error:', error);
            showError(`Error: ${error.message}`);
            updateProgress(0, 'Generation failed');
            tryonImage.src = '';
        }
    });

    // Helper functions
    function updateProgress(percent, status) {
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.textContent = `${percent}%`;
        statusText.textContent = status;

        // Update progress bar color based on status
        if (percent === 0) {
            progressBar.classList.remove('bg-primary', 'bg-success');
            progressBar.classList.add('bg-danger');
        } else if (percent === 100) {
            progressBar.classList.remove('bg-primary', 'bg-danger');
            progressBar.classList.add('bg-success');
        } else {
            progressBar.classList.remove('bg-success', 'bg-danger');
            progressBar.classList.add('bg-primary');
        }
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        // Remove any existing status messages
        removeStatusMessages();
        
        uploadForm.appendChild(errorDiv);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        
        // Remove any existing status messages
        removeStatusMessages();
        
        uploadForm.appendChild(successDiv);
        
        // Remove success message after 5 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }

    function removeStatusMessages() {
        document.querySelectorAll('.error-message, .success-message').forEach(el => el.remove());
    }

    function clearImages() {
        originalImage.src = '';
        maskImage.src = '';
        maskedImage.src = '';
        tryonImage.src = '';
        promptInfo.classList.add('d-none');
        generateSection.classList.add('d-none');
        currentFilename = null;
    }

    // Preview image before upload
    document.getElementById('clothingImage').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file size
            if (file.size > MAX_FILE_SIZE) {
                showError('File size exceeds 16MB limit.');
                this.value = ''; // Clear the file input
                clearImages();
                return;
            }

            // Validate file type
            const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                showError('Please upload a valid image file (JPEG, PNG).');
                this.value = ''; // Clear the file input
                clearImages();
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                originalImage.src = e.target.result;
                clearOtherImages();
            }
            reader.readAsDataURL(file);
        }
    });

    function clearOtherImages() {
        maskImage.src = '';
        maskedImage.src = '';
        tryonImage.src = '';
        promptInfo.classList.add('d-none');
        generateSection.classList.add('d-none');
        currentFilename = null;
    }
});