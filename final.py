import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import json
import cv2
import plantcv as pcv
from skimage.morphology import medial_axis, skeletonize
from skimage.filters import threshold_otsu,gaussian
from skimage.io import imread
from skimage.color import rgb2gray
import tensorflow as tf
from tensorflow import keras
 
# ---------------------------------------------------------------
# Set this to True only when you want to debug locally and see
# matplotlib windows pop up. Keep False when running app.py / Flask.
# ---------------------------------------------------------------
DEBUG_SHOW = False
 
# ---------------------------------------------------------------
# Must match retrain.py's IMG_SIZE exactly, or predictions break.
# retrain.py currently uses IMG_SIZE = 64.
# ---------------------------------------------------------------
IMG_SIZE = 64
 
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
LABEL_PATH = os.path.join(BASE_DIR, 'models', 'MODEL', 'label_map.json')
 
with open(LABEL_PATH, 'r', encoding='utf-8') as f:
    _label_map = json.load(f)
# json keys are always strings -> convert back to int
NUM_TO_NAME = {int(k): v for k, v in _label_map.items()}
print(f"Loaded {len(NUM_TO_NAME)} classes from {LABEL_PATH}")
 
def connectedcomp(img , blurring=5):
    # Convert to grayscale
    gray_img = cv2.cvtColor(img ,cv2.COLOR_BGR2GRAY)
 
    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray_img, (blurring,blurring), 0)
 
    # Apply Threshold
    threshold = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
 
    # Connected Components Analysis
    analysis = cv2.connectedComponentsWithStats(threshold, 4, cv2.CV_32S)
    (totalLabels, label_ids, values, centroid) = analysis
 
    # Initialize an output image
    output = np.zeros(gray_img.shape, dtype="uint8")
 
    # Loop through components
    for i in range(1, totalLabels):
        area = values[i, cv2.CC_STAT_AREA]
 
        if area > 50:
            # Get bounding box coordinates
            x1, y1, w, h = values[i, cv2.CC_STAT_LEFT], values[i, cv2.CC_STAT_TOP], values[i, cv2.CC_STAT_WIDTH], values[i, cv2.CC_STAT_HEIGHT]
            X, Y = centroid[i]
 
            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 3)
            cv2.circle(img, (int(X), int(Y)), 4, (0, 0, 255), -1)
 
            # Create a mask for the component
            componentMask = (label_ids == i).astype("uint8") * 255
            output = cv2.bitwise_or(output, componentMask)
 
    if DEBUG_SHOW:
        plt.figure(figsize=(6, 6))
        plt.imshow(output, cmap='gray')
        plt.axis("off")
        plt.title("Connected Components")
        plt.show()
 
    return output
 
def show_image(img, title="Image"):
    """Helper function to display images using Matplotlib (debug only)."""
    if not DEBUG_SHOW:
        return
    plt.figure(figsize=(5, 5))
    if len(img.shape) == 2:  # Grayscale image (single-channel)
        plt.imshow(img, cmap="gray")
    else:  # Color image (BGR to RGB)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()
 
def lineseg(img):
    print('Performing Line Segmentation...')
    print('----------------------------------------------------')
 
    res = []
    
    # Ensure image is grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
 
    # Apply binary inverse thresholding
    _, thresh2 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
 
    # Define a rectangular kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 2))
 
    # Morphological dilation to enhance lines
    mask = cv2.morphologyEx(thresh2, cv2.MORPH_DILATE, kernel)
 
    # Display the processed mask
    show_image(mask, "Dilated Mask")
    
    print('After mask processing...')
 
    bboxes = []
    bboxes_img = gray.copy()
 
    # Find contours of segmented lines (handles OpenCV 3.x and 4.x)
    contours_info = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
    if len(contours_info) == 3:
        _, contours, _ = contours_info  # OpenCV 3.x
    else:
        contours, _ = contours_info  # OpenCV 4.x
 
    # Process each contour
    for cntr in contours:
        x, y, w, h = cv2.boundingRect(cntr)
        cv2.rectangle(bboxes_img, (x, y), (x + w, y + h), (255, 255, 255), 1)  # White border for visibility
        bboxes.append((x, y, w, h))
 
    # Display bounding box image
    show_image(bboxes_img, "Bounding Boxes on Segmented Lines")
 
    for j, (x, y, w, h) in enumerate(bboxes):
        crop = gray[y:y+h, x:x+w]
        show_image(crop, f"Segmented Line {j+1}")
 
        res.append(crop)
        print(f'Line {j+1} segmented')
 
    return res
 
def charseg(crop,char_seg_height=10):
    print('char seg')
    print('----------------------------------------------------')
    res=[]
    
    vertical_projection = np.sum(crop, axis=0)
    vertical_projection=vertical_projection/255
    vertical_projection = [round(item) for item in vertical_projection]
    # plot the vertical projects
    if DEBUG_SHOW:
        fig, ax = plt.subplots(nrows=2)
        plt.xlim(0, crop.shape[1])
        ax[0].imshow(crop, cmap="gray")
        ax[1].plot(vertical_projection)
    #Continuation of Word Segmentation, works well if there is more than 1 word
    height = crop.shape[0]
    width=crop.shape[1]
    #print(width)
    #print(height)
    height-=height/char_seg_height
    ## we will go through the vertical projections and 
    ## find the sequence of consecutive white spaces in the image
    whitespace_lengths = []
    whitespace = 0
    #print(vertical_projection)
    for vp in vertical_projection:
        if vp >= height:
            whitespace = whitespace + 1
        elif vp < height:
            if whitespace != 0:
                whitespace_lengths.append(whitespace)
            whitespace = 0 # reset whitepsace counter. 
    if whitespace!=0:
      whitespace_lengths.append(whitespace)
    #print("whitespaces:", whitespace_lengths)
    #avg_white_space_length = min(whitespace_lengths)
    avg_white_space_length=min(whitespace_lengths)
    #print("average whitespace lenght:", avg_white_space_length)
    whitespace_length = 0
    divider_indexes = []
    divider_indexes.append(0)
    for index, vp in enumerate(vertical_projection):
        if vp >= height:
            whitespace_length = whitespace_length + 1
        elif vp < height:
            if whitespace_length != 0 and whitespace_length >= avg_white_space_length:
                #print(whitespace_length)
                divider_indexes.append(index-int(whitespace_length/2))
            whitespace_length = 0 # reset it
    divider_indexes.append(index-int(whitespace_length/2))            
    #print(divider_indexes)
    divider_indexes = np.array(divider_indexes)
    dividers = np.column_stack((divider_indexes[:-1],divider_indexes[1:]))
    #print(dividers)
    if DEBUG_SHOW:
        fig, ax = plt.subplots(nrows=len(dividers), figsize=(5,10))
    if len(dividers)==1:
      pass
      #ax.imshow(crop[:,dividers[0][0]:dividers[0][1]], cmap="gray")
    else:
        for index, window in enumerate(dividers):
          #ax[index].axis("off")
          #cv2.imwrite('/content/drive/MyDrive/LineSegmentation/b1/3/{}.jpg'.format(index),crop[:,window[0]:window[1]])
          res.append(crop[:,window[0]:window[1]])
          if DEBUG_SHOW:
              ax[index].imshow(crop[:,window[0]:window[1]], cmap="gray")
    return res
 
 
def skeletonize1(charImg):
    print('Skeletonization')
    print('----------------------------------------------------')
    
    img_inverse = 255 - charImg
    size = np.size(img_inverse)
    skel = np.zeros(img_inverse.shape, np.uint8)
 
    ret, img_inverse = cv2.threshold(img_inverse, 127, 255, 0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    done = False
 
    while not done:
        eroded = cv2.erode(img_inverse, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img_inverse, temp)
        skel = cv2.bitwise_or(skel, temp)
        img_inverse = eroded.copy()
 
        zeros = size - cv2.countNonZero(img_inverse)
        if zeros == size:
            done = True
 
    show_image(skel, "Skeletonized Image (Method 1)")
    return skel
 
def skeletonize2(charImg):
    ret, charImg = cv2.threshold(charImg, 127, 255, 0)
    curImg = skeletonize(charImg)
    show_image(curImg, "Skeletonized Image (Method 2)")
    return curImg
 
def skeletonize3(charImg):
    img_inverse = 255 - charImg
    skel, distance = medial_axis(img_inverse, return_distance=True)
    show_image(skel, "Skeletonized Image (Method 3)")
    return skel
 
def prune(skeleton):
    # Resize the skeleton to make it larger
    skeleton_big = cv2.resize(skeleton, (2 * skeleton.shape[1], 2 * skeleton.shape[0]))
    
    # Create a structuring element and dilate
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    dil = cv2.dilate(skeleton_big, element)
    
    # Import morphology directly from plantcv.plantcv
    from plantcv.plantcv import morphology
    
    # Use the imported morphology module directly
    pruned_skeleton, segmented_img, segment_objects = morphology.prune(skel_img=dil, size=70)
    
    # Dilate the pruned skeleton
    kernel = np.ones((3, 3), np.uint8)
    img_dilation = cv2.dilate(pruned_skeleton, kernel, iterations=2)
    
    # Threshold to get a binary image
    ret, binImg = cv2.threshold(img_dilation, 127, 255, cv2.THRESH_BINARY)
    
    # Invert the binary image
    res = 255 - binImg
    show_image(res, "Pruned Skeleton")
    
    return res
 
def predict_chars(images):
 
    test_images = []
 
    for image_name in images:
 
        # Resize image to CNN expected size (must match retrain.py's IMG_SIZE)
        curImg = cv2.resize(image_name, (IMG_SIZE, IMG_SIZE))
 
        # Convert to grayscale if needed
        if len(curImg.shape) == 3:
            curImg = cv2.cvtColor(curImg, cv2.COLOR_BGR2GRAY)
 
        # Normalize pixel values
        curImg = curImg.astype("float32") / 255.0
 
        # Add channel dimension
        curImg = np.expand_dims(curImg, axis=-1)
 
        test_images.append(curImg)
 
    # Convert list to numpy array
    test_images = np.array(test_images)
 
    # Debugging
    print("Input shape to model:", test_images.shape)
 
    # Model prediction
    predictions = model.predict(test_images)
 
    test_preds = []
 
    for pred in predictions:
 
        # Get predicted class index
        index_val = np.argmax(pred)
        confidence = pred[index_val]
 
        # Convert index to character using the dynamically loaded label map
        if index_val in NUM_TO_NAME:
            test_preds.append(NUM_TO_NAME[index_val])
        else:
            test_preds.append("Unknown")
 
        print(f"  -> class idx={index_val}  conf={confidence:.3f}  label={NUM_TO_NAME.get(index_val, 'UNKNOWN_IDX')}")
 
    return test_preds
 
 
 
def check_invert(img):
  white_count,black_count=0,0
  img_arr = np.array(img)
  for i in img_arr:
    for j in i:
      if j==255:
        white_count+=1
      elif j==0:
        black_count+=1
  if black_count>white_count:
    return 255-img
  return img
    
 
def line_thinning(img):
  kernel = np.ones((1, 1), np.uint8)
  img_erosion = cv2.dilate(img, kernel, iterations=2)
  #print('thinning')
  #cv2_imshow(img_erosion)
  return img_erosion
 
 
#loading model
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'MODEL', 'model.h5')
model = keras.models.load_model(MODEL_PATH)
print(f"Loaded model from {MODEL_PATH}")
print(f"Model input shape: {model.input_shape}")
 
 
def run_ocr(image_path=None):
 
    char_seg_height = 15
    blurring = 5
 
    # Default image path
    if image_path is None:
        image_path = r"C:\Users\pranay umesh chavan\BRAHMI\final_bramhi\models\input\b1.jpg"
 
    # Load image
    img = cv2.imread(image_path)
 
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
 
    show_image(img, "Original Image")
 
    # Resize image
    img = cv2.resize(img, (5 * img.shape[1], 5 * img.shape[0]))
 
    # Apply connected components
    cc_img = connectedcomp(img, blurring)
 
    show_image(cc_img, "Connected Components")
 
    # Check and invert image
    cc_img_1 = check_invert(cc_img)
 
    show_image(cc_img_1, "Inverted Image")
 
    # Perform line segmentation
    lines = lineseg(cc_img_1)
 
    print("Number of lines detected:", len(lines))
 
    final_predictions = []
 
    for i in lines:
 
        thinned_line = line_thinning(i)
 
        res_chars = charseg(thinned_line, char_seg_height)
 
        res_skel = []
 
        for j in res_chars:
 
            temp_image = skeletonize1(j)
 
            pruned = prune(temp_image)
 
            res_skel.append(pruned)
 
        # Predict characters
        res_arr = predict_chars(res_skel)
 
        for k in range(len(res_skel)):
 
            print('---------------')
 
            show_image(res_chars[k], "Segmented Character")
 
            show_image(res_skel[k], "Skeletonized Character")
 
            print(res_arr[k])
 
            final_predictions.append(res_arr[k])
 
    return final_predictions
 
 
# Run directly only if this file is executed standalone
if __name__ == "__main__":
 
    predictions = run_ocr()
 
    print("\nFinal Predictions:")
    print(predictions)