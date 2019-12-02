# Sprout

Sprout is an application that utilizes image processing techniques to study bamboo's structural integrity by determining its fiber density. The app makes dimensional measurements based on a scanned bamboo cross-section and counts the number of fibers to determine the fiber density and distribution of the sample. Results are presented in a tabular format and visualized through graphs. 

Sprout uses OpenCV to perform all image processing techniques needed to make measurements and study the input image. It also has a User Interface (UI) that was designed using PyQt5. 

The application is capable of measuring:
  - inner and outer diameter of the bamboo
  - bamboo surface area
  - centroid of the bamboo
  - moments of inertia of the sample
  - product of inertia
  - fiber density across the ring
  
Bamboo samples can be divided from 1 to 25 rings and 12 to 400 wedges.

Suported input image formats are: jpg, jpeg, tif, bmp.
Supported input image DPI's are from 1200 to 4800 dpi.

To launch the application, use Python 3.7, install all the dependecnies in requirements.txt, and launch Sprout.py.

**Creating an Executable**

To create an executable, install pyinstaller on your computer and run the following command:
> pyinstaller <Directory>\Sprout.py -i <Directory>\Images\Sprout.ico --hidden-import Pillow.Image --windowed
  
This will package all the dependencies of Sprout and the source code in an executable which will allow you to distribute the program more easily.

After running this command, copy Sprout.ui and SproutSave.ui to the main folder of the executable.
Then create a folder "Images" in the main folder of the executable and copy LoadingImage.png, RingsWedgesRegions.png, Sprout Logo.png, and SproutIcon.ico to the newly created "Images" folder.

Then launch Sprout.exe
