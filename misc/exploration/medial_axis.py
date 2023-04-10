import numpy as np
from skimage import morphology, draw, measure
import cv2
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import networkx as nx


def medial_axis(img):
    # invert the image to treat the free space as foreground
    img = img.astype(bool)
    # compute the medial axis
    skel, distance = morphology.medial_axis(img, return_distance=True)
    # create a blank grayscale image to store the medial axis
    med_axis = np.zeros(img.shape, dtype=np.uint8)
    # set the pixel values of the medial axis based on the distance transform
    med_axis[skel] = 255
    # return the medial axis image
    return med_axis

def find_medial_axis_vertices(med_axis):
    # find the contours of the medial axis image
    contours = measure.find_contours(med_axis, 0.5)
    # find the center of each contour
    centers = [np.mean(contour, axis=0).astype(int) for contour in contours]
    vertices = centers
    # vertices.extend(intersections)
    '''
    vertices = []
    # approximate each contour with a polygon
    for contour in contours:
        polygon = measure.approximate_polygon(contour, tolerance=2.0)
        vertices.extend(polygon.tolist())
    # remove duplicate vertices
    vertices = list(set(tuple(v) for v in vertices))
    # return the vertices
   '''
    # merge vertices that are close to each other
    dist_matrix = cdist(vertices, vertices)
    for i, v1 in enumerate(vertices):
        for j, v2 in enumerate(vertices[i+1:], start=i+1):
            if dist_matrix[i, j] < 3:
                vertices[i] = v1
                vertices[j] = v1
    
    return vertices, contours

def cast_rays(img, pixel_coords):    
    # Initialize results list
    results = []    
    # Iterate over pixel coordinates
    i = 0
    for coord in pixel_coords:
        pre_results = []
        # Iterate over angles
        for angle in range(0,360,2):
            # Iterate over distances
            for dist in range(0,100):
                # Calculate x and y coordinates
                x = int(coord[0] + np.cos(np.radians(angle))*dist)
                y = int(coord[1] + np.sin(np.radians(angle))*dist)
                # Check if x and y are within the image
                if x < 0 or x > img.shape[0] - 1 or y < 0 or y > img.shape[1] - 1 or (x,y) in pre_results:
                    break
                # Check if pixel is occupied
                if img[x,y] == 0:
                    pre_results.append((x,y))
                    break
        results.append(pre_results)       
    return results


def is_unique_point(lst,vertex):    
    res = []
    new_lst = []
    res_point = []
    points = set(sum(lst, []))
    print(f"number of detected walls are {len(points)}")    
    sorted_list = sorted(lst, key=lambda x: len(x),reverse=True)
    sorted_index = sorted(range(len(lst)), key=lambda x: len(lst[x]),reverse=True)
    for point in points:
        print(point)
        for i in range(len(sorted_list)):
            if point in sorted_list[i]:
                if point not in res_point:
                    res.append(vertex[sorted_index[i]])
                    for j in range(len(sorted_list[i])):
                        if sorted_list[i][j] not in res_point:
                            res_point.append(sorted_list[i][j])                            
                break
    print(f"number of detected walls are {len(res_point)}")
    return res, points



img = cv2.imread("map_framed.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = img//240
img_copy = img.copy()
# make grayscale image binary

# compute the medial axis of the free space
med_axis = medial_axis(img)
# find the white pixels in the medial axis image
white = np.where(med_axis == 255)
# create a list of vertices from the white pixels where x is white[0] and y is white[1] in numpy array form
vertices = list(zip(white[0], white[1]))
print(len(vertices))

# print(f" whites are {white}")
'''
vertices = []
for x in range(med_axis.shape[0]):
    for y in range(med_axis.shape[1]):
        if med_axis[x, y] == 255:
            neighbors = med_axis[max(0, x-2):min(med_axis.shape[0], x+2),
                                    max(0, y-2):min(med_axis.shape[1], y+2)]
            print(neighbors)
            if np.sum(neighbors == 255) > 4:
                vertices.append((x, y))
                '''
# vertices,cont = find_medial_axis_vertices(med_axis)
#print(f"vertices is {vertices}")
# plan a path through the medial axis
#path = plan_path(vertices, img)
detected_walls = cast_rays(img_copy, vertices) 
print(f"number of detected walls are {len(detected_walls)}")  
'''
dw = []
v = []
for i in range(len(detected_walls)):
    is_subset = False
    for j in range(len(detected_walls)):
        if i != j and set(detected_walls[i]).issubset(set(detected_walls[j])):
            if detected_walls != detected_walls[j]:
                is_subset = True
            break
    if not is_subset:
        dw.append(detected_walls[i])
        v.append(vertices[i])
result = v
'''
result,pts = is_unique_point(detected_walls,vertices)
# create a black image with the same dimensions as the original image
end = np.zeros(img.shape, dtype=np.uint8)
# make the pixels in the 'result' white
for p in result:
    end[p[0], p[1]] = 255
# display the results
cv2.imshow("end",end)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite("end.png",end)
'''
# display the results
fig, axes = plt.subplots(1, 2, figsize=(8, 4)) 
axes[0].imshow(img, cmap='gray')
axes[0].set_title('Input')
axes[1].imshow(med_axis, cmap='gray')
axes[0].plot([p[1] for p in result],[p[0] for p in result],'ro')
axes[0].plot([p[1] for p in pts],[p[0] for p in pts],'bo')
axes[1].set_title('Medial Axis')
plt.show()
'''