"""
This script is for running the DESI EmFit Code for a given table of sources.
It requires input and output filenames

Author : Ragadeepika Pucha
Version : 2023 April 27
"""

import sys
sys.path.append('/global/cfs/cdirs/desi/users/raga19/repos/DESI_linefitting/py/')
sys.path.append('/global/cfs/cdirs/desi/users/raga19/repos/DESI_Project/py/')

import numpy as np
import emline_fitting as emfit
from astropy.table import Table, vstack
from matplotlib.backends import backend_pdf as pdf

import warnings
warnings.filterwarnings('ignore')

from multiprocessing import Pool, cpu_count
import time

filename = str(sys.argv[1])
outfile = str(sys.argv[2])

start = time.time()

t = Table.read(filename)
num_partitions = cores = cpu_count()

pool = Pool(processes = cores)
inputs = [(obj['SPECPROD'], obj['SURVEY'], obj['PROGRAM'], obj['HEALPIX'], obj['TARGETID'], obj['Z']) for obj in t]
t_final = vstack(pool.starmap(emfit.fit_emline_spectra, inputs))
pool.close()
pool.join()

t_final.write(outfile, overwrite = True)

end = time.time()
print ('Time taken: ', round(end-start, 2), 'sec')


