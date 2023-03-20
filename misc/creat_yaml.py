import argparse
import yaml

argparser = argparse.ArgumentParser()
argparser.add_argument("--grid_size", type=int, default=100, help="Distance between grid points in cm")
argparser.add_argument("--rotation", type = float, default=0, help="Rotation of the camera in radians")
args = argparser.parse_args()
print(args)
grid_size = args.grid_size
rotation = args.rotation
with open("../controllers/geometric_posest/params.yaml", "w") as f:
    yaml.dump({"grid_size": grid_size, "rotation": rotation}, f)
