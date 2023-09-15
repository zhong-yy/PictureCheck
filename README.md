# PictureCheck
A tool to manually check pictures in a folder, keeping those you want

# Prerequistes
The following packages are required:
- pyqt5
- pandas
- numpy

First create an empty environment:
```bash
conda create -n picture_select python=3.11
```
Go to the new environment
```bash
conda activate picture_select
```
Install the above packages
```bash
pip install pyqt5
conda install pandas
conda install numpy
```
It is faster to install pyqt using pip than conda.

# Usage
```bash
python picture_selecter.py
```

1. First click on the menu item "Files" to select the input folder that contains pictures you want to inspect. You can also set the output folder to save selected pictures. By default, if you have not set an output folder, a subfolder named "selected_figures" will be created in the input folder to save selected pictures.
2. Click on the "cross" mark to skip pictures you don't want. Click on the "tick" mark to select pitures that meet your requirement. After you select a picture, it will be copied to the output folder. If you regret your decision about a picture, you can use the left arrow in the lower left of the window to go back to the previouse picture, and change your decision with the "cross" or "tick" mark.
3. When you exit the program, a file named "figure_list.csv" is created to record which pistures have been checked. When the same folder is loaded again, the program can start from the point where it existed last time.
   
[Screencast from Friday, September 15, 2023 01:03:27 PM HKT.webm](https://github.com/zhong-yy/PictureCheck/assets/38816011/a2e9e1ba-a890-4af7-9496-0c60b41e262a)







