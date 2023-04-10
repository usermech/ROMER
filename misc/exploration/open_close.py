import cv2 
import numpy as np

with open('med_axis.txt', 'r') as f:
    medial = [tuple(map(float, line.split())) for line in f]

def count_neighbors(point, medial):
        """Returns a list of valid neighbors for the given point on the grid map"""
        x, y = point
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)]
        valid_neighbors = []
        for neighbor in neighbors:
            if neighbor in medial:
                valid_neighbors.append(neighbor)
        return len(valid_neighbors)

intersection = []
for point in medial:    
    num_neighbors = count_neighbors(point,medial)
    if num_neighbors >= 3:
        intersection.append(point)

# load map image
img = cv2.imread('map_framed.png', 0)

# create a black image
img2 = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

# make intersections white
for point in intersection:
    img2[int(point[1]), int(point[0])] = (255, 255, 255)

gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)


# Define the kernel size for erosion and dilation
kernel_size = (23, 23)

# Create the erosion kernel
erosion_kernel = np.ones(kernel_size, np.uint8)

# Erode the image
dilated_img = cv2.dilate(gray, erosion_kernel, iterations=1)

# erode the image
#eroded_img = cv2.erode(dilated_img, erosion_kernel, iterations=1)

# Perform connected component analysis
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dilated_img, connectivity=8)

original_image = cv2.imread('map_framed.png', cv2.IMREAD_COLOR)
centroids = centroids[1:]
# Display the centroids in the original image
for centroid in centroids:
    cv2.circle(original_image, (int(centroid[0]), int(centroid[1])), 5, (255, 0, 0), -1)    
    # Return the list of foreground centroids pixel coordinates
with open('foreground_centroids.txt', 'w') as f:
    for centroid in centroids:
        f.write(str(centroid[0]) + ' ' + str(centroid[1]) + '\n')
# Display the original and processed images
cv2.imshow('Original Image', original_image)
cv2.imshow('Eroded Image', dilated_img)    

# Wait for a key press and then close the windows

cv2.waitKey(0)
cv2.destroyAllWindows()
    