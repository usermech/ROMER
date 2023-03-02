import csv
import numpy as np
from matplotlib import use
use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import argparse
from os import path, makedirs

def heatmap(arr, title):
	mat=np.reshape(arr, (18,6))
	mat=mat.transpose()
	# change ordering so the plots make sense spatially
	mat=mat[::1,::-1]

	fig=plt.figure(figsize=(18, 6))
	fig.suptitle(title)
	sns.heatmap(mat, cmap='coolwarm', annot=True, vmin=0, vmax=0.2)	

# parse args to get experiment parameters
parser=argparse.ArgumentParser()
parser.add_argument('count', type=int, help="Number of tags to place on the ceiling.")
parser.add_argument('gridx', type=int, help="Column count of the grid the tags are placed on.")
parser.add_argument('gridy', type=int, help="Row count of the grid the tags are placed on.")
args=parser.parse_args()

#create results folder if it doesn't exist
if not path.exists("./results"):
    makedirs("./results")

# read data
with open("../controllers/heatmap_supervisor/grid_errors.csv") as f:
    dat=[]
    csvreader=csv.reader(f)
    for row in csvreader:
        dat.append([ast.literal_eval(x) for x in row])

## lowest error
# get the lowest error item from each one.
lowesterr_array=[pos[0][0] if len(pos)>0 else np.nan for pos in dat]
heatmap(lowesterr_array, f"Lowest Error, {args.count} tags, {args.gridx}x{args.gridy} grid")
plt.savefig(f"results/{args.count}_{args.gridx}x{args.gridy}_lowest_error.png")

## avg. error
avgerr_array=[np.mean([tags[0] for tags in pos]) for pos in dat]
heatmap(avgerr_array, f"Average Error, {args.count} tags, {args.gridx}x{args.gridy} grid")
plt.savefig(f"results/{args.count}_{args.gridx}x{args.gridy}_avg_error.png")