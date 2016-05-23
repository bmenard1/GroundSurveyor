from distutils.core import setup

setup(
    name='GroundSurveyor',
    version='0.1.0',
    author='Brice Menard',
    author_email='menard@jhu.edu',
    packages=['ground_surveyor'],
    scripts=['bin/compute_pile_statistics.py',
             'bin/mosaic_piles.py',
             'bin/make_piles_of_unit_fields.py'],
    #url='http://pypi.python.org/pypi/GroundSurveyor/',
    url='http://github.com/bmenard1/GroundSurveyor/',
    license='LICENSE.txt',
    description='Deep imagery stack analysis and mosaicing.',
    long_description=open('README.txt').read(),
    install_requires=[
        # Add gdal-python, opencv2, scipy, scipy.signal, scipy.ndimage, numpy
    ],
)
