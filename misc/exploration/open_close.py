import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load the image
img = cv2.imread('end.png', cv2.IMREAD_GRAYSCALE)

# Define the kernel size for erosion and dilation
kernel_size = (25, 25)

# Create the erosion kernel
erosion_kernel = np.ones(kernel_size, np.uint8)

# Erode the image
dilated_img = cv2.dilate(img, erosion_kernel, iterations=1)

# erode the image
#eroded_img = cv2.erode(dilated_img, erosion_kernel, iterations=1)

# Perform connected component analysis
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dilated_img, connectivity=8)

original_image = cv2.imread('map_framed.png', cv2.IMREAD_COLOR)
# Display the centroids in the original image
for centroid in centroids:
    cv2.circle(original_image, (int(centroid[0]), int(centroid[1])), 5, (255, 0, 0), -1)    
    # Return the list of foreground centroids pixel coordinates

# save foreground centroids in a file
with open('foreground_centroids.txt', 'w') as f:
    for centroid in centroids:
        f.write(str(centroid[0]) + ' ' + str(centroid[1]) + '\n')

# Display the original and processed images
cv2.imshow('Original Image', original_image)
cv2.imshow('Eroded Image', dilated_img)    

# Wait for a key press and then close the windows

cv2.waitKey(0)
cv2.destroyAllWindows()