import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import cv2
import plantcv as pcv
from skimage.morphology import medial_axis, skeletonize
from skimage.filters import threshold_otsu,gaussian
from skimage.io import imread
from skimage.color import rgb2gray
import tensorflow as tf
from tensorflow import keras

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

    # ✅ Replace cv2_imshow() with plt.imshow()
    plt.figure(figsize=(6, 6))
    plt.imshow(output, cmap='gray')
    plt.axis("off")
    plt.title("Connected Components")
    plt.show()

    return output

def show_image(img, title="Image"):
    """Helper function to display images using Matplotlib (for Jupyter Notebook)."""
    if len(img.shape) == 3 and img.shape[2] == 3:  # Convert BGR to RGB if needed
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img)
    else:
        plt.imshow(img, cmap='gray')
        
    plt.title(title)
    plt.axis('off')
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
    fig, ax = plt.subplots(nrows=len(dividers), figsize=(5,10))
    if len(dividers)==1:
      pass
      #ax.imshow(crop[:,dividers[0][0]:dividers[0][1]], cmap="gray")
    else:
        for index, window in enumerate(dividers):
          #ax[index].axis("off")
          #cv2.imwrite('/content/drive/MyDrive/LineSegmentation/b1/3/{}.jpg'.format(index),crop[:,window[0]:window[1]])
          res.append(crop[:,window[0]:window[1]])
          ax[index].imshow(crop[:,window[0]:window[1]], cmap="gray")
    return res


def show_image(img, title="Image"):
    """Helper function to display images using Matplotlib (for Jupyter Notebook)"""
    plt.imshow(img, cmap='gray')
    plt.title(title)
    plt.axis('off')
    plt.show()

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
  num_to_name = {0: 'a', 1: 'a(3)', 2: 'a(4)', 3: 'a(5)', 4: 'aaa', 5: 'ba', 6: 'ba(2)', 7: 'baa', 8: 'be', 9: 'bha', 10: 'bhaa', 11: 'bhe', 12: 'bhi', 13: 'bhii', 14: 'bho', 15: 'bhu', 16: 'bhuu', 17: 'bi', 18: 'bii', 19: 'bo', 20: 'bo(2)', 21: 'bu', 22: 'buu', 23: 'ca', 24: 'caa', 25: 'ce', 26: 'cha', 27: 'chaa', 28: 'che', 29: 'chi', 30: 'chii', 31: 'cho', 32: 'chu', 33: 'chuu', 34: 'ci', 35: 'cii', 36: 'co', 37: 'cu', 38: 'cuu', 39: 'da(2)', 40: 'daa', 41: 'daa(2)', 42: 'daaa', 43: 'daaaa', 44: 'dae', 45: 'dai', 46: 'daii', 47: 'dao', 48: 'dau', 49: 'dauu', 50: 'de', 51: 'dha', 52: 'dhaa', 53: 'dhaaa', 54: 'dhaaaa', 55: 'dhae', 56: 'dhai', 57: 'dhaii', 58: 'dhao', 59: 'dhau', 60: 'dhauu', 61: 'dhi', 62: 'dhii', 63: 'dho', 64: 'dhu', 65: 'dhue', 66: 'dhuu', 67: 'di', 68: 'dii', 69: 'do', 70: 'du', 71: 'duu', 72: 'e', 73: 'ee', 74: 'ga', 75: 'gaa', 76: 'ge', 77: 'gha', 78: 'ghaa', 79: 'ghe', 80: 'ghi', 81: 'ghii', 82: 'gho', 83: 'ghu', 84: 'ghuu', 85: 'gi', 86: 'gii', 87: 'go', 88: 'gu', 89: 'guu', 90: 'ha', 91: 'haa', 92: 'he', 93: 'hi', 94: 'hii', 95: 'ho', 96: 'hu', 97: 'huu', 98: 'i', 99: 'ja', 100: 'ja(2)', 101: 'ja(3)', 102: 'ja(4)', 103: 'jaa', 104: 'je', 105: 'jha', 106: 'jhaa', 107: 'jhe', 108: 'jhi', 109: 'jhii', 110: 'jho', 111: 'jhu', 112: 'jhuu', 113: 'ji', 114: 'jii', 115: 'jo', 116: 'ju', 117: 'juu', 118: 'ka', 119: 'kaa', 120: 'ke', 121: 'kha', 122: 'kha(2)', 123: 'khaa', 124: 'khaa(2)', 125: 'khe', 126: 'khe(2)', 127: 'khi', 128: 'khii', 129: 'khii(2)', 130: 'kho', 131: 'kho(2)', 132: 'khu', 133: 'khu(2)', 134: 'khuu', 135: 'khuu(2)', 136: 'ki', 137: 'kii', 138: 'ko', 139: 'ku', 140: 'kuu', 141: 'la', 142: 'la(2)', 143: 'la(3)', 144: 'laa', 145: 'le', 146: 'li', 147: 'lii', 148: 'lo', 149: 'lu', 150: 'luu', 151: 'ma', 152: 'ma(2)', 153: 'maa', 154: 'me', 155: 'mi', 156: 'mii', 157: 'mo', 158: 'mu', 159: 'muu', 160: 'na', 161: 'na(2)', 162: 'naa', 163: 'ne', 164: 'ni', 165: 'nii', 166: 'nna', 167: 'nnaa', 168: 'nne', 169: 'nni', 170: 'nnii', 171: 'nno', 172: 'nno(2)', 173: 'nnu', 174: 'nnuu', 175: 'no', 176: 'nu', 177: 'nuu', 178: 'nya', 179: 'nya(2)', 180: 'o', 181: 'o(2)', 182: 'pa', 183: 'paa', 184: 'pe', 185: 'pha', 186: 'pha(2)', 187: 'phaa', 188: 'phe', 189: 'phi', 190: 'phii', 191: 'pho', 192: 'phu', 193: 'phuu', 194: 'pi', 195: 'pii', 196: 'po', 197: 'pu', 198: 'puu', 199: 'ra', 200: 'ra(2)', 201: 'ra(3)', 202: 'raa', 203: 're', 204: 'ri', 205: 'rii', 206: 'ro', 207: 'ru', 208: 'ruu', 209: 'sa', 210: 'sa(2)', 211: 'saa', 212: 'se', 213: 'sha', 214: 'shaa', 215: 'shaaa', 216: 'shaaaa', 217: 'shae', 218: 'shai', 219: 'shaii', 220: 'shao', 221: 'shau', 222: 'she', 223: 'shi', 224: 'shii', 225: 'sho', 226: 'shu', 227: 'shuu', 228: 'si', 229: 'sii', 230: 'so', 231: 'su', 232: 'suu', 233: 'ta', 234: 'taa', 235: 'taaa', 236: 'taaaa', 237: 'tae', 238: 'tai', 239: 'taii', 240: 'tao', 241: 'tau', 242: 'tauu', 243: 'te', 244: 'tha', 245: 'tha(2)', 246: 'thaa', 247: 'thaaa', 248: 'thaaaa', 249: 'thaai', 250: 'thae', 251: 'thai', 252: 'thaii', 253: 'thao', 254: 'thau', 255: 'thauu', 256: 'the', 257: 'the(2)', 258: 'thi', 259: 'thii', 260: 'tho', 261: 'thu', 262: 'thuu', 263: 'tii', 264: 'to', 265: 'tu', 266: 'tuu', 267: 'va', 268: 'vaa', 269: 'vhu', 270: 'vhuu', 271: 'vi', 272: 'vii', 273: 'vu', 274: 'vu(2)', 275: 'vuu', 276: 'vuu(2)', 277: 'ya', 278: 'ya(2)', 279: 'yaa', 280: 'ye', 281: 'yi', 282: 'yii', 283: 'yo', 284: 'yo(2)', 285: 'yu', 286: 'yuu'}
  
  test_images = []
  for image_name in images:
        # Resize to the required dimensions
        curImg = cv2.resize(image_name, (75, 75))
        
        # Make sure it's single channel (grayscale)
        if len(curImg.shape) == 3:  # If it's RGB
            curImg = cv2.cvtColor(curImg, cv2.COLOR_BGR2GRAY)
            
        # Normalize pixel values
        curImg = curImg / 255.0
        
        # Flatten the image to 1D array (if your model expects flattened input)
        # Change this dimension to match what your model expects (480 according to error)
        curImg = curImg.flatten()
        
        # If needed, resize to match the expected dimension
        # This assumes the model expects a flattened vector of length 480
        if len(curImg) != 480:
            # You might need to adjust how you resize or preprocess the image
            # Option 1: Truncate or pad
            if len(curImg) > 480:
                curImg = curImg[:480]  # Truncate
            else:
                curImg = np.pad(curImg, (0, 480 - len(curImg)))  # Pad
        
        test_images.append(curImg)
  
  test_images = np.array(test_images)
  
  print(test_images.shape)  # Should now be (n, 480)
  
  predictions = model.predict(test_images)
  predictions = np.array(predictions)
  test_preds = []
  for pred in predictions:
          max_val = -1
          index_val = -1
          for idx, val in enumerate(pred):
                  if val > max_val:
                          max_val = val
                          index_val = idx
          test_preds.append(num_to_name[index_val])
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
model = keras.models.load_model("F:/final_bramhi/OCR/model.h5")


def show_image(img, title="Image"):
    plt.figure(figsize=(5, 5))
    if len(img.shape) == 2:  # Grayscale image (single-channel)
        plt.imshow(img, cmap="gray")
    else:  # Color image (BGR to RGB)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()

char_seg_height = 15
blurring = 5

# Load image
img = cv2.imread('F:/final_bramhi/OCR/recognize/output.png')
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

for i in lines:
    thinned_line = line_thinning(i)
    res_chars = charseg(thinned_line, char_seg_height)
    res_skel = []
    
    for j in res_chars:
        temp_image = skeletonize1(j)
        res_skel.append(prune(temp_image))
    
    res_arr = predict_chars(res_skel)
    
    for k in range(len(res_skel)):
        print('---------------')
        show_image(res_chars[k], "Segmented Character")
        show_image(res_skel[k], "Skeletonized Character")
        print(res_arr[k])
