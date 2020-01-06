iteration_number = 1000
iteration_count = -1

if iteration_count == -1:
    
    print("Successfully importing modules")
    
    import numpy as np
    from scipy import stats
    import scipy as sp
    import math
    import random
    from collections import defaultdict
    import json
    from collections import Counter
    import time
    import os
    import networkx as nx
    
    import Tree_simulator as cts
    
    dropbox_path = "/Users/s1743989/VirusEvolution Dropbox/Verity Hill/Agent_based_model/"
    
    results_path = "Looping models/Results/Playing_with_parameters/Option_A/"
    
    run_number = 6
    
    print("Defining parameters")
    
    os.mkdir(dropbox_path + results_path + str(run_number))
    os.mkdir(dropbox_path + results_path + str(run_number) + "/big_epidemics")
    os.mkdir(dropbox_path + results_path + str(run_number) + "/log_files")
    os.mkdir(dropbox_path + results_path + str(run_number) + "/trees") 
    os.mkdir(dropbox_path + results_path + str(run_number) + "/dist_mvmt")
    os.mkdir(dropbox_path + results_path + str(run_number) + "/skylines")
    
    run_out = open(dropbox_path + results_path + str(run_number) + "/big_epidemics/large_epidemics.csv", 'a')

    run_out.write("Iteration number" + "," + "R0" + "," + "case_number" + "\n")

    R0_output = open(dropbox_path + results_path + str(run_number) + "/R0_run.csv", 'a')
    size_output = open(dropbox_path + results_path + str(run_number) + "/epidemic_size.csv", 'a')


    popn_size = 7092142
    epidemic_length = 126
    cfr = 0.7
    epidemic_runout = 0
    sampling_percentage = 0.16
    
    clinical_x = np.linspace(0, 40, 40)

    incshape = (8.5/7.6)**2
    incscale = (7.6**2)/8.5
    inccdf = sp.stats.gamma.cdf(clinical_x, incshape, loc = 0, scale = incscale)

    death_shape = (8.6/6.9)**2
    death_scale = (6.9**2)/8.6
    death_cdf = sp.stats.gamma.cdf(clinical_x, death_shape, loc = 0, scale = death_scale)

    recovery_shape = (15.2/6.2)**2
    recovery_scale = (6.2**2)/15.2
    recovery_cdf = sp.stats.gamma.cdf(clinical_x, recovery_shape, loc = 0, scale = recovery_scale)

    agent_location = defaultdict(list)
    
    district_list = ["bo", 'bombali', 'bonthe', 'kailahun', 'kambia', 'kenema', 'koinadugu', 'kono', 'moyamba', 'portloko', 'pujehun', 'tonkolili', 'westernarearural', 'westernareaurban']

    print("Importing dictionaries")
    
    with open(dropbox_path + "Contact_structure/agent_location.txt") as json_file:
        data = json.load(json_file)

    for key in data.keys():
        new_key = int(key)
        agent_location[new_key] = data[key]


    with open(dropbox_path + "Contact_structure/District_to_hh.txt") as json_file:
        dist_to_hh = json.load(json_file)

    with open(dropbox_path + "Contact_structure/hh_to_cluster.txt") as json_file:
        hh_to_cluster = json.load(json_file)

    with open(dropbox_path + "Contact_structure/cluster_to_hh.txt") as json_file:
        cluster_to_hh = json.load(json_file)

    with open(dropbox_path + "Contact_structure/Hh_to_people.txt") as json_file:
        hh_to_ppl = json.load(json_file)

    with open(dropbox_path + "Contact_structure/cluster_to_ppl.txt") as json_file:
        cluster_to_ppl = json.load(json_file)

    with open(dropbox_path + "Contact_structure/District_to_ppl.txt") as json_file:
        dist_to_ppl = json.load(json_file)

    with open(dropbox_path + "Contact_structure/district_relative_distance.txt") as json_file:
        district_distance = json.load(json_file)

    district_pops = {}

    with open(dropbox_path + "Contact_structure/district_population.csv", 'r') as f:
        for l in f:
            toks = l.strip("\n").split(",")
            district_pops[toks[0]] = int(toks[1])



    class Individual(): 
        def __init__(self, unique_id): 

            self.unique_id = unique_id

            self.children = []
            self.exptimer = 0
            self.inftimer = 0

            self.hh = agent_location[self.unique_id][0]
            self.comm = agent_location[self.unique_id][1]
            #self.ch = agent_location[self.unique_id][2]
            self.dist = agent_location[self.unique_id][2]

            self.incubation_time()
            self.death_prob()

            if self.death_state == True: 
                self.death_time()
                self.infectious_period = self.death_day + 7
            else:
                self.recovery_time()
                self.infectious_period = self.recovery_day

        def death_prob(self):

            death_poss = np.random.uniform(0, 1.0)

            if death_poss > cfr: #So they are still alive
                self.death_state = False
            else:
                self.death_state = True

            return self.death_state

        def incubation_time(self):

            random_number = random.uniform(0,1)
            self.incubation_day = np.argmax(inccdf > random_number)

            return self.incubation_day

        def death_time(self):

            random_number = random.uniform(0,1)

            self.death_day = np.argmax(death_cdf > random_number)

            return self.death_day

        def recovery_time(self):

            #Can't recover before day 4 - taken from the NEJM paper figure
            random_number = random.uniform(recovery_cdf[3],1)
            self.recovery_day = np.argmax(recovery_cdf > random_number)
            
            return self.recovery_day




    class Case():
        def __init__(self, case_id, level):

            self.children = []

            self.case_id = case_id

            self.level = level

            #print("case ID " + str(self.case_id) + " is level " + str(self.level))

            if self.case_id != 0 and self.level == None:
                print("ERROR " + str(self.case_id))



    def initialise_case(focal_case, level): #parent as a case object
        """ Takes current individual who is doing the infecting as a case object input
        Makes case objects for new cases and adds to the case dictionary"""

        new_case = Case(len(case_dict), level)

        new_case.parent = focal_case

        case_dict[new_case] = None
        #case_dictall[new_case.case_id] = None

        return new_case


    def get_possible_cases(individual):
        """Finds number of people exposed with their contact level relative to focal_individual"""
        poss_contact_dict = {}

        function = np.random.poisson

        lamb = 0.65

        a = 1
        b = 1
        c = 0.07

        Hh_number = function(lamb)
        comm_number = function(a*lamb)
        dist_number = function(b*lamb)
        country_number = function(c*lamb)

        if Hh_number != None:
            poss_contact_dict["Hh"] = Hh_number
        else:
            poss_contact_dict["Hh"] = 0

        if comm_number != None:
            poss_contact_dict["Comm"] = comm_number
        else:
            poss_contact_dict["Comm"] = 0

        if dist_number != None:
            poss_contact_dict["Dist"] = dist_number
        else:
            poss_contact_dict["Dist"] = 0

        if country_number != None:
            poss_contact_dict["Country"] = country_number
        else:
            poss_contact_dict["Country"] = 0

        return poss_contact_dict  


    def get_cdf(dim):

        x = np.linspace(0,dim, dim) #This is where difference between living/dead comes in
        mu = 3.1
        sigma = 2.5

        a = shape = (mu/sigma)**2
        scale = (sigma**2)/mu

        cdf = sp.stats.gamma.cdf(x,a,loc=0,scale=scale)

        return cdf


    def when_infected(focal_ind, current_day, possible_case):

        if focal_ind.infectious_period not in cdf_len_set:
            cdf = get_cdf(focal_ind.infectious_period)
            cdf_array.append(cdf)
            cdf_len_set.add(focal_ind.infectious_period)
        else:
            for item in cdf_array:
                if focal_ind.infectious_period == len(item):
                    cdf = item

        random_number = random.uniform(0,1)

        try:
            day = np.argmax(cdf > random_number)

            try:
                day_inf = day + current_day + focal_ind.incubation_day
                return day_inf
            except TypeError:
                return "done"
            
        except ValueError:
            return None


    def get_options_district():

        if parent.comm not in option_dict_districtlevel.keys():

            poss_comms = [hh_to_cluster[hh] for hh in dist_to_hh[parent.dist]]

            dist_ppl_list = ([cluster_to_ppl[clust] for clust in poss_comms if clust != parent.comm])

            option_dict_districtlevel[parent.comm] = dist_ppl_list

        else:

            dist_ppl_list = option_dict_districtlevel[parent.comm]

        return(dist_ppl_list)



    def who_am_I(focal_case): #input is case object - already been initialised
        """Input is case object that has already been initialised.
        Finds out which of the parent's potential contacts are still susceptible"""

        if len(infected_individuals_set) == popn_size: 
            return False

        if focal_case.level == "Hh":
            poss_case = random.choice(hh_to_ppl[parent.hh])

        elif focal_case.level == "Comm":
            poss_case = random.choice(random.choice([hh_to_ppl[hh] for hh in cluster_to_hh[parent.comm] 
                                                if hh != parent.hh]))
          

        elif focal_case.level == "Dist":
            #Tried to optimise this but have left for now
            dist_ppl_list = get_options_district()

            poss_case = random.choice(random.choice(dist_ppl_list))

        elif focal_case.level == "Country":        

            district = random.choice(district_distance[parent.dist])

            poss_case = random.choice(dist_to_ppl[district])

        else:
            print("ERROR no level assigned")


        #Is the person actually susceptible
        if poss_case not in infected_individuals_set:
            new_individual = Individual(poss_case)
            case_dict[focal_case] = new_individual
            infected_individuals_set.add(poss_case)

        else:
            #print("Already infected")
            return

        #print("Time taken to define self = " + str(end-start))
        return(poss_case)



    # ### Results functions


    def simulator_output(R0_output, size_output):
        
        edge_list = []
        case_list = []

        for pair in pair_list:
            case = pair[0].unique_id
            parent = pair[1].unique_id

            edge_list.append((parent,case))
            case_list.append(case)

        G = nx.Graph()

        G.add_nodes_from(case_list)
        G.add_edges_from(edge_list)

        nedges = G.number_of_edges()

        nvertices = G.number_of_nodes()


        try:
            average_degree = nedges/nvertices
        except ZeroDivisionError:
            average_degree = 0.0
            #print("Average R0 = " + str(mean))
        
        R0_output.write(str(average_degree) + "\n")

        size_output.write(str(len(case_dict)) + "," + str(len(districts_present)) + "," + str(len(cluster_set)) + "\n")


        return str(average_degree)

   
        
for i in range(iteration_number):
       
    iteration_count += 1

    if iteration_count%100 == 0:
        write_file = True
    else:
        write_file = False
      
    if iteration_count%100 == 0:
        print(str(iteration_count) + " runs completed")

    dist_mvmt = defaultdict(list)
        
    for item1 in district_list:
        for item2 in district_list:
            if item1 != item2:
                dist_mvmt[item1,item2] = []
        
    case_dict = {}
    day_dict = defaultdict(list)
    day_dictall = defaultdict(list)

    option_dict_countrylevel = defaultdict(list)
    option_dict_districtlevel = defaultdict(list)

    infected_individuals_set = set()
    parent_list = []
    remove_set = set()

    cdf_array = []
    cdf_len_set = set()
    
    districts_present = []
    cluster_set = set()
    
    pair_list = []
    
    trans_dict = defaultdict(list)
    nodes = []

    index_case_individual = Individual(random.choice(range(1382431,1908832))) #These should be the IDs of the range in Kailahun

    index_case_individual.incubation_day = 0 #So that the first case is infectious on day one of the simulation
             
    index_case_case = Case(0, None)
    index_case_case.parent = None
    case_dict[index_case_case] = index_case_individual
    
    trans_dict[index_case_individual.unique_id] = ["NA", '0', index_case_individual.incubation_day]
    nodes.append(index_case_individual.unique_id)

    infected_individuals_set.add(index_case_individual.unique_id)
    
    districts_present.append(index_case_individual.dist)

    cluster_set.add(index_case_individual.comm)

    if write_file == True:
        
        info_file = open(dropbox_path + results_path + str(run_number) + "/log_files/information_file_for_" + str(iteration_count) + ".csv", 'w')
        
        tree_file = open(dropbox_path + results_path + str(run_number) + "/trees/tree_for_" + str(iteration_count) + ".txt", 'w')
        
        district_mvmt_file = open(dropbox_path + results_path + str(run_number) + "/dist_mvmt/mvmt_for_" + str(iteration_count) + ".csv", 'w')
             
        skyline_file = open(dropbox_path + results_path + str(run_number) + "/skylines/skyline_for_" + str(iteration_count) + ".csv", 'w')
             
        skyline_file.write("number" + ","
                           + "start_interval" + ","
                           + "end_interval" + ","
                           + "logpopize" + "\n")

        district_mvmt_file.write("DistrictOne" + ","
                                 + "DistrictTwo" + ","
                                 + "Times" + "\n")
        
        info_file.write("Individual" + "," 
                        + "Parent" + "," 
                        + "Household" + ","
                        + "District" + ","
                        + "Day_infected" + ","
                        + "Day_onset" + "," 
                        + "Day_sampled" +
                        "\n")


        info_file.write(str(index_case_individual.unique_id) + "," 
                        + "NA" + ","
                        + str(index_case_individual.hh) + "," 
                        + str(index_case_individual.dist) + ","
                        + str(0) + ","
                        + str(index_case_individual.incubation_day) + ","
                        + str(index_case_individual.incubation_day) +
                        "\n")


    for i in range(epidemic_length):
        day_dict[i] = []

    count_removers = 0
    count_lastday = 0

    loop_one = True
    last_day = False

    stop_loop = False
    
    runout = False
    
    too_large = False

    ###############################################################

    poss_case_dict = get_possible_cases(index_case_individual)

    #print(poss_case_dict)

    for level, number in poss_case_dict.items():
        for person in range(number):
            day_inf = when_infected(index_case_individual, 0, person)
            if not day_inf: #if not day_inf: #if day_inf == None 
                pass
            else:
                new_case = initialise_case(index_case_case, level)
                day_dict[day_inf].append(new_case)
                #print("Case ID " + str(new_case.case_id) + " should be level " + str(new_case.level))

    #start = time.time()

    count = 0
    
    
    try:
        for day, case_list in day_dict.items():
            #print(day, case_list)
            if stop_loop == True: #When everyone has been infected
                break
            count += 1
            if count > epidemic_length:
                #print(count)
                print("Epidemic ran out of time in " + str(iteration_count))
                epidemic_runout += 1
                too_long = True
                break
            if len(case_dict) > 500000: #to stop it getting huge - try this and see! May skew too much
                print("broke the loop - too large")
                too_large = True
                break
            #if count % 50 == 0:
             #   print(str(count) + " iterations done")
            if len(case_list) != 0: #If there are new cases on this day
                for focal_case in case_list: 
                    if loop_one == True:

                        parent = case_dict[focal_case.parent]#Gets the individual object of parent (intialised last time) from the case dictionary using the case id

                        assignment = who_am_I(focal_case) #Assign the current case id to an individual

                        if assignment == None: #If individual is already infected
                            remove_set.add(focal_case) #Case doesn't exist so must be removed from day/case dicts

                        elif assignment == False: #If there is no-one left
                            print("All members of the population infected")
                            last_day = day
                            print("last day = " + str(last_day))
                            if case_dict[c] == None:
                                count_lastday += 1
                                remove_set.add(focal_case)
                            loop_one = False

                        else: #There is a successful assignation to a specific individual

                            focal_individual = case_dict[focal_case] #This is an Individual object got by who_am_I

                            focal_individual.parent = parent #Gives Individual the same parent as the Case object for recording

                            pair = (focal_individual, focal_individual.parent)
                            
                            pair_list.append(pair)
                        
                            parent.children.append(focal_individual)
                            
                            trans_dict[focal_individual.unique_id] = [focal_individual.parent.unique_id, day, (day+ focal_individual.incubation_day)]
                            
                            nodes.append(focal_individual.unique_id)
                            
                            if write_file == True:
                                info_file.write(str(focal_individual.unique_id) + "," + 
                                                str(focal_individual.parent.unique_id) +  "," +
                                                str(focal_individual.hh) +  "," +
                                                str(focal_individual.dist) + "," +
                                                str(day) + "," +
                                                str(day + focal_individual.incubation_day) + "," +
                                                str(day + focal_individual.incubation_day) +
                                                "\n")
                                
                                if focal_individual.dist != focal_individual.parent.dist:
                                    dist_mvmt[focal_individual.dist,focal_individual.parent.dist].append(day)
                                

                            if focal_individual.dist not in districts_present:
                                districts_present.append(focal_individual.dist)
                        
                            if focal_individual.comm not in cluster_set:
                                cluster_set.add(focal_individual.comm)
                            
                            poss_case_dict = get_possible_cases(focal_individual) #Gives dict of contact_level: number of people

                            for level, number in poss_case_dict.items():
                                for person in range(number):
                                    day_inf_output = when_infected(focal_individual, day, person)

                                    if day_inf_output == None:
                                        #print("Finished infection first")
                                        pass

                                    elif day_inf_output > epidemic_length:
                                        #print("Epidemic days have finished")
                                        runout = True

                                    else:
                                        new_case = initialise_case(focal_case, level)
                                        day_dict[day_inf_output].append(new_case)

                    elif loop_one == False: #To remove some extra people at the end of the epidemic if the whole pop has been infected
                        if case_dict[focal_case] == None:
                            remove_set.add(focal_case)

    except RuntimeError:
        #print("RuntimeError in iteration " + str(iteration_count))
        runout = True

        #Removing cases that don't exist eg because the person was already infected, or because the parent had recovered/died

        
        for key, value in case_dict.items():
            if type(value) != Individual:
                remove_set.add(key)

    for item in remove_set:
        del case_dict[item]

    #Removing those people from the day dict
    #This bit could be quite slow if it's a big epidemic, but it only happens once per run.
    #Could maybe try and get day from above (store day when assignment comes back as none) and then lookup rather than loop 
    for key, lst in day_dict.items():
        case_list = [item for item in lst if item not in remove_set] 
        day_dict[key] = case_list



    day_dict[0] = [index_case_case] #Put here so that it doesn't confuse the loop above because it has no parent
    
    if runout == True:
        
        tree_file = open(dropbox_path + results_path + str(run_number) + "/trees/tree_for_" + str(iteration_count) + ".txt", 'w')
        
        district_mvmt_file = open(dropbox_path + results_path + str(run_number) + "/dist_mvmt/mvmt_for_" + str(iteration_count) + ".csv", 'w')
        
        runout_info = open(dropbox_path + results_path + str(run_number) + "/big_epidemics/log_for_" + str(iteration_count) + ".csv", 'w')
        
        skyline_file = open(dropbox_path + results_path + str(run_number) + "/skylines/skyline_for_" + str(iteration_count) + ".csv", 'w')
             
        skyline_file.write("number" + ","
                           + "start_interval" + ","
                           + "end_interval" + ","
                           + "logpopize" + "\n")

        district_mvmt_file.write("DistrictOne" + ","
                                 + "DistrictTwo" + ","
                                 + "Times" + "\n")
        
        
        
        runout_info.write("Individual" + "," 
            + "Parent" + "," 
            + "Household" + ","
            + "District" + ","
            + "Day_infected" + ","
            + "Day_onset" + "," 
            + "Day_sampled" +
            "\n")
       
        
        for indie in case_dict.values():
            
            day = trans_dict[indie.unique_id][1]
            symptoms = trans_dict[indie.unique_id][2]
            sampled = trans_dict[indie.unique_id][2]

            try:
                runout_info.write(str(indie.unique_id) + "," + 
                        str(indie.parent.unique_id) +  "," +
                        str(indie.hh) +  "," +
                        str(indie.dist) + "," +
                        str(day) + "," +
                        str(symptoms) + "," +
                        str(sampled) +
                        "\n")
            except AttributeError:
                runout_info.write(str(indie.unique_id) + "," + 
                        "NA" +  "," +
                        str(indie.hh) +  "," +
                        str(indie.dist) + "," +
                        str(day) + "," +
                        str(symptoms) + "," +
                        str(sampled) +
                        "\n")
           


    if write_file == True or runout == True:
        
        for key, value in dist_mvmt.items():
            if len(value) != 0:
                district_mvmt_file.write(key[0] + "," + key[1] + "," + ",".join([str(i) for i in value]) + "\n")
       
        district_mvmt_file.close()
        
        result = cts.simulate_tree(trans_dict, nodes, sampling_percentage)
        
        if result:
            newick_string = result[0]
            skyline = result[1]

            tree_file.write(newick_string)

            tree_file.close()

            logpop_count = 0
            start_interval = 0.0
            for key, value in skyline.items():
                logpop_count += 1
                skyline_file.write(str(count) + ","
                                  + str(start_interval) + ","
                                  + str(key) + ","
                                  + str(value) + "\n")

                start_interval = key

            skyline_file.close()
        
        if write_file == True:
                     
            info_file.close()
    
    R0 = simulator_output(R0_output, size_output)
    
    if runout == True:
        run_out.write(str(iteration_count) + "," + R0 + "," + str(len(case_dict)) + "\n")
    
    if too_large == True:
        too_big.write(str(iteration_number) + "," + R0 + "," + str(len(day_dict)) + "\n")


    if len(case_dict) == popn_size:
        print("Whole population infected in " + str(last_day))


R0_output.close()
size_output.close()
run_out.close()
    
    



