# -*- coding: utf-8 -*-
"""
This function is to create a subset of demand pairs of all possible 
demand pairs, by assigning two data centers

Created on Tue Dec 24 14:41:15 2013

@author: xuanliu
"""

import random
import math
from copy import deepcopy

def dc_nodes(path_dict, num_node, place_type, topo_type):
    """
    This function is to return two nodes where the data centers 
    should be placed. 
    Input is the path_dict, 
    placement type: adjacent/far as possible
    topo type: ring/grid/full/random
    """
    
    if topo_type == "ring":
        # ring topology
        #node_x = random.choice(range(1, num_node + 1))
        node_x = 1
        if place_type == 'a':
            node_y = (node_x + 1) % num_node
        elif place_type == 'f':
            if num_node % 2 == 1: # odd number of nodes
                node_y = (node_x + (num_node + 1) / 2) % num_node
            else:
                node_y = (node_x + num_node / 2) % num_node
        if node_y == 0:
            node_y = num_node
    if topo_type == "grid":
        # grid topology: m-by-m
        top, bottom, left, right = grid_edges(num_node)
        corner = grid_corner(num_node)
        h_edges = deepcopy(top)
        v_edges = deepcopy(left)
        h_edges.extend(bottom)
        v_edges.extend(right)
        #side = set().union(set(top), set(bottom), set(left), set(right))
        
        if place_type == 's':
            #side_nonc = side.difference(set(corner))
            #node_x = random.choice(list(side_nonc))
            #node_x = random.choice(top)
            node_x = 2
            if node_x in h_edges and node_x not in corner:
                node_y = node_x + 1
            elif node_x in v_edges and node_x not in corner:
                node_y = int(node_x + math.sqrt(num_node))
            else:
                pass
            print "Data Center Nodes", node_x, node_y
        if place_type == 'c':
            #node_x = random.choice(corner)
            node_x = 1
            node_y = num_node + 1 - node_x
        if place_type == 'a':
            # two data centers are adjacent in the center
            if num_node % 2 == 1:
                # odd number of nodes
                node_x = int((1 + num_node) / 2)
            else:
                # even number of nodes
                node_x = int((num_node - math.sqrt(num_node)) / 2)
            node_y = node_x + 1 # inside the grid
    print "Data Center Nodes", node_x, node_y    
    return (node_x, node_y)
    

def grid_edges(num_node):
    """
    return a set of nodes at the edges of a grid topology 
    num_nodes = m * m
    """
    m = math.sqrt(num_node)
    top = []
    bottom = []
    left = []
    right = []
    for node_id in range(1, num_node + 1):
        if node_id % m == 1:
            left.append(node_id)
        elif node_id % m == 0:
            right.append(node_id)
        elif node_id <= m:
            top.append(node_id)
        elif node_id >= num_node - m + 1:
            bottom.append(node_id)
        else:
            pass
    return (top, bottom, left, right)

def grid_corner(num_node):
    """
    return the corner of a grid network
    num_nodes = m * m
    """
    m = int(math.sqrt(num_node))
    corner = [1, m, num_node - m + 1, num_node]
    return corner
    

            
