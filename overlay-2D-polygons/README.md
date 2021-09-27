=== Overlay results from your trained Zendo task onto images

This script takes a directory of images & json file pairs, where the json file contains the inferences results for that image, and outputs a folder of images with the inference results from Zendo overlayed on each image.

This script requires "opencv-python" pip package and python3.

run the following cmd and replace DIRECTORY_NAME with the location of your directory containing images & json file pariings.

python3.9 zendo_video_overlay_visualize_on_frames.py DIRECTORY_NAME
