import glob
import subprocess
import os

# requires imagemagick (brew install imagemagick)

for filepath in sorted(glob.iglob('datasets/blue-toolchest/*.jpg')):
	fileName = os.path.splitext(os.path.basename(filepath))[0]
	print("Silhouetting %s" % (fileName))
	subprocess.run([
            'convert',
            filepath,
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
	print("Vectorizing %s" % (fileName))
	subprocess.run([
    	'potrace',
    	'-s',
    	'out/processed/' + fileName + '.bmp',
    	'-o',
    	'out/svg/' + fileName + '.svg'
    	])
    





