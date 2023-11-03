import pandas as pd
import json
import MoSiR.GraphGen as gf
import MoSiR.ImportInfo as ip

class InvalidOption(Exception):
    def __init__(self, message: str):    
        super().__init__(message)

# Json -----------------------------------------------------------------------

class ReportData():
    def __init__(self, directory):
        with open(directory, "r") as f: 
            self._DATA = json.load(f)
            
    def GetData(self):
        return self._DATA
            
    def GetOutputName(self):
        return [i for i in self.GetData()]
    
    def GetOutputData(self, OutputName: str):
        return self._DATA[OutputName]

def UnitChange(Number: float, From: str, To: str) -> float:
    F = From.lower()
    T = To.lower()
    if F == 'kgc':
        if T in ['tc', 'tco2eq']:
            return Number/1000
        elif T in ['kgc', 'w/m2']:
            return Number
        else: 
            raise InvalidOption(f"{To} n'est pas une option d'unité d'output \
                (tC, kgC, tCO2eq ou w/m2)")
    elif F == 'tc':
        if T in ['kgc', 'w/m2']:
            return Number * 1000
        elif T in ['tc', 'tco2eq']:
            return Number
        else: 
            raise InvalidOption(f"{To} n'est pas une option d'unité d'output \
                (tC, kgC, tCO2eq ou w/m2)")
    else:
        raise InvalidOption(f"{From} n'est pas une option d'unité d'input \
                            (kgC ou tC)") 
        
def OutputCreation(Graph: gf.GraphFactory, Import: ip.ImportData, 
                   Report: ReportData, Directory: str):
    """
    Fonction pour créer des outputs des résultats des calculs
    
    Args:
        Graph: La classe graph factory de GraphFactory.py
        Import: La classe ImportData du fichier d'import
        Report: La classe ReportData 
        Directory: Le dossier dans lequel les outputs seront enregistrés
    """
    #if '\\' in Directory:
    #    raise SyntaxError("Dans le output directory, il est nécessaire d'utiliser des\
    #        frontslash (/) et non des backslash (\) ")
        
    Time = Report.GetOutputData('Time')
    Ext = Report.GetOutputData('Output file extension')
    PRG = Report.GetOutputData('PRG')
    Output = Report.GetOutputData('Output')
    InputUnit = Import.GetUnit().lower()
    
    for GraphName in Output:
        Info = Output[GraphName]
        for output_name in Info:
            Data = Info[output_name]
            Nodes_name = Data['Nodes_name']
            Type = Data['Type']
            Summarize = Data['Summarize']
            ReportUnit = Data['Unit'].lower()
            if type(Data['Cumulative']) == bool:
                Cumu = Data['Cumulative']
            else: 
                raise InvalidOption(f"Cumulative ({Data['Cumulative']}) dans le fichier \
                                    de reporting doit être un booléen, donc soit 'true' ou 'false'")

            df = pd.DataFrame(columns = Nodes_name)
            df.insert(0, 'Time', None)

            G = Graph.GetGraph(GraphName)
            for Node in G.Nodes():
                if Node.NAME in Nodes_name:
                    for Timestep in range(Time + 1):
                        df.loc[Timestep, 'Time'] = Timestep
                        if Type == 'Flux in':
                            result = Node.GetFluxIn(G, Timestep, Cumulative = Cumu)
                            result = UnitChange(result, InputUnit, ReportUnit)
                            df.loc[Timestep, Node.NAME] = result
                        elif Type == 'Flux out':
                            result = Node.GetFluxOut(G, Timestep, Cumulative = Cumu)
                            result = UnitChange(result, InputUnit, ReportUnit)
                            df.loc[Timestep, Node.NAME] = result
                        elif Type == 'Stock':
                            result = Node.GetStock(G, Timestep, Cumulative = Cumu)
                            result = UnitChange(result, InputUnit, ReportUnit)
                            df.loc[Timestep, Node.NAME] = result
                        else:
                            raise InvalidOption(f"L'entrée <Type> ('{Type}') dans le \
                                reporting file n'est pas un choix valide. Choix \
                                possibles: 'Flux in', 'Flux out' ou 'Stock'.")
            if Summarize == 'Combined':
                df['Combined'] = df.drop('Time', axis = 1).sum(axis = 1)
                df = df[['Time', 'Combined']]
            df['Unit'] = ReportUnit
            if Directory[-1] == '/':
                df.to_csv(Directory + GraphName + '_' + output_name + Ext, 
                          index = False, sep = ',')
            elif Directory[-1] != '/':
                df.to_csv(Directory + '/' + GraphName + '_' + output_name + Ext, 
                          index = False, sep = ',')