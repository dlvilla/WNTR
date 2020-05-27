from nose.tools import *
from nose import SkipTest
from os.path import abspath, dirname, join
from matplotlib import pyplot as plt
import numpy as np
import networkx as nx
import wntr

testdir = dirname(abspath(str(__file__)))
datadir = join(testdir,'networks_for_testing')
netdir = join(testdir,'..','..','examples','networks')

def test_weight_graph():
    inp_file = join(netdir,'Net3.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    
    node_weight = wn.query_node_attribute('elevation')
    link_weight = wn.query_link_attribute('length')
    
    G = wn.get_graph(node_weight, link_weight)
    
    assert_equal(G.nodes['111']['weight'], 10*0.3048)
    assert_equal(G['159']['161']['177']['weight'], 2000*0.3048)

def test_terminal_nodes():
    inp_file = join(netdir,'Net1.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    G = wn.get_graph()
    
    terminal_nodes = wntr.metrics.terminal_nodes(G)
    expected = set(['2', '9'])
    assert_set_equal(set(terminal_nodes), expected)

def test_bridges():
    inp_file = join(netdir,'Net1.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    G = wn.get_graph()
    
    bridges = wntr.metrics.bridges(G)
    expected = set(['9','10','110'])
    assert_set_equal(set(bridges), expected)

def test_diameter():
    inp_file = join(datadir,'Anytown.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    for pump in wn.pump_name_list[:-1]: # remove 2 of the 3 pumps
        wn.remove_link(pump)
    G = wn.get_graph()
    udG = G.to_undirected()
    val = nx.diameter(udG)
    excepted = 7 # Davide Soldi et al. (2015) Procedia Engineering
    assert_equals(val, excepted)

def test_central_point_dominance():
    inp_file = join(datadir,'Anytown.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    for pump in wn.pump_name_list[:-1]: # remove 2 of the 3 pumps
        wn.remove_link(pump)
    G = wn.get_graph()

    val = wntr.metrics.central_point_dominance(G)
    expected = 0.23 # Davide Soldi et al. (2015) Procedia Engineering
    error = abs(expected-val)
    assert_less(error, 0.01)

def test_spectral_gap():
    inp_file = join(datadir,'Anytown.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    for pump in wn.pump_name_list[:-1]: # remove 2 of the 3 pumps
        wn.remove_link(pump)
    G = wn.get_graph()

    val = wntr.metrics.spectral_gap(G)
    expected = 1.5149 # Davide Soldi et al. (2015) Procedia Engineering
    error = abs(expected-val)
    assert_less(error,0.01)

def test_algebraic_connectivity():
    inp_file = join(datadir,'Anytown.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    for pump in wn.pump_name_list[:-1]: # remove 2 of the 3 pumps
        wn.remove_link(pump)
    G = wn.get_graph()
    
    val = wntr.metrics.algebraic_connectivity(G)
    expected = 0.1708 # Davide Soldi et al. (2015) Procedia Engineering
    error = abs(expected-val)
    raise SkipTest
    assert_less(error,0.01)

def test_crit_ratio_defrag():
    inp_file = join(datadir,'Anytown.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    for pump in wn.pump_name_list[:-1]: # remove 2 of the 3 pumps
        wn.remove_link(pump)
    G = wn.get_graph()
    
    val = wntr.metrics.critical_ratio_defrag(G)
    expected = 0.63 # Pandit et al. (2012) Critical Infrastucture Symposium
    error = abs(expected-val)
    raise SkipTest
    assert_less(error,0.01)
    
def test_Net1_MultiDiGraph():
    inp_file = join(netdir,'Net1.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    G = wn.get_graph()

    node = {'11': {'pos': (30.0, 70.0),'type': 'Junction'},
            '10': {'pos': (20.0, 70.0),'type': 'Junction'},
            '13': {'pos': (70.0, 70.0),'type': 'Junction'},
            '12': {'pos': (50.0, 70.0),'type': 'Junction'},
            '21': {'pos': (30.0, 40.0),'type': 'Junction'},
            '22': {'pos': (50.0, 40.0),'type': 'Junction'},
            '23': {'pos': (70.0, 40.0),'type': 'Junction'},
            '32': {'pos': (50.0, 10.0),'type': 'Junction'},
            '31': {'pos': (30.0, 10.0),'type': 'Junction'},
            '2':  {'pos': (50.0, 90.0),'type': 'Tank'},
            '9':  {'pos': (10.0, 70.0),'type': 'Reservoir'}}

    edge = {'11': {'12': {'11':  {'type': 'Pipe'}},
                   '21': {'111': {'type': 'Pipe'}}},
            '10': {'11': {'10':  {'type': 'Pipe'}}},
            '13': {'23': {'113': {'type': 'Pipe'}}},
            '12': {'13': {'12':  {'type': 'Pipe'}},
                   '22': {'112': {'type': 'Pipe'}}},
            '21': {'31': {'121': {'type': 'Pipe'}},
                   '22': {'21':  {'type': 'Pipe'}}},
            '22': {'32': {'122': {'type': 'Pipe'}},
                   '23': {'22':  {'type': 'Pipe'}}},
            '23': {},
            '32': {},
            '31': {'32': {'31':  {'type': 'Pipe'}}},
            '2':  {'12': {'110': {'type': 'Pipe'}}},
            '9':  {'10': {'9':   {'type': 'Pump'}}}}

    assert_dict_contains_subset(node, G.nodes)
    assert_dict_contains_subset(edge, G.adj)
    
def test_plot_center():
    inp_file = join(netdir,'Net3.inp')
    wn = wntr.network.WaterNetworkModel(inp_file)
    
    # no plot limits input
    fig, ax = plt.subplots(1,1)
    wntr.graphics.network.plot_network(wn,plot_center=(25,12),ax=ax)
    plt.close(fig)
    
    # direct coordinate input
    fig, ax = plt.subplots(1,1)
    wntr.graphics.network.plot_network(wn,plot_center=(25,12),plot_limits=(10,10),ax=ax)
    assert_equal(ax.get_xlim(),(20.0,30.0))
    assert_equal(ax.get_ylim(),(7.0,17.0))
    plt.close(fig)
    
    # link input
    fig, ax = plt.subplots(1,1)
    plot_limit_val = (16,8)
    wntr.graphics.network.plot_network(wn,plot_center='309',
                                       plot_limits=plot_limit_val,
                                       ax=ax,
                                       link_labels=['309'])
    node_265_coord = (25.39,13.60)
    node_267_coord = (23.38,12.95)
    center = [(n265 + n267)/2 for n265,n267 in zip(node_265_coord,node_267_coord)]
        
    assert_equal(ax.get_xlim(),(center[0]-0.5*plot_limit_val[0],
                                center[0]+0.5*plot_limit_val[0]))
    assert_equal(ax.get_ylim(),(center[1]-0.5*plot_limit_val[1],
                                center[1]+0.5*plot_limit_val[1]))
    plt.close(fig)
    
    # node input
    fig, ax = plt.subplots(1,1)
    linknames = wn.get_links_for_node('61')
    wntr.graphics.network.plot_network(wn,plot_center='61',plot_limits=(10,10),
                                       ax=ax,node_labels=['61'],
                                       link_labels=linknames)    
    assert_equal(ax.get_xlim(),(23.71-5.0,23.71+5.0))
    assert_equal(ax.get_ylim(),(29.03-5.0,29.03+5.0))
    plt.close(fig)
    
    # ValueError exceptions
    with assert_raises(ValueError):
        # too long of plot_center input
        wntr.graphics.network.plot_network(wn,plot_center=(25,12,10),plot_limits=(10,10),ax=ax)
    
    with assert_raises(ValueError):
        # incorrect object
        wntr.graphics.network.plot_network(wn,plot_center=wn,plot_limits=(10,10),ax=ax)
    
    with assert_raises(ValueError):
        # plot_limits too many inputs
        wntr.graphics.network.plot_network(wn,plot_center=(25,12),plot_limits=(10,10,10),ax=ax)  
    
    with assert_raises(ValueError):
        # plot_limits incorrect type input
        wntr.graphics.network.plot_network(wn,plot_center=(25,12),plot_limits=ax,ax=ax) 
        
    with assert_raises(ValueError):
        # plot_limits input with no plot_center
        wntr.graphics.network.plot_network(wn,plot_limits=(10,10),ax=ax)  

if __name__ == '__main__':
    test_weight_graph()
    test_plot_center()