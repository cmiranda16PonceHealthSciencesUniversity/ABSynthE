from collections import defaultdict
import random

from tree_class_fitting import *
from node_class_fitting import *


def sampling(trans_dict, sampled_percentage, epidemic_len): 
    """Get who is sampled, inputs are list of individual ids and the sampled percentage"""
    not_enough_cases = False
    week_bins = []
    weeks_cases = defaultdict(list)
    those_sampled = set()
    
    total = len(trans_dict) #Doesn't have NA in it because that can't be sampled
    
    number_of_people = round(total*sampled_percentage)
    
    those_sampled = set(random.sample(trans_dict.keys(), k = number_of_people))

    #weeks = round(epidemic_len/7)

    #if weeks > 0:
     #   samples_per_week = round(number_of_people/weeks)
    #else:
     #   return

    #if samples_per_week < 1:
     #   not_enough_cases = True
      #  return 


    #for i in range(weeks):
     #   weeks_cases[i] = []

    #week_bins[len(week_bins) - 1] = (140,148)
    #Leaving this out because it's a specific conditioning on the long epidemics. Can put back in when needed


    #for key,value in trans_dict.items():
     #   date_sampled = value[2]
      #  week_number = int(date_sampled/7)
       # weeks_cases[week_number].append(key)

    #if len(weeks_cases[(140,148)]) == 0:
     #   not_enough_cases = True
      #  return

   # for week, lst in weeks_cases.items():
    #    if len(lst) >= samples_per_week:
     #       for i in random.sample(lst, k=samples_per_week):
      #          those_sampled.add(i)

    #more_needed = number_of_people - len(those_sampled)

    #if more_needed > 0:
     #   try:
      #      for i in random.sample(trans_dict.keys(), k=more_needed):
       #         those_sampled.add(i)
       # except ValueError:
        #    not_enough_cases = True
         #   return 

    
    return those_sampled

def get_R0(node_dict):
    """Count number of people in 4th and 3rd generations to calculate R0"""
    
    gen_3 = 0
    gen_4 = 0
    
    for nde in node_dict.values():
        
        if nde.generation == 3:
            gen_3 += 1
            gen_4 += len(nde.infections)
            
    if gen_3 != 0 and gen_4 != 0:
        R0 = gen_4/gen_3
    
        return R0

def plot_skyline(Ne_dict):

    for_plotting = {}
    
    for key, value in Ne_dict.items():
        
        new_key = key*-1
        
        for_plotting[new_key] = value

    names = list(for_plotting.keys())
    values = list(for_plotting.values())

    plt.step(names,values)


def simulate_tree(trans_dict, child_dict, nodes, sampling_proportion, epidemic_len, LTT): 
    """Function to simulate a coalescent tree"""
            
    sampling_output = sampling(trans_dict, sampling_proportion, epidemic_len)
    
    if not sampling_output:
        not_enough_cases = sampling_output
        print("triggered not enough cases")
        return
    else:
        those_sampled = sampling_output
        

    
    if len(those_sampled) != 0:
    
        node_dict = {}
   
        #Intialise as type individual nodes, make transmission tree and make subtrees
        
        index_case = child_dict["NA"][0]
        
        node(index_case, "Ind", trans_dict=trans_dict, child_dict=child_dict, those_sampled=those_sampled, node_dict=node_dict)
            
        coalescent_tree = tree.tree(node_dict=node_dict, epidemic_len=epidemic_len)

        if LTT:
            
            coalescent_tree.get_active_population()
  
            return coalescent_tree
        
        else:
            
            return coalescent_tree
       
    else:
        print("triggered here")
        return

