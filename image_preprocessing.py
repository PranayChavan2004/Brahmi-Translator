import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage import measure
from skimage.filters import threshold_otsu
from matplotlib import pyplot as plt


# 1. Image Loading
def load_image(image_path):
    image = cv2.imread(image_path)
    return image

# 2. Convert to Grayscale
def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 3. Denoising
def denoise_image(image):
    return cv2.fastNlMeansDenoising(image, None, 30, 7, 21)

# 4. Contrast Enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
def enhance_contrast(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)

# 5. Binarization using Otsu's Thresholding
def otsu_threshold(image):
    ret, binarized = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binarized

# 6. Canny Edge Detection
def canny_edge_detection(image):
    return cv2.Canny(image, 100, 200)

# 7. Skeletonization
def skeletonize_image(image):
    # Convert to binary (if not already)
    binary_image = image / 255
    skeleton = skeletonize(binary_image)
    return (skeleton * 255).astype(np.uint8)

# 8. Morphological Transformations (Dilation and Erosion)
def morphological_transformations(image):
    kernel = np.ones((3, 3), np.uint8)
    dilation = cv2.dilate(image, kernel, iterations=1)
    erosion = cv2.erode(image, kernel, iterations=1)
    return dilation, erosion

# 9. Connected Component Analysis
def connected_components_analysis(image):
    num_labels, labels = cv2.connectedComponents(image)
    return num_labels, labels

# 10. Character Segmentation
def character_segmentation(image):
    # Find contours (character boundaries)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

# 11. Resize and Normalize Characters
def resize_and_normalize_characters(image, contours):
    characters = []
    for contour in contours:
        # Get bounding box of each character
        x, y, w, h = cv2.boundingRect(contour)
        character = image[y:y+h, x:x+w]
        # Resize and normalize character
        character_resized = cv2.resize(character, (28, 28))
        character_normalized = character_resized / 255.0
        characters.append(character_normalized)
    return characters

# Main function to perform all preprocessing steps
def preprocess_image(image_path):
    image = load_image(image_path)
    
    # Convert to Grayscale
    gray = convert_to_grayscale(image)
    
    # Denoising
    denoised = denoise_image(gray)
    
    # Contrast Enhancement
    enhanced = enhance_contrast(denoised)
    
    # Binarization using Otsu's Thresholding
    binarized = otsu_threshold(enhanced)
    
    # Canny Edge Detection
    edges = canny_edge_detection(binarized)
    
    # Skeletonization
    skeleton = skeletonize_image(binarized)
    
    # Morphological Transformations
    dilation, erosion = morphological_transformations(skeleton)
    
    # Connected Component Analysis
    num_labels, labels = connected_components_analysis(dilation)
    
    # Character Segmentation
    contours = character_segmentation(dilation)
    
    # Resize and Normalize Characters
    characters = resize_and_normalize_characters(dilation, contours)
    
    return characters, contours, dilation, erosion, num_labels, labels

# Example usage
image_path = 'path_to_your_image.jpg'
characters, contours, dilation, erosion, num_labels, labels = preprocess_image(image_path)

# Display results
plt.subplot(1, 2, 1)
plt.imshow(dilation, cmap='gray')
plt.title('Dilation Result')

plt.subplot(1, 2, 2)
plt.imshow(erosion, cmap='gray')
plt.title('Erosion Result')

plt.show()

print(f'Number of connected components: {num_labels}')
