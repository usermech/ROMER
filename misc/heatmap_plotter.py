import csv
import numpy as np
from matplotlib import use
use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import ast

def heatmap(arr):
	mat=np.reshape(arr, (18,6))
	mat=mat.transpose()
	# change ordering so the plots make sense spatially
	mat=mat[::1,::-1]

	plt.figure(figsize=(18, 6))
	sns.heatmap(mat, cmap='coolwarm', annot=True, vmin=0, vmax=0.2)	

with open("../controllers/heatmap_supervisor/grid_errors.csv") as f:
    dat=[]
    csvreader=csv.reader(f)
    for row in csvreader:
        dat.append([ast.literal_eval(x) for x in row])

## lowest error
# get the lowest error item from each one.
lowesterr_array=[pos[0][0] if len(pos)>0 else np.nan for pos in dat]
heatmap(lowesterr_array)
plt.savefig("lowest_error.png")

## avg. error
avgerr_array=[np.mean([tags[0] for tags in pos]) for pos in dat]
heatmap(avgerr_array)
plt.savefig("avg_error.png")

print("python done!!!")