import networkx as nx
import igraph as ig

class ConstError(Exception):
    def __init__(self, message: str):    
        super().__init__(message)

class WPGraph():
    def __init__(self, KEY):
        super().__init__()
        self._graph = nx.DiGraph()
        self._NAME = KEY
    
    def add_node(self, node):
        return self._graph.add_node(node)
    
    def add_edge(self, From, To, Proportions):
        return self._graph.add_edge(From, To, Proportion = Proportions)
    
    def get_edge_proportions(self, From, To) -> list[float]:
        return self._graph.get_edge_data(From, To)["Proportion"]
    
    def get_predecessors(self, node):
        return self._graph.predecessors(node)
    
    def get_successors(self, node):
        return self._graph.successors(node)
    
    def nodes(self):
        return self._graph.nodes()
    
    @property
    def get_name(self):
        return self._NAME
    
    @get_name.setter
    def get_name(self):
        return ConstError("Graph name can't be changed outside Miro")

class WPGraph_IG():
    def __init__(self, KEY):
        super().__init__()
        self._graph = ig.Graph(directed = True)
        self._NAME = KEY
   
    def __ToIGnode(self, node):
        return self._graph.vs.find(data = node)
   
    def add_node(self, node):
        return self._graph.add_vertex(data = node)
    
    def add_edge(self, From, To, Proportions):
        From_VS = self.__ToIGNode(From)
        To_VS = self.__ToIGNode(To)
        return self._graph.add_edge(From_VS, To_VS, Proportion = Proportions)
    
    def get_edge_proportions(self, From, To) -> list[float]:
        From_VS = self.__ToIGNode(From)
        To_VS = self.__ToIGNode(To)
        return self._graph.es[self._graph.get_eid(From_VS, To_VS)]['Proportion']
    
    def get_predecessors(self, node):
        From_VS = self.__ToIGNode(node)
        return [self._graph.vs[i]['data'] for i in self._graph.predecessors(From_VS)]
    
    def get_successors(self, node):
        To_VS = self.__ToIGNode(node)
        return [self._graph.vs[i]['data'] for i in self._graph.successors(To_VS)]
    
    def nodes(self):
        return [i['data'] for i in self._graph.vs]
    
    @property
    def get_name(self):
        return self._NAME
    
    @get_name.setter
    def get_name(self):
        return ConstError("Graph name can't be changed outside Miro")