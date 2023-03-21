import csv
import numpy as np
from matplotlib import use
use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import argparse
from os import path, makedirs, stat
import yaml

with open('../controllers/geometric_posest/params.yaml') as f:
	loadedparams = yaml.safe_load(f)
grid_shape = (loadedparams.get('grid_x'), loadedparams.get('grid_y'))
print("grid_shape: ", grid_shape)

def savescore(score):
	csv_headers=["TAGCOUNT","GRIDX","GRIDY","TAGSIZE","SCORE"]
	with open('scores.csv', 'a', newline='') as f:
		csvw=csv.writer(f)
		
		#write the column headers if the file is empty.
		needs_header = stat('scores.csv').st_size == 0
		if needs_header:
			csvw.writerow(csv_headers)
		
		#add new round of scores
		csvw.writerow([args.count, args.gridx, args.gridy, args.size, score])

def heatmap(arr, title,ax,*args):
	maxval = args[0] if len(args)>0 else 0.2
	mat=np.reshape(arr, grid_shape)
	mat=mat.transpose()
	# change ordering so the plots make sense spatially
	mat=mat[::1,::-1]  
	if ax is None:
		fig=plt.figure(figsize=grid_shape)
		fig.suptitle(title)
		sns.heatmap(mat, cmap='coolwarm', annot=True, vmin=0, vmax=maxval)	
	else:		
		ax.set_title(title)
		sns.heatmap(mat, cmap='coolwarm', annot=True, vmin=0, vmax=maxval, ax=ax)
# parse args to get experiment parameters
parser=argparse.ArgumentParser()
parser.add_argument('count', type=int, help="Number of tags to place on the ceiling.")
parser.add_argument('gridx', type=int, help="Column count of the grid the tags are placed on.")
parser.add_argument('gridy', type=int, help="Row count of the grid the tags are placed on.")
parser.add_argument('size', type=int, help="Size of the aruco marker.")
args=parser.parse_args()

#create results folder if it doesn't exist
if not path.exists("./results"):
    makedirs("./results")
if not path.exists(f"./results/tag{args.size}"):
	makedirs(f"./results/tag{args.size}")

# read data
with open("../controllers/geometric_posest/grid_errors.csv") as f:
    dat=[]
    csvreader=csv.reader(f)
    for row in csvreader:
        dat.append([ast.literal_eval(x) for x in row])


#Create a figure with 3 subplots
fig, axs=plt.subplots(3, 1, figsize=(grid_shape[0], grid_shape[1]*3))
lowesterr_array=[pos[0][0] if len(pos)>0 else np.nan for pos in dat]
heatmap(lowesterr_array, f"Lowest Error, {args.count} tags, {args.gridx}x{args.gridy} grid, {args.size} cm", axs[0])
avgerr_array=[np.mean([tags[0] for tags in pos]) for pos in dat]
heatmap(avgerr_array, f"Average Error, {args.count} tags, {args.gridx}x{args.gridy} grid, {args.size} cm", axs[1])
numtags_array=[len(pos) for pos in dat]
heatmap(numtags_array, f"Number of Tags, {args.count} tags, {args.gridx}x{args.gridy} grid, {args.size} cm", axs[2], max(numtags_array))
plt.savefig(f"results/tag{args.size}/subplot{args.count}_{args.gridx}x{args.gridy}_heatmap.png")

## lowest error
# get the lowest error item from each one.
heatmap(lowesterr_array, f"Lowest Error, {args.count} tags, {args.gridx}x{args.gridy} grid, {args.size} cm", None)
plt.savefig(f"results/tag{args.size}/{args.count}_{args.gridx}x{args.gridy}_lowest_error.png")

## avg. error
heatmap(avgerr_array, f"Average Error, {args.count} tags, {args.gridx}x{args.gridy} grid, {args.size} cm", None)
plt.savefig(f"results/tag{args.size}/{args.count}_{args.gridx}x{args.gridy}_avg_error.png")

## number of tags
numtags_array=[len(pos) for pos in dat]
heatmap(numtags_array, f"Number of Tags, {args.count} tags, {args.gridx}x{args.gridy} grid, {args.size} cm", None, max(numtags_array))
plt.savefig(f"results/tag{args.size}/{args.count}_{args.gridx}x{args.gridy}_num_tags.png")

## compute a score
# for now, the average of all average errors, ignore nan
score=np.nanmean(avgerr_array)
# save to csv file
savescore(score)
# print score
print(f"SCORE {score}")
