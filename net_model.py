# -*- coding: utf-8 -*-
"""
This module defines a class called network

Created on Tue Dec 24 15:27:57 2013

@author: xuanliu
"""

import model_create_debug as mc
#from copy import deepcopy
from optparse import OptionParser
import dc_placemt
import sys
import math
#import random

class network(object):
    """
    Define a network class
    """
    def __init__(self):
        """ 
        initialize the model 
        topo_type: random/ring/grid/full/rocketfuel
        dc_type: none('n')/adjacent('a')/far('f')
        load_type: uniform('u')/random('r')/
        """
        self.num_nodes = 0
        self.topo_type = ''
        self.d_pairs = []
        self.path_dict = {}
        self.links = {}
        self.dc_type = 'n'
        self.load_type = 'uniform'
        self.is_bin = 'no'
        self.num_paths = 0
        self.cost_type = 'byhops'
        self.dc_tuple = ()

    def set_topo(self, topo_type):
        ''' set topology type '''
        self.topo_type = topo_type
    
    def set_num_nodes(self, num_nodes):
        ''' set the number of nodes in the network '''
        self.num_nodes = num_nodes
            
    def set_dc_type(self,dc_type):
        ''' set whether and where to place the data centers '''
        self.dc_type = dc_type
    
    def set_d_type(self, load_type):
        ''' set the demand type '''
        self.load_type = load_type
    
    def set_bin(self):
        ''' specify if it's a binary variable '''
        self.is_bin = 'yes'
    
    def set_num_path(self, num_p):
        ''' set the number of paths for each demand pair '''
        self.num_paths = num_p

    def set_cost_type(self,c_type):
        ''' set the cost type for the objective equation '''
        self.cost_type = c_type
        
    def get_paths(self, path_lib):
        ''' get path dictionary '''
        self.num_nodes, self.path_dict = mc.parse_file(path_lib)
    
    def get_links(self, weight_csv):
        ''' get link_dictionary '''
        self.links = mc.get_links(weight_csv)
        
    def get_all_demands(self):
        self.d_pairs = self.path_dict.keys()
            
    def get_dc_nodes(self):
        """
        get the nodes where the data centers should be placed
        Assume two datacenters will be placed in the network
        """
        dc_x, dc_y = dc_placemt.dc_nodes(self.path_dict, 
                                         self.num_nodes, 
                                         self.dc_type, 
                                         self.topo_type)
        print "x", dc_x, "y", dc_y
        self.dc_tuple = (dc_x, dc_y)
        
    
    def get_dmdpair(self):
        """
        this function returns a list of demand pairs that are from all nodes 
        in the network to the data center nodes
        """
        dc_x, dc_y = self.dc_tuple
        nodes = range(1, self.num_nodes + 1)
        dmd_pairs = []
        for node_id in nodes:
            if node_id != dc_x and node_id != dc_y:
                dmd_pairs.append((min(node_id, dc_x), max(node_id, dc_x)))
                dmd_pairs.append((min(node_id, dc_y), max(node_id, dc_y)))
        return dmd_pairs
        
    def get_special_dpair(self):
        """
        get special demand pair based on the topo_type (ring/topo), 
        load_type and dc_type
        """
        
        if self.topo_type == 'ring':
            if self.dc_type == 'n':
                if self.load_type == 'uniforme1n' or \
                    self.load_type == 'nonuniforme1n':
                    return (1, self.num_nodes)
                elif self.load_type == 'uniformeij' or \
                    self.load_type == 'nonuniformeij':
                    d_dst = self.num_nodes / 2
                    return (1, d_dst)
            else:
                dc_x, dc_y = self.dc_tuple
                d_src = min([dc_x, dc_y])
                other_dc = max([dc_x, dc_y])
                if self.num_nodes == 3:
                    # special case: three-node ring topology
                    d_dst = 6 - dc_x - dc_y
                    return d_src, d_dst
                print "d_src", d_src
                if self.dc_type == 'a':  
                    if self.load_type == 'uniforme1n' or \
                        self.load_type == 'nonuniforme1n':
                        d_dst = (d_src - 1) % self.num_nodes
                        if d_dst == 0 and d_dst != other_dc % self.num_nodes:
                            d_dst = self.num_nodes
                        elif d_dst == other_dc % self.num_nodes:
                            d_dst = (d_src + 1)
                        print "d_src, d_dst", d_src, d_dst
                        return (d_src, d_dst)
                    elif self.load_type == 'uniformeij' or \
                        self.load_type == 'nonuniformeij':
                        d_dst = (self.num_nodes / 2 + d_src ) % self.num_nodes
                        if d_dst == 0:
                            d_dst = self.num_nodes
                        return (d_src, d_dst)
                elif self.dc_type == 'f':
                    if self.load_type == 'uniforme1n' or \
                        self.load_type == 'nonuniforme1n':
                        d_dst = (d_src - 1) % self.num_nodes
                        if d_dst == 0 and d_dst != other_dc % self.num_nodes:
                            d_dst = self.num_nodes
                        elif d_dst == other_dc % self.num_nodes:
                            d_dst = (d_src + 1)
                        return (d_src, d_dst)
                    elif self.load_type == 'uniformeij' or \
                        self.load_type == 'nonuniformeij':
                        d_dst =(max(dc_x, dc_y) + 1) % self.num_nodes
                        if d_dst == 0:
                            d_dst = self.num_nodes
                        return (d_src, d_dst)

        if self.topo_type == 'grid':
            if self.dc_type == 'n':
                if self.load_type == 'uniforme1n' or \
                    self.load_type == 'nonuniforme1n':
                    return (1, 2)
                elif self.load_type == 'uniformeij' or \
                    self.load_type == 'nonuniformeij':
                    return (1, self.num_nodes)
            else:
                dc_x, dc_y = self.dc_tuple
                d_src = min([dc_x, dc_y])
                if self.dc_type == 's':
                    # two data centers are adjacent on the side
                    diff = abs(dc_y - dc_x)
                    if self.load_type == 'uniforme1n' or \
                        self.load_type == 'nonuniforme1n':
                        d_dst = (d_src - diff) % self.num_nodes
                        #return (d_src, d_dst)
                    elif self.load_type == 'uniformeij' or \
                        self.load_type == 'nonuniformeij':
                        if d_src % math.sqrt(self.num_nodes) == 1:
                            if d_src - 1 <= math.sqrt(self.num_nodes)/2:
                                # on the top left side
                                d_dst = self.num_nodes
                                #return (d_src, d_dst)
                            else:
                                # on the bottom left side
                                d_dst = math.sqrt(self.num_nodes)
                            #return (d_src, d_dst)
                        elif d_src % math.sqrt(self.num_nodes) == 0:
                            if d_src <= self.num_nodes / 2:
                                # on the top right side
                                d_dst = self.num_nodes - math.sqrt(self.num_nodes) + 1
                                #return (d_src, d_dst)
                            else:
                                # on the bottom right side
                                d_dst = 1
                            #return (d_src, d_dst)
                        else:
                            # on the top/bottom side
                            if d_src <= math.sqrt(self.num_nodes) / 2:
                                # on the left half of top side
                                d_dst = self.num_nodes
                            elif d_src < math.sqrt(self.num_nodes):
                                # on the right half of top side
                                d_dst = self.num_nodes - math.sqrt(self.num_nodes) + 1
                            elif d_src % math.sqrt(self.num_nodes) <= \
                                    math.sqrt(self.num_nodes) / 2:
                                # on the left half of bottom side
                                d_dst = math.sqrt(self.num_nodes)
                            else:
                                # on the right half of bottom side
                                d_dst = 1
                    return (d_src, d_dst)
                elif self.dc_type == 'c':
                    # the num_nodes is squared of x
                    if self.load_type == 'uniforme1n' or \
                        self.load_type == 'nonuniforme1n':
                        d_dst = d_src + math.sqrt(self.num_nodes)
                        #return (d_src, d_dst)
                    elif self.load_type == 'uniformeij' or \
                        self.load_type == 'nonuniformeij': 
                        d_dst = max(dc_x, dc_y) - math.sqrt(self.num_nodes)
                    return (d_src, d_dst)
                elif self.dc_type == 'a':
                    # two data centers are adjecent in the middle
                    if self.load_type == 'uniforme1n' or \
                        self.load_type == 'nonuniforme1n':
                        d_dst = d_src - 1
                        #return (d_src, d_dst)
                    elif self.load_type == 'uniformeij' or \
                        self.load_type == 'nonuniformeij': 
                        d_dst = self.num_nodes
                    return (d_src, d_dst)
                else:
                    print "not a correct dc_type"
                    
        

def dryrun():
    ''' for debug '''
    # parameters, should be passed by cmd line
    topo_type = 'ring'
    dc_type = 'n'
    load_type = 'uniforme1n'
    num_paths = 2
    is_bin = 'no'
    num_nodes = 3
    model_type = 'mcr'
    link_capacity = 100
    
    # topology files
    path_lib = 'ring_3_path.txt'
    weight_csv = 'ring_3.csv'
    
    # ampl data file
    ampl_data_file = 'ring_3_test.dat'
    
    # create a network model
    model = network()
    
    # set binary model
    if is_bin == 'yes':
        model.set_bin()
    else:
        pass

    # no datacenter assignment, so should consider all pairs    
    model.set_dc_type(dc_type)
    # set demand type: uniform, random/min/max
    model.set_d_type(load_type)
    # set the number of nodes in the network
    model.set_num_nodes(num_nodes)
    # set topology type
    model.set_topo(topo_type)
    # set the number of paths
    model.set_num_path(num_paths)
    
    model.get_paths(path_lib)
    
    #model.get_dc_nodes()
    
    # No Data Center Scenario
    if model.dc_type == 'n':
        d_pairs = None
        if 'e1n' in model.load_type or 'eij' in model.load_type:
            d_src, d_dst = model.get_special_dpair()
            s_dpair = (min(d_src, d_dst), max(d_src, d_dst))
        else:
            s_dpair = None
        mc.run(ampl_data_file, path_lib,
                   weight_csv, model_type, topo_type,
                   model.load_type, model.num_paths, 
                   model.cost_type, link_capacity, d_pairs, s_dpair)
      
    else:
        model.get_dc_nodes()
        d_pairs = model.get_dmdpair()
        if 'e1n' in model.load_type or 'eij' in model.load_type: 
            d_src, d_dst = model.get_special_dpair()
            s_dpair = (min(d_src, d_dst), max(d_src, d_dst))
            print "special d_pair", s_dpair
            print "d_src, d_dst", d_src, d_dst
        else:
            s_dpair = None
        
        print model.load_type
        mc.run(ampl_data_file, path_lib,
                   weight_csv, model_type, topo_type,
                   model.load_type, model.num_paths, 
                   model.cost_type, link_capacity, d_pairs, s_dpair)
    
    
        
    
def create_option(parser):
    """
    add the options to the parser:
    takes arguments from commandline
    """
    parser.add_option("-v", action="store_true",
                      dest="verbose",
                      help="Print output to screen")
    parser.add_option("-w", dest="ampl_data_file",
                      type="str",
                      default="ample_test.dat",
                      help="Create ample data file")
    parser.add_option("--pfile", dest="path_lib",
                      type="str",
                      default="path_test.txt",
                      help="read the path file")
    parser.add_option("--csv", dest="weight_csv",
                      type="str",
                      default="test_topo.csv",
                      help="read topology csv file stores the adjacent matrix")
    parser.add_option("-m", dest="model_type",
                      type="str",
                      default="mcr",
                      help="minimum cost routing")
    parser.add_option("-t", dest="topo_type",
                      type="str",
                      default="random",
                      help="Topology type: random/grid/ring/full/rocketfuel")
    parser.add_option("-d", dest="demand_type",
                      type="str",
                      default="uniform",
                      help="Demand Type: uniform/nonuniform")
    parser.add_option("-c", dest="cost_type",
                      type="str",
                      default="byhops",
                      help="Type of cost of flow on path for each demand pair")
    parser.add_option("--np", dest="num_paths",
                      type="int",
                      default=5,
                      help="Number of path per demand pair")
    parser.add_option("--lc", dest="link_capacity",
                      type="float",
                      default=100,
                      help="Capacity for each link")
    parser.add_option("--dc", dest="dc_type",
                      type="str",
                      default="n",
                      help="""
                      The way to place two data centers in the network
                      Options are: 
                      ring topology: adjacent('a')/far ('f')
                      grid topology: side adjacent('s')/inside adjacent('a')/
                      corner('c')
                      full topology: adjacent('a')
                      random topology: adjacent('a')/far('f')
                      rocketfuel topology: TBD
                      No data centers: 'n'
                      """)
    parser.add_option("--nn", dest="num_nodes",
                      type="int",
                      default=3,
                      help="Number of nodes in the topology")
    parser.add_option("--seed", dest="seed_val",
                      type="int",
                      default=1,
                      help="Initial seed number for random number generation")
    
                      
def main(argv=None):
    """
    program wrapper
    """
    if not argv:
        argv=sys.argv[1:]
    usage = ("""%prog [-v verbose] 
                    [-w ampl_data_file] 
                    [--pfile path_lib] 
                    [--csv weight_csv] 
                    [-m model_type] 
                    [-t topo_type]
                    [-d demand_type]
                    [-c cost_type]
                    [--np num_paths]
                    [--lc link_capacity]
                    [--dc dc_type]
                    [--nn num_nodes]
                    [--seed seed_val]""")
    parser = OptionParser(usage=usage)
    create_option(parser)
    (options, _) = parser.parse_args(argv)
    
    # take arguments
    ampl_data_file = options.ampl_data_file
    path_lib = options.path_lib
    weight_csv = options.weight_csv
    model_type = options.model_type
    topo_type = options.topo_type
    load_type = options.demand_type
    cost_type = options.cost_type
    num_paths = options.num_paths
    link_capacity = options.link_capacity
    dc_type = options.dc_type
    num_nodes = options.num_nodes
    seed_val = options.seed_val
    
    
     # create a network model
    model = network()

    # set binary model
#    if is_bin == 'yes':
#        model.set_bin()
#    else:
#        pass
    
    # set cost type
    if cost_type != 'byhops':
        model.cost_type = 'rand'
    else:
        pass

    # no datacenter assignment, so should consider all pairs    
    model.set_dc_type(dc_type)
    # set demand type: uniform, random/min/max
    model.set_d_type(load_type)
    # set the number of nodes in the network
    model.set_num_nodes(num_nodes)
    # set topology type
    model.set_topo(topo_type)
    # set the number of paths
    model.set_num_path(num_paths)
    
    model.get_paths(path_lib)
    
    
    # No Data Center Scenario
    # No Data Center Scenario
    if model.dc_type == 'n':
        d_pairs = None
        if ('e1n' in model.load_type) or ('eij' in model.load_type):
            #print "E1N case"
            d_src, d_dst = model.get_special_dpair()
            s_dpair = (min(d_src, d_dst), max(d_src, d_dst))
        else:
            s_dpair = None
        #print "s_dpair", s_dpair
        mc.run(ampl_data_file, path_lib,
                   weight_csv, model_type, topo_type,
                   model.load_type, model.num_paths, 
                   model.cost_type, link_capacity, d_pairs, s_dpair, seed_val)
      
    else:
        model.get_dc_nodes()
        d_pairs = model.get_dmdpair()
        #print d_pairs
        if 'e1n' in model.load_type or 'eij' in model.load_type:
            #print "E1N case"
            d_src, d_dst = model.get_special_dpair()
            if (d_src, d_dst) == None:
                print "ERROR"
            else:
                s_dpair = (min(d_src, d_dst), max(d_src, d_dst))
                #print "d_src, d_dst", d_src, d_dst
        else:
            s_dpair = None
        print "special d_pair", s_dpair
        
        #print model.load_type
        mc.run(ampl_data_file, path_lib,
                   weight_csv, model_type, topo_type,
                   model.load_type, model.num_paths, 
                   model.cost_type, link_capacity, d_pairs, s_dpair, seed_val)
                   

if __name__ == '__main__':
    sys.exit(main()) 