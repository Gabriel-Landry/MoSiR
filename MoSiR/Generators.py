"""
Copyright (c) 2023 Gouvernement du Québec
SPDX-License-Identifier: LiLiQ-R-1.1
License-Filename: LICENSES/EN/LiLiQ-R11unicode.txt
"""

from abc import ABCMeta

class Generator(metaclass=ABCMeta):
    def __init__(self,GraphName:str):
        self.__GraphName= GraphName
        self._nodes = {}
        self._edges = {}
    def get_graph_name(self)->str:
        return self.__GraphName
    def to_dict(self)->dict:
        return {"Nodes":self._nodes,"Edges":self._edges}
    def get_graph_stats(self)->dict():
        Alldata = {"Nodes":{"Size":len(self._nodes)},"Edges":{"Size":len(self._edges)}}
        Minedgevalue = 1
        Maxedgevalue = 0
        for Datatype,Data in zip(["Nodes","Edges"],[self._nodes.values(),self._edges.values()]):
            for NodeItems in Data:
                for Name,Element in NodeItems.items():
                    if Name not in ["Name","Values","From","To","X","Y"]:
                        if Name not in Alldata[Datatype]:
                            Alldata[Datatype][Name] = 0
                        target_value = 0
                        if int(Element) > 0:
                            target_value = 1
                        Alldata[Datatype][Name] += target_value
                    elif (Name == "Values"):
                        for Value in Element:
                            Minedgevalue = min(Value,Minedgevalue)
                            Maxedgevalue = max(Value,Maxedgevalue)
        Alldata["Edges"]["Min"] = Minedgevalue
        Alldata["Edges"]["Max"] = Maxedgevalue
        return Alldata
    
class Dictgenerator(Generator):
    def __init__(self, graphname: str,nodes:dict(),edges:dict()):
        super().__init__(graphname)
        self._edges = edges
        self._nodes = {}
        for strkey,data in nodes.items():
            self._nodes[int(strkey)] = data