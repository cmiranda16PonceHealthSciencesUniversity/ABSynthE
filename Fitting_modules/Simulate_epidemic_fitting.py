
from multiprocessing.pool import ThreadPool
from collections import defaultdict

from epidemic_function_fitting import *
import index_functions_fitting

import Tree_simulator_fitting as cts


def simulate_epidemic(a, b, c, LTT, iteration_number_outside, distributions, contact_structure, size_file, district_keys, ch_keys):

    original_dist_mvmt = defaultdict(list)
    original_ch_mvmt = defaultdict(list)

    for pair in district_keys:
        original_dist_mvmt[pair] = []
    
    for pair2 in ch_keys:
        original_ch_mvmt[pair2] = []

    original_case_dict = {}
    original_day_dict = defaultdict(list)
    option_dict_district_level = defaultdict(list)
    infected_individuals_set = set()
    cdf_array = []
    cdf_len_set = set()
    original_trans_dict = defaultdict(list)
    original_child_dict = defaultdict(list)
    original_nodes = []
    original_onset_times = []

    epidemic_length = 148

    for i in range(epidemic_length):
        original_day_dict[i] = []

    capped = True

    result = run_model(a, b, c, LTT, iteration_number_outside, distributions, contact_structure, capped, size_file, original_dist_mvmt, original_ch_mvmt, original_case_dict, original_day_dict, option_dict_district_level, infected_individuals_set, cdf_array, cdf_len_set, original_trans_dict, original_child_dict, original_nodes, original_onset_times)

    return result

def run_model(a, b, c, LTT, iteration_number, distributions, contact_structure, capped, size_file, original_dist_mvmt, original_ch_mvmt, original_case_dict, original_day_dict, option_dict_district_level, infected_individuals_set, cdf_array, cdf_len_set, original_trans_dict, original_child_dict, original_nodes, original_onset_times):
    
    
    case_limit = 10000 #This may not be high enough, so we'll need to check if the epidemics are big enough
    popn_size = 7092142
    epidemic_length = 148
    cfr = 0.7
    sampling_percentage = 0.16
    

    iteration_count = -1
    
    for i in range(iteration_number):
    
    ##Setting things up for running###
        iteration_count += 1
        
        ###Making index case###
        index_case_case, index_case_individual, original_case_dict, original_trans_dict, original_child_dict, original_nodes, infected_individuals_set, original_day_dict = index_functions_fitting.make_index_case(contact_structure[0], cfr, distributions, original_case_dict, original_trans_dict, original_child_dict, original_nodes, infected_individuals_set, original_day_dict)
        
        
        susceptibles_left = True
        
        
        ###Run the epidemic###
        day_dict, case_dict, nodes, trans_dict, child_dict, dist_mvmt, ch_mvmt, onset_times, epidemic_capped = run_epidemic(0, original_day_dict, susceptibles_left , original_case_dict, original_trans_dict, original_child_dict, infected_individuals_set, popn_size, option_dict_district_level, original_onset_times, original_nodes, cdf_len_set, cdf_array, original_dist_mvmt, original_ch_mvmt, contact_structure, cfr, distributions, iteration_count, capped, epidemic_length, case_limit, a, b, c)

        
        remove_set = set()   
    
        ###Removing cases that don't exist eg because the person was already infected, or because the parent had recovered/died###
        for key, value in case_dict.items():
            if type(value) != Individual:
                remove_set.add(key)

        for item in remove_set:
            del case_dict[item]

        #Removing those people from the day dict
        for key, lst in day_dict.items():
            case_list = [item for item in lst if item not in remove_set] 
            day_dict[key] = case_list

        day_dict[0].append(index_case_case) #Put here so that it doesn't confuse the loop above because it has no parent AND otherwise it would get reassigned and stuff

        ###Getting results and writing to file###

        last_day = max(onset_times)
        
        if len(case_dict) > 1800 and len(case_dict) < 2800: #Conditioning to speed up ABC
            
            size = len(case_dict)

            size_file.write(f"{a}, {b}, {c}, {size}\n")

            
            #tree = cts.simulate_tree(trans_dict, child_dict, nodes, sampling_percentage, last_day, LTT)
            
            return dist_mvmt, ch_mvmt


        
        else:
            return

            


