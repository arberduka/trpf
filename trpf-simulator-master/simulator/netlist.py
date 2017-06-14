import ast, shlex, os, pprint, numbers
import pandas as pd
import pygraphviz as pgv
from IPython.display import Image

def load(netlist):
    """Parse the netlist file, return simulation parameters."""
    #AD __file__ gives the name of the current file (netlist.py), realpath returns the absolute 
    #path to this file, dirname returns the name of the directory containing __file__, and join
    #returns the path to the directory containing __file__ and adds "/../netlists/netlist.ntl"
    #to the end of it, where netlist is the argument given to load (stripped of .ntl).
    #Essentially, nlpath gives the path to the netlist given to load, assuming that it is present 
    #in the netlists folder.
    
    nlpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                          '..', 'netlists', netlist.split('.ntl')[0] + '.ntl')
    #AD properties is a hash of attributes of a netlist; name is a string containing everything
    #before .ntl in the argument given to load. graph is a 2D data structure with labeled axes.
    #routes is an empty hash, thresholds and weights are empty arrays, etc. The default value
    #for steps is 200.
        properties = {
        'name': netlist.split('.ntl')[0], 
        'graph': pd.DataFrame(),
        'routes': {},
        'thresholds': [],
        'weights': [],
        'trpf': {
            'g': [], 
            't': [], 
            'p': []
        },
        'trips': [],
        'agents': [],
        'optimums': {},
        'steps': 200
    }   
    
    #AD The with block allows the file specified by nlpath to be closed automatically after the
    #with block is complete, regardless of if any errors are thrown within the block. 
    #nlpath gives the path to the netlist, and 'r' opens it in read mode. The opened file is 
    #referred to as f. For every line in f, if the first character is a # (comment) or the line 
    #is simply white space (line.strip() removes all leading and trailing white space) this line 
    #is skipped. If the first word in a line (split using shell-like syntax) is trip, then the
    #number of trips (ntrips) is incremented. First, the number of trips is counted. A hash with
    #an empty array is made for each trip, to store all the routes in a trip. The same is done
    #for the optimums. An empty array with ntrips elements is made to store the trip number
    #(given by index?). THe string 'Overall' is added as the last element of this array.
    #agents is also initialized as an empty array of ntrips elements, to store the number
    #of agents per trip.

    with open(nlpath, 'r') as f: 
        # One initial pass to count number of trips
        ntrips = 0
        for line in f:
            if line[0] == '#' or len(line.strip()) == 0:
               continue
            if shlex.split(line.lower().strip())[0] == 'trip':
                ntrips += 1
        properties['routes'] = {trip: [] for trip in range(ntrips)}
        properties['optimums'] = {trip: [] for trip in range(ntrips)}
        properties['trips'] = [None for trip in range(ntrips)]
        properties['trips'].append('Overall')
        properties['agents'] = [None for trip in range(ntrips)]
    
    with open(nlpath, 'r') as f:
        for line in f:
            if line[0] == '#' or len(line.strip()) == 0:
                continue

            args = shlex.split(line.lower().strip())
            command = args.pop(0)

            kwargs = {arg.split('=')[0]: arg.split('=')[1]
                      for arg in args if '=' in arg}
            posargs = [arg for arg in args if '=' not in arg]

            # TODO: don't think this needs to be specified
            if command == 'type' and args[0] == 'multiod':
                pass
            else:
                pass
            
            if command == 'edge':
                if len(args) >= 2:
                    row = {'node 1': args[0], 'node 2': args[1]}
                    if 'fft' in kwargs:
                        row.update({'fft': float(kwargs['fft'])})
                    else:
                        row.update({'fft': 0})
                    if 'ddt' in kwargs:
                        row.update({'ddt': float(kwargs['ddt'])})
                    else:
                        row.update({'ddt': 0})
                properties['graph'] = pd.concat(
                    [properties['graph'], pd.DataFrame(row, index=[0], 
                        columns=['node 1', 'node 2', 'fft', 'ddt'])], 
                    ignore_index=True)
             
            if command == 'trip':
                properties['routes'][int(kwargs['index'])] \
                    = [[] for i in range(int(kwargs['routes']))] 
                properties['optimums'][int(kwargs['index'])] \
                    = [None for i in range(int(kwargs['routes']))]
                properties['trips'][int(kwargs['index'])] \
                    = kwargs['name'].upper()
                properties['agents'][int(kwargs['index'])] \
                    = int(kwargs['agents'])

            if command == 'route':
                trip = int(kwargs['trip'])
                route = int(kwargs['route'])
                properties['routes'][trip][route] = args[0].split(',')
                properties['optimums'][trip][route] = int(kwargs['so'])

            if command == 'weights':
                properties['thresholds'].append([0 for bp in args])
                properties['weights'].append([0 for bp in args])
                for i, breakpoint in enumerate(args):
                    cars, weight = breakpoint.split(':')
                    properties['thresholds'][-1][i] = int(cars)
                    properties['weights'][-1][i] = int(weight)

            if command == 'trpf':
                if len(args) >= 3:
                    gvals = ast.literal_eval(kwargs['g'])
                    if isinstance(gvals, list):
                        properties['trpf']['g'] = gvals
                    elif isinstance(gvals, numbers.Number):
                        properties['trpf']['g'] = [gvals]
                    
                    tvals = ast.literal_eval(kwargs['t'])
                    if isinstance(tvals, list):
                        properties['trpf']['t'] = tvals
                    elif isinstance(tvals, numbers.Number):
                        properties['trpf']['t'] = [tvals]
                        
                    pvals = ast.literal_eval(kwargs['p'])
                    if isinstance(pvals, list):
                        properties['trpf']['p'] = pvals
                    elif isinstance(pvals, numbers.Number):
                        properties['trpf']['p'] = [pvals]
                
                if 'steps' in kwargs:
                    properties['steps'] = int(kwargs['steps'])

    return properties

def show(netlist):
    """ Print text of netlist file """
    nlpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                          '..', 'netlists', netlist.split('.ntl')[0] + '.ntl')
        
    with open(nlpath, 'r') as f: 
        for line in f:
            print(line)

def draw(properties, filename):
    df = properties['graph']
    edges = zip(df['node 1'].tolist(),
                df['node 2'].tolist(),
                df['fft'].tolist(),
                df['ddt'].tolist())
    network = pgv.AGraph(strict=False,directed=True)
    network.node_attr['shape'] = 'circle'
    network.node_attr['fontsize'] = '12'
    network.graph_attr['rankdir'] = 'LR'
    network.edge_attr['fontsize'] = '8' 
    network.graph_attr['label'] = properties['name'] + '.ntl'
    #  network.graph_attr['ratio']='.5'
    for src, dest, fft, ddt in edges:
        if fft and ddt:
            network.add_edge(src, dest, label='fft={}, ddt={}'.format(fft, ddt)) 
        elif fft:
            network.add_edge(src, dest, label='fft={}'.format(fft))
        elif ddt: 
            network.add_edge(src, dest, label='ddt={}'.format(ddt))
        else: 
            network.add_edge(src, dest)

        
    #  print(network.string())
    
    network.layout(prog='dot')
    network.draw(filename)
    #  Image(filename='network.png') 
    
    #  B.layout() # layout with default (neato)
    #  B.draw('simple.png') # draw png
    #  print("Wrote simple.png")

if __name__ == '__main__':
    p = load('example')
    draw(p, 'network.png')
