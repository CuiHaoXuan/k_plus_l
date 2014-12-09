#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script is to parse the topology information from xml or gml files, 
which includes the information about nodes, links, link capacities, costs
demand information,etc.

The input is the xml/gml file, and the output is a adjacent matrix, which
will be read by matlab code to generate the path

The xml file is obtained from http://sndlib.zib.de/home.action, so the 
format is based on the source pre-defined by http://sndlib.zib.de/home.action

Note: To run this script, needs to install xmltodict module separately

Code by Xuan Liu
Jan. 3, 2014

"""


from lxml import etree
import xmltodict
import topo_create
import networkx as nx
import json

def parse_xml(xmlfile='geant.xml'):
    ''' parse xml file to string '''
    tree = etree.parse(xmlfile)
    return tree 

def get_children(tree):
    ''' get child trees '''
    tree_root = tree.getroot()
    child_tree = tree_root.getchildren()
    netstruct_tree = child_tree[1]
    demand_tree = child_tree[2]
    return netstruct_tree, demand_tree

def get_node_link_tree(netstruct_tree):
    ''' get trees for nodes and links'''
    children = netstruct_tree.getchildren()
    nodes = children[0]
    links = children[1]
    return nodes, links
        
def xml_todictlist(xml_tree):
    ''' convert lxml.etree._Element to a list of dictionary '''
    xml_str=etree.tostring(xml_tree, pretty_print=True)
    xml_dictlist = xmltodict.parse(xml_str)
    tag = xml_tree.tag
    key = xml_dictlist[tag].keys()
    return xml_dictlist[tag][key[-1]]
    
def get_nodes(nodes_dictlist):
    """
    create a node dictionary in form of 
    dict = {node_a: {id: 1, coordinates: (x, y)},...}
    Sample item in the nodes_dictlist is given below:
        OrderedDict([(u'@id', u'at1.at'), 
                     (u'coordinates', OrderedDict([(u'x', u'16.3729'), 
                                                   (u'y', u'48.2091')]))])
    """
    node_dict = {}
    node_index = 1
    for node in nodes_dictlist:
        node_name = str(node['@id'])
        #print node_name
        node_dict[node_name] = {}
        node_dict[node_name]['id'] = node_index
        coordinate = map(float, dict(node['coordinates']).values())
        node_dict[node_name]['coordinates'] = tuple(coordinate)
        node_index += 1
    return node_dict
    
        
def get_links(link_dictlist, node_dict):
    """
    create a link dictionary in form of 
    dict = {link_id: {src: node_x, dst: node_y, capacity: 100, cost:804.0}, 
            ...}
    Sample item in the link_dictlist is given below:
    OrderedDict([(u'@id', u'at1.at_ch1.ch'), 
                 (u'source', u'at1.at'), 
                 (u'target', u'ch1.ch'), 
                 (u'additionalModules', 
                  OrderedDict([(u'addModule', 
                                OrderedDict([(u'capacity', u'40000.0'), 
                                             (u'cost', u'804.0')]))]))])
    Note: the link here is indirected link
    """      
                        
    link_dict = {}
    link_index = 1
    for link in link_dictlist:
        link_name = str(link['@id'])
        node_x = link_name.partition('_')[0]
        node_y = link_name.partition('_')[2]
        node_x_id = node_dict[node_x]['id']
        node_y_id = node_dict[node_y]['id']
        link_dict[link_index] = {}
        link_dict[link_index]['src'] = node_x_id
        link_dict[link_index]['dst'] = node_y_id
        link_dict[link_index]['capacity'] = 100
        link_dict[link_index]['cost'] = \
                float(link['additionalModules']['addModule']['cost'])
        link_index += 1
    return link_dict
    
def get_demands(demand_dictlist, node_dict):
    """
    create a link dictionary in form of 
    dict = {demand_id: {src: node_x, dst:node_y, value: load_m}, ...}
    Sample item in the demand_dictlist is given below:
    OrderedDict([(u'@id', u'ny1.ny_il1.il'), 
                 (u'source', u'ny1.ny'), 
                 (u'target', u'il1.il'), 
                 (u'demandValue', u'3003.0')])
    Note: the demand here is directed demand, so needs to add demand x_y and 
          y_x for demand pair(x, y)
    """
    demand_dict = {}
    for demand in demand_dictlist:
        demand_name = str(demand['@id'])
        node_x = demand_name.partition('_')[0]
        node_y = demand_name.partition('_')[2]
        node_x_id = node_dict[node_x]['id']
        node_y_id = node_dict[node_y]['id']
        reverse_name = node_y + '_' + node_x
        reverse_dvalue = get_reverse_demand(demand_dictlist, reverse_name)
        new_dvalue = float(demand['demandValue']) + reverse_dvalue
        key = str((min(node_x_id, node_y_id), max(node_x_id, node_y_id)))
        demand_dict[key] = round(new_dvalue, 4)
    return demand_dict
        
        
def get_reverse_demand(demand_dictlist, demand_name):
    """
    this function is to return the demand vaule for (y,x), where demand name
    y_x is given. This is specific to the indirection case
    """ 
    for demand in demand_dictlist:
        if demand['@id'] == demand_name:
            return float((demand['demandValue']))
    return 0
            
def create_adj_matrix(link_dict):
    ''' create the link adjacent matrix '''
    edges_dict = {}
    cost_dict = {}
    graph = nx.Graph()
    for link_id in link_dict:
        src = link_dict[link_id]['src']
        dst = link_dict[link_id]['dst']
        cost = link_dict[link_id]['cost']
        edges_dict[link_id] = (src, dst)
        cost_dict[link_id] = cost
        graph.add_edge(src, dst, weight=cost)
    topo_create.topo_csv_gen('geant.csv', graph)
    return graph
   
def dryrun():
    ''' debug '''
    #geant_xml = 'geant-source/geant.xml'
    geant_xml = 'topo_info/geant_demand/geant-demand-20050509-2130.xml'
    tree = parse_xml(geant_xml)
    netstruct_tree, demand_tree = get_children(tree)
    nodes, links = get_node_link_tree(netstruct_tree)
    node_dictlist = xml_todictlist(nodes)
    #link_dictlist = xml_todictlist(links)
    demand_dictlist = xml_todictlist(demand_tree)
    
    node_dict = get_nodes(node_dictlist)
    #link_dict = get_links(link_dictlist, node_dict)
    demand_dict = get_demands(demand_dictlist, node_dict)
    
    #graph = create_adj_matrix(link_dict)
    
    s = json.dumps(demand_dict)
    fopen = open('topo_info/geant_demand/geant_demand_20050509_2130.json', 'w')

    fopen.write(s)
    fopen.close()

    return node_dict, demand_dict
    #return node_dict, link_dict, demand_dict, graph

    

    
    