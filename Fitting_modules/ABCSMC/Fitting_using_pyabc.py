from collections import defaultdict
import random
from multiprocessing.pool import ThreadPool
import time
import os

from pyabc.sampler import ConcurrentFutureSampler
from concurrent.futures import ThreadPoolExecutor

import Tree_simulator_fitting as cts
from Simulate_epidemic_fitting import *
from vector_comparisons import *
from movement_fitting import *


import tempfile
import pyabc

dropbox_path = "/localdisk/home/s1732989/ABM/Fitting/"

results_path = "LTT_ABCSMC/"

#dropbox_path = "/Users/s1743989/VirusEvolution Dropbox/Verity Hill/Agent_based_model/"
#results_path = "Looping models/Results/Fitting/LTT/"

run_number = 1

try:
    os.mkdir(os.path.join(dropbox_path, results_path, str(run_number)))
except FileExistsError:
    pass

observed_SS = get_observed_SS()

new_LTT = list(observed_SS[2])
      
observed = {"a":new_LTT, "b":observed_SS[7], "c":observed_SS[6]}

def distance(x,y): #inputs are the dictionaries
    
   
    new_a_x = np.array(x['a'])
    new_a_y = np.array(y['a'])
    
    if new_a_x.size == new_a_y.size:
        dist_a = np.linalg.norm(new_a_x - new_a_y)
    else:
        dist_a == 1
    
    dist_b = np.linalg.norm(x["b"] - y["b"])
    dist_c = np.linalg.norm(x["c"] - y["c"])
    
    final_b = dist_b/y["b"]
    final_c = dist_c/y["c"]

    dist = dist_a + final_b + final_c
    
    return dist
    


#distance = pyabc.PNormDistance(p=2)

def simulate_pyabc(parameter):
    result = simulate_epidemic(**parameter)
    return {"a":result[0], "b":result[1], "c":result[2]} #so this returns the sample as a dictionary

parameters = dict(a=(0.5,1), b=(0,0.3), c=(0,0.5))

prior = pyabc.Distribution(**{key: pyabc.RV("uniform", a, b - a) for key, (a,b) in parameters.items()})


pool = ThreadPoolExecutor(max_workers=4)
sampler = ConcurrentFutureSampler(pool)

abc = pyabc.ABCSMC(simulate_pyabc, prior, distance, sampler=sampler)

db_path = ("sqlite:///" +
           os.path.join(tempfile.gettempdir(), "results.db"))

abc_id = abc.new(db_path, observed)



history = abc.run(max_nr_populations=10, minimum_epsilon=0.1)
