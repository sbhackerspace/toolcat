import glob
import subprocess
import os
import argparse
import numpy as np
import math
from matplotlib import pylab as plt

# requires imagemagick (brew install imagemagick)

def autoRotate(imagePath, axisPreference='horizontal'):
    image = plt.imread(imagePath)
    #convert to grayscale
    image = np.dot(image[...,:3], [0.299, 0.587, 0.114])
    #get XY coordinates of black pixels
    points = np.argwhere(image.T < 255)

    #get normalized values 
    normalization_offset = (np.average(points[:,0]), np.average(points[:,1]))
    normalized_points = np.array([points[:,0] - normalization_offset[0], points[:,1] - normalization_offset[1]]).transpose()
    x = normalized_points[:,0]
    y = normalized_points[:,1]

    #get eigenvectors to represent major and minor axes of tool
    (eigenvalues, eigenvectors) = np.linalg.eigh(np.cov([x,y]))
    
    #find major axis of part
    major_eigenvector = eigenvectors[0]
    if eigenvalues[0] < eigenvalues[1]:
        major_eigenvector = eigenvectors[1]

    #compute theta from eigenvectors
    rot_radians = math.atan2(major_eigenvector[1],major_eigenvector[0])
    rot_degrees = rot_radians * ( 180 / math.pi)
    if axisPreference == 'vertical':
        rot_degrees += 90
    elif axisPreference != 'horizontal':
    	print("Incorrect option")
    	return
    return rot_degrees

def pipeline(path, scalingFactor=1.0):
	fileName = os.path.splitext(os.path.basename(path))[0]
	print("Silhouetting %s" % (fileName))
	subprocess.run([
            'convert',
            path,
            # downsample, make grayscale, select all channels (used for open/close I think)
            '-resize','25%','-grayscale','Rec709Luma','-channel','RGB',
            # threshold
            '-threshold','20%',
            # invert (want object white not black
            '-negate',
            # close gaps between allen key legs
            '-morphology','Close','Disk:6.5',
            # set options for future -connected-components so objects smaller than some pixel count get merged into outer/neighbor object
            '-define','connected-components:area-threshold=400',
            # number pixels doing flood fill from one corner into connected objects
            '-connected-components','4',
            # make black first two found objects (should be outside, then lightbox, everything else disappear)
            '-threshold','1',
            #invert image for SVG processing
            '-negate',
            os.path.join('out/processed', fileName + '.bmp')])

	rotationTheta = autoRotate(os.path.join('out/processed', fileName + '.bmp'), axisPreference='vertical')
	print("roation: %s" %  rotationTheta)
	print("Vectorizing %s" % (fileName))
	subprocess.run([
    	'potrace',
    	'--rotate',
    	str(rotationTheta),
    	'--resolution',
    	str(72*11.428/12), # apply scaling factor to expected DPI so SVG units are physical units
    	'-s',
    	'out/processed/' + fileName + '.bmp',
    	'-o',
    	'out/svg/' + fileName + '.svg'
    	])
	def calibrate():
		pass


def main():
	#pipeline('datasets/blue-toolchest/3-12-in-ruller.jpg')
	#return

	if os.path.isfile('dataset/blue-toolchest/cal.jpg'):
		calibrate()
	for filepath in sorted(glob.iglob('datasets/blue-toolchest/*.jpg')):
		pipeline(filepath)


if __name__ == "__main__":
    main()

