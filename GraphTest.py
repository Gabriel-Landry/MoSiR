import pandas as pd
import GraphFactory as gf
import warnings
import json

class QuantityError(Exception):
    def __init__(self, message: str):            
        super().__init__(message) 
        
class EdgeError(Exception):
    def __init__(self, message: str):            
        super().__init__(message)
        
class ConstError(Exception):
    def __init__(self, message: str):    
        super().__init__(message)

# Test indépendant du import -------------------------------------------------
""" 
Test_01 = gf.WPGraph("Test Graph")

A = gf.TopNode('A', [0], [10])  
B = gf.ProportionNode('B')
C = gf.DecayNode('C', 3)
D = gf.DecayNode('D', 3)
E = gf.RecyclingNode('E')
F = gf.PoolNode('F')
A.GetCarbon(Test_01, 1)
Test_01.AddNode(A)
Test_01.AddNode(B)
Test_01.AddNode(C)
Test_01.AddNode(D)
Test_01.AddNode(E)
Test_01.AddNode(F)
 
Test_01.AddEdge(A, B, Proportions = [1])
Test_01.AddEdge(B, C, Proportions = [1])
Test_01.AddEdge(C, D, Proportions = [0.5])
Test_01.AddEdge(C, E, Proportions = [0.5])
Test_01.AddEdge(E, B, Proportions = [1])
Test_01.AddEdge(D, F, Proportions = [1])

A.CountCarbon(Test_01, 0) == C.CountCarbon(Test_01, 0)
B.GetCarbon(Test_01, 0)
C.CountCarbon(Test_01, 0)
 
total = 0
for i in test1.nodes():
    if type(i) == PoolNode:
        total += i.CountCarbon(test1, 16)
    if type(i) == DecayNode:
        total += i.CountCarbon(test1, 16)
    if type(i) == RecyclingNode:
        total += i.GetCarbon(test1, 17)
    print(total) 
    """


# Test de l'import -----------------------------------------------------------
Test_02 = gf.GraphFactory('T:/Donnees/Usagers/LANGA3/MoSiR/Graphs_04.json')
MOSIR_TOLERENCE = 0.0001

# First node et last node
for GraphName in Test_02.GetData:
    GRAPH = Test_02.GetData.get(GraphName)
    NODES = GRAPH.get('Nodes', {})
    EDGES = GRAPH.get('Edges', {})
    TOPNODES = set([int(ID) for ID in NODES]) - \
                set([data['To'] for keys, data in EDGES.items()])
    if len(TOPNODES) > 1:
        warnings.warn(f"Attention, plus d'une TopNode présente.\
            Les inputs vont être acheminés à ces deux nodes: \
            {TOPNODES}")  
    LASTNODES = set([int(ID) for ID in NODES]) - \
                set([data['From'] for keys, data in EDGES.items()])
    if len(LASTNODES) == 0:
        warnings.warn(f"Attention, aucune PoolNode présente. La quantité \
            de carbone présente dans le système sera calculé seulement sur \
            des nodes de demi-vie ou de recyclage")   
   
# Total des Edges 
for Name in Test_02.GetGraphName:
    Graph = Test_02.GetGraph(Name)
    for Node in Graph.Nodes():
        Total = 0
        for Successors in Graph.GetSuccessors(Node):
            if Successors.NAME == 'N2O emissions':
                continue
            Total += Node._GetValueTime(Graph.GetEdgeProportions(Node, Successors), 0)
        if Total - 1 > MOSIR_TOLERENCE or 1 - Total > MOSIR_TOLERENCE and Total != 0:
            raise EdgeError(f"La somme des edges sortant de {Node.NAME} n'est pas égale à 100%") 
        elif Total < MOSIR_TOLERENCE:
            warnings.warn(f'La somme des edges sortant de la node {Node.NAME} est de 0')
            
# Test de overflow
for GraphName in Test_02.GetData:
    GRAPH = Test_02.GetData.get(GraphName)
    NODES = GRAPH.get('Nodes', {})
    EDGES = GRAPH.get('Edges', {})
    for NodeId in NODES:
        Overflow = []
        for key, values in EDGES.items():
            if values.get('To') == int(NodeId):
                Overflow.append(values.get('Overflow'))
        if all(i == Overflow[0] for i in Overflow) == False:
            raise EdgeError(f"La node {NODES[str(NodeId)].get('Name')} reçoit \
                des edges avec et sans overflow")

# "EternalStock": 1.0, "Oxydation": 0.0, "Export": 0.0, 
   
# Total input versus in system 
for Name in Test_02.GetGraphName:
    Graph = Test_02.GetGraph(Name)
    Input = 0
    for Time in range(150): # Ajuster le temps des simulations
        InSystem = 0
        for Node in Graph.Nodes():
            if type(Node) == gf.TopNode:
                Input += Node.CountCarbon(Graph, Time)
            elif Node.NAME == 'N2O emissions':
                continue
            elif type(Node) == gf.PoolNode or type(Node) == gf.DecayNode or \
                type(Node) == gf.RecyclingNode:
                InSystem += Node.CountCarbon(Graph, Time)
        if Input > InSystem - MOSIR_TOLERENCE and Input < InSystem + MOSIR_TOLERENCE :
            print(f'Time {Time} checked')
            continue
        else:
            raise QuantityError(f"Graph : {Graph.GetName} La quantité total \
                en input ({Input}) au temps {Time} n'est pas égale au total \
                présent dans le système ({InSystem})")

# Prod de résultats ----------------------------------------------------------

# Dataframe all nodes > 0
data = {'Time': [],
        'Node': [],
        'Value': []}
df = pd.DataFrame(data)
for Name in Test_02.GetGraphName:
    Graph = Test_02.GetGraph(Name)
    for Time in range(16): # Ajuster le temps des simulations
        for Node in Graph.Nodes():
            C = Node.GetCarbon(Graph, Time)
            if C != 0:
                N = Node.NAME
                T = Time
                new = {'Time': T, 'Node': N, 'Value': C}
                new_df = pd.DataFrame([new])
                df = pd.concat([df, new_df], ignore_index = True)

#df.to_csv('Output_verification.csv', index = False, sep = ';')

# Emissions nodes
data = {'Time': [],
        'CH4 emissions': [],
        'CO2 emissions': [],
        'N2O emissions': []}
df = pd.DataFrame(data)
for Name in Test_02.GetGraphName:
    Graph = Test_02.GetGraph(Name)
    for Time in range(16): 
        for Node in Graph.Nodes():
            if Node.NAME == 'CH4 emissions':
                CH4 = Node.CountCarbon(Graph, Time, Cumulative = False)
            elif Node.NAME == 'CO2 emissions':
                CO2 = Node.CountCarbon(Graph, Time, Cumulative = False)
            elif Node.NAME == 'N2O emissions':
                N2O = Node.CountCarbon(Graph, Time, Cumulative = False)
        new_line = pd.DataFrame([{'Time': Time, 
                                 'CH4 emissions': CH4,
                                 'CO2 emissions': CO2, 
                                 'N2O emissions': N2O}])
        df = pd.concat([df, new_line], ignore_index = True)

#df.to_csv('Output_emissions.csv', index = False, sep = ';')


# N2O checkup

for Name in Test_02.GetGraphName:
    Graph = Test_02.GetGraph(Name)
    for Time in range(16): # Ajuster le temps des simulations
        for Node in Graph.Nodes():
            if Node.NAME in ['Land application', 'Biomethanisation, combustion']:
                print(f'Time {Time}, {Node.NAME} = {Node.GetCarbon(Graph, Time)}')
                #C = Node.CountCarbon(Graph, Time, Cumulative = False)
                #if C != 0:
                #    N = Node.NAME
                #    T = Time
                #    new = {'Time': T, 'Node': N, 'Value': C}
                #    new_df = pd.DataFrame([new])
                #    df = pd.concat([df, new_df], ignore_index = True)


#with pd.option_context('display.max_rows', None,
#                       'display.max_columns', None,
#                       'display.precision', 4,
#                       ):
#    print(df3)



#
#for edge_id, edge_data in edges.items():
#    From = edge_data['From']
#    To = edge_data['To']
#    nom_from = None
#    nom_to = None
#    for node_id, node_data in nodes.items():
#        if int(node_id) == From:
#            nom_from = node_data['Name']
#        elif int(node_id) == To:
#            nom_to = node_data['Name']
#    print(f'Connection entre {nom_from} à {nom_to}')

# ----------------------------------------------------------------------------
"""
G = ig.Graph(directed = True)

a = TopNode('P1', [0], [10])
b = ProportionNode('P2')
c = ProportionNode('P3')
d = ProportionNode('P4')

G.add_vertex(a, Nom = 'Test1')
G.add_vertex(b, Nom = 'Test2')
G.add_vertex(c, Nom = 'Test3')
G.add_vertex(d, Nom = 'Test4')

G.add_edge(0, 1, Proportion = 0.1)
G.add_edge(0, 2, Proportion = 0.2)
G.add_edge(1, 3, Proportion = 0.3)
G.add_edge(2, 3, Proportion = 0.4)

G.to_dict_dict()
G.get_vertex_dataframe()
G.es.select(3)['Proportion']
G.vs.select(1)['Name']
G.es[G.get_eid(0, 1)]['Proportion']

dictio = G.to_dict_dict()

G.predecessors()

help(G.Full)
G.Full(len(G.vs.indices))

for i in G.vs:
    print(i)

liste = {1: 'a', 2: 'b', 3: "ce"}

for i, j in enumerate(liste):
    print(i)
"""