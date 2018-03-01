# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 14:09:13 2018

@author: tcvandongen

This is an attempt to read the model data from excel into format needed for simple LP model

Rules w.r.t. the data:
    1. First sheets should be sets, then parameters
    2. If an element is not declared the parameter will be emptied (and error printed to screen)
"""

import pandas as pd
import pulp
import itertools

DataPath = "C:\\Users\\tcvandongen\\Desktop\\Project X\\Network Optimisation\\ModelData (shortage).xlsx"

# Read the entire excel file in a dataframe
xl = pd.ExcelFile(DataPath)
SheetsToRead = xl.sheet_names

df = pd.read_excel(DataPath, SheetsToRead)

ModelData = {}

# Now we loop through the sheets
for i in SheetsToRead:
    # Determine headernames
    a = df[i].columns
    
    if a.size == 1: # We are looking at a set
        indexlist = []
        
        for k in range(0,df[i].shape[0]):
            indexlist.append(df[i].iloc[k][0])
        
        ModelData[a[0]] = indexlist
    else:
        # Create dictionary with indices as key and parameter as value
        tmpDict = {}
        
        for j in range(0,df[i].shape[0]):       # Loop over rows starting from row 1
            indexlist = []
            
            for k in range(0,a.size-1):         # Loop through columns to determine index values
                indexlist.append(df[i].iloc[j][k])
            
            key = tuple(indexlist)
            tmpDict[key] = df[i].iloc[j][a.size-1]
            
        if a[a.size-1] in ModelData:            # Merge existing dictionary with new one
            tmpDict = {**ModelData[a[a.size-1]] ,**tmpDict}
    
#        print("Added: "+a[a.size-1])
        ModelData[a[a.size-1]] = tmpDict
        
       
## Retrieve the set elements from the data
if 'TimePeriods' in ModelData:
    TimePeriods = ModelData['TimePeriods']
else:
    TimePeriods = []

if 'TimePeriodGroups' in ModelData:
    TimePeriodGroups = ModelData['TimePeriodGroups']
else:
    TimePeriodGroups = []

AllTimePeriods = TimePeriods + TimePeriodGroups

if 'Locations' in ModelData:
    Locations = ModelData['Locations']
else:
    Locations = []
    
if 'LocationGroups' in ModelData:
    LocationGroups = ModelData['LocationGroups']
else:
    LocationGroups = []

Locations.remove("Depot2")
Locations.remove("Customer2")
Locations.remove("Customer3")
Locations.remove("Customer4")
Locations.remove("Customer5")

AllLocations = Locations + LocationGroups

if 'ProductionUnits' in ModelData:
    ProductionUnits = ModelData['ProductionUnits']
else:
    ProductionUnits = []

if 'ProductionUnitGroups' in ModelData:
    ProductionUnitGroups = ModelData['ProductionUnitGroups']
else:
    ProductionUnitGroups = []

AllProductionUnits = ProductionUnits + ProductionUnitGroups

if 'Streams' in ModelData:
    Streams = ModelData['Streams']
else:
    Streams = []

if 'StreamGroups' in ModelData:
    StreamGroups = ModelData['StreamGroups']
else:
    StreamGroups = []
    
AllStreams = Streams + StreamGroups

## Reading the data
def ReadingTheData(key, data, sets, optional = None):
    if key in data:
        parameter = data[key]
        if optional != None:
            parameter = Populate(parameter, sets, optional)
        parameter = RemoveUndeclaredIndices(parameter, sets)
    else:
        parameter = {}
    return parameter

## Checking the data
def RemoveUndeclaredIndices(pParameter,sListOfSets):
    UndeclaredIndices = []
    for x in pParameter:
        for k in range(0,len(x)):
            if (x[k] not in sListOfSets[k]):
                UndeclaredIndices.append(x)
    for y in UndeclaredIndices:
        if y in pParameter:
            print(str(y)+" will be deleted as one of the indices has not been declared in its set.")
            del pParameter[y]
    return pParameter

def Populate(pParameter,sListOfSets,sListOfPopulates):
    NewParameter = {}
    for x in pParameter:
        IndicesToPopulate = []
        for k in range(0,len(x)):
            if (str(x[k])[0:6] == "forall"):
                GroupToPopulate = str(x[k])[7:]
                y = [z for z in sListOfSets[k] if (sListOfPopulates[k].get(tuple([z,GroupToPopulate])) == 1)]
            else:
                GroupToPopulate = x[k]
                y = [x[k]]
            IndicesToPopulate.append(y)
        PopulatedIndices = list(itertools.product(*IndicesToPopulate))
        for i in PopulatedIndices:
            NewParameter[i] = pParameter[x]
    return NewParameter
    

# Read the groups
TimePeriodGroup = ReadingTheData('TimePeriodGroup', ModelData, [TimePeriods, TimePeriodGroups])
for item in TimePeriods:
    TimePeriodGroup[tuple([item,item])] = 1

LocationGroup = ReadingTheData('LocationGroup', ModelData, [Locations, LocationGroups])
for item in Locations:
    LocationGroup[tuple([item,item])] = 1

ProductionUnitGroup = ReadingTheData('ProductionUnitGroup', ModelData, [ProductionUnits, ProductionUnitGroups])
for item in ProductionUnits:
    ProductionUnitGroup[tuple([item,item])] = 1
    
StreamGroup = ReadingTheData('StreamGroup', ModelData, [Locations, LocationGroups])
for item in Streams:
    StreamGroup[tuple([item,item])] = 1


# Read the parameters
ModelData['SupplyCost'] = ReadingTheData('SupplyCost', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup]) 
ModelData['MinSupply'] = ReadingTheData('MinSupply', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])
ModelData['MaxSupply'] = ReadingTheData('MaxSupply', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])
ModelData['MinTransport'] = ReadingTheData('MinTransport', ModelData, [AllTimePeriods, AllLocations, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, LocationGroup, StreamGroup])
ModelData['MaxTransport'] = ReadingTheData('MaxTransport', ModelData, [AllTimePeriods, AllLocations, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, LocationGroup, StreamGroup])
ModelData['CostTransport'] = ReadingTheData('CostTransport', ModelData, [AllTimePeriods, AllLocations, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, LocationGroup, StreamGroup])
ModelData['MinDemand'] = ReadingTheData('MinDemand', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])
ModelData['MaxDemand'] = ReadingTheData('MaxDemand', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])
ModelData['PriceDemand'] = ReadingTheData('PriceDemand', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])
ModelData['Yield'] = ReadingTheData('Yield', ModelData, [AllTimePeriods, AllLocations, AllProductionUnits, AllStreams], [TimePeriodGroup, LocationGroup, ProductionUnitGroup, StreamGroup])
ModelData['MinProduction'] = ReadingTheData('MinProduction', ModelData, [AllTimePeriods, AllLocations, AllProductionUnits, AllStreams], [TimePeriodGroup, LocationGroup, ProductionUnitGroup, StreamGroup]) 
ModelData['MaxProduction'] = ReadingTheData('MaxProduction', ModelData, [AllTimePeriods, AllLocations, AllProductionUnits, AllStreams], [TimePeriodGroup, LocationGroup, ProductionUnitGroup, StreamGroup])
ModelData['MinInventory'] = ReadingTheData('MinInventory', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])
ModelData['MaxInventory'] = ReadingTheData('MaxInventory', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])
ModelData['CostInventory'] = ReadingTheData('CostInventory', ModelData, [AllTimePeriods, AllLocations, AllStreams], [TimePeriodGroup, LocationGroup, StreamGroup])


def SolveModel(ModelData, ShortageMode):
    
    ## Create the model
    if ShortageMode == 0:
        model = pulp.LpProblem("Network Optimisation", pulp.LpMaximize)
    elif ShortageMode == 1:
        model = pulp.LpProblem("Network Optimisation Shortage Model", pulp.LpMinimize)
    
    # Create the variables supply, transport & demand
    
    # Supply
    vSupply = pulp.LpVariable.dicts("Supply",(i for i in ModelData['SupplyCost']), lowBound = 0, cat='Continuous')
    
    # Transport
    vTransport = pulp.LpVariable.dicts("Transport",(i for i in ModelData['CostTransport']), lowBound = 0, cat='Continuous')
    
    # Production
    ProductionUnitsInLocations = set()
    for i in ModelData['Yield']:
        j = list(i)
        j.pop(-1)
        ProductionUnitsInLocations.add(tuple(j))
        
    ## Create variable 
    vProcessed = pulp.LpVariable.dicts("Processed",(i for i in ProductionUnitsInLocations), lowBound = 0, cat='Continuous')
    vConsumed = pulp.LpVariable.dicts("Consumed",(i for i in ModelData['Yield'] if ModelData['Yield'][i] < 0), lowBound = 0, cat='Continuous')
    vProduced = pulp.LpVariable.dicts("Produced",(i for i in ModelData['Yield'] if ModelData['Yield'][i] > 0), lowBound = 0, cat='Continuous')
    
    ## Demand
    vDemand = pulp.LpVariable.dicts("Demand",(i for i in ModelData['PriceDemand']), lowBound = 0, cat='Continuous')
    
    ## Inventory
    vInventory = pulp.LpVariable.dicts("Inventory",(i for i in ModelData['CostInventory']), lowBound = 0, cat='Continuous')

    
    ## Create shortage/surplus variables
    if (ShortageMode == 1):
        vShortageMinSupply = pulp.LpVariable.dicts("ShortageMinSupply",(i for i in ModelData['MinSupply']), lowBound = 0, cat='Continuous')
        vShortageMaxSupply = pulp.LpVariable.dicts("ShortageMaxSupply",(i for i in ModelData['MaxSupply']), lowBound = 0, cat='Continuous')
        vShortageMinDemand = pulp.LpVariable.dicts("ShortageMinDemand",(i for i in ModelData['MinDemand']), lowBound = 0, cat='Continuous')
        vShortageMaxDemand = pulp.LpVariable.dicts("ShortageMaxDemand",(i for i in ModelData['MaxDemand']), lowBound = 0, cat='Continuous')
        vShortageMinTransport = pulp.LpVariable.dicts("ShortageMinTransport",(i for i in ModelData['MinTransport']), lowBound = 0, cat='Continuous')
        vShortageMaxTransport = pulp.LpVariable.dicts("ShortageMaxTransport",(i for i in ModelData['MaxTransport']), lowBound = 0, cat='Continuous')
        vShortageMinProduction = pulp.LpVariable.dicts("ShortageMinProduction",(i for i in ModelData['MinProduction']), lowBound = 0, cat='Continuous')
        vShortageMaxProduction = pulp.LpVariable.dicts("ShortageMaxProduction",(i for i in ModelData['MaxProduction']), lowBound = 0, cat='Continuous')
        vShortageMinInventory = pulp.LpVariable.dicts("ShortageMinInventory",(i for i in ModelData['MinInventory']), lowBound = 0, cat='Continuous')
        vShortageMaxInventory = pulp.LpVariable.dicts("ShortageMaxInventory",(i for i in ModelData['MaxInventory']), lowBound = 0, cat='Continuous')
        ShortageMinSupply = vShortageMinSupply
        ShortageMaxSupply = vShortageMaxSupply
        ShortageMinDemand = vShortageMinDemand
        ShortageMaxDemand = vShortageMaxDemand
        ShortageMinTransport = vShortageMinTransport
        ShortageMaxTransport = vShortageMaxTransport
        ShortageMinProduction = vShortageMinProduction
        ShortageMaxProduction = vShortageMaxProduction
        ShortageMinInventory = vShortageMinInventory
        ShortageMaxInventory = vShortageMaxInventory
    else:
        ShortageMinSupply = {x: 0 for x in ModelData['MinSupply']}
        ShortageMaxSupply = {x: 0 for x in ModelData['MaxSupply']}
        ShortageMinDemand = {x: 0 for x in ModelData['MinDemand']}
        ShortageMaxDemand = {x: 0 for x in ModelData['MaxDemand']}
        ShortageMinTransport = {x: 0 for x in ModelData['MinTransport']}
        ShortageMaxTransport = {x: 0 for x in ModelData['MaxTransport']}
        ShortageMinProduction = {x: 0 for x in ModelData['MinProduction']}
        ShortageMaxProduction = {x: 0 for x in ModelData['MaxProduction']}
        ShortageMinInventory = {x: 0 for x in ModelData['MinInventory']}
        ShortageMaxInventory = {x: 0 for x in ModelData['MaxInventory']}
    
    # Create the model constraints
    for x in ModelData['MinSupply']:
        check = [vSupply[z] for z in vSupply if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vSupply[z] for z in vSupply if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))) >= ModelData['MinSupply'][x] - ShortageMinSupply[x]
        else:
            print("MinSupply could not be declared for: "+str(x)+". Check if SupplyCost has been specified for these indices.")
    
    for x in ModelData['MaxSupply']:
        check = [vSupply[z] for z in vSupply if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vSupply[z] for z in vSupply if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))) <= ModelData['MaxSupply'][x] + ShortageMaxSupply[x]
        else:
            print("MaxSupply could not be declared for: "+str(x)+". Check if SupplyCost has been specified for these indices.")
            
    for x in ModelData['MinDemand']:
        check = [vDemand[z] for z in vDemand if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vDemand[z] for z in vDemand if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))) >= ModelData['MinDemand'][x] - ShortageMinDemand[x]
        else:
            print("MinDemand could not be declared for: "+str(x)+". Check if PriceDemand has been specified for these indices.")
        
    for x in ModelData['MaxDemand']:
        check = [vDemand[z] for z in vDemand if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vDemand[z] for z in vDemand if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))) <= ModelData['MaxDemand'][x] + ShortageMaxDemand[x]
        else:
            print("MaxDemand could not be declared for: "+str(x)+". Check if PriceDemand has been specified for these indices.")
    
    for x in ModelData['MinTransport']:
        check = [vTransport[z] for z in vTransport if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in LocationGroup) and (tuple([z[3],x[3]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vTransport[z] for z in vTransport if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in LocationGroup) and (tuple([z[3],x[3]]) in StreamGroup))) >= ModelData['MinTransport'][x] - ShortageMinTransport[x]
        else:
            print("MinTransport could not be declared for: "+str(x)+". Check if CostTransport has been specified for these indices.")
    
    for x in ModelData['MaxTransport']:
        check = [vTransport[z] for z in vTransport if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in LocationGroup) and (tuple([z[3],x[3]]) in StreamGroup))]
        print(check)
        if len(check) > 0:
            model += pulp.lpSum(vTransport[z] for z in vTransport if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in LocationGroup) and (tuple([z[3],x[3]]) in StreamGroup))) <= ModelData['MaxTransport'][x] + ShortageMaxTransport[x]
        else:
            print("MaxTransport could not be declared for: "+str(x)+". Check if CostTransport has been specified for these indices.")
    
    for x in ModelData['MinInventory']:
        check = [vInventory[z] for z in vInventory if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vInventory[z] for z in vInventory if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))) >= ModelData['MinInventory'][x] - ShortageMinInventory[x]
        else:
            print("MinInventory could not be declared for: "+str(x)+". Check if InventoryCost has been specified for these indices.")
            
    for x in ModelData['MaxInventory']:
        check = [vInventory[z] for z in vInventory if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vInventory[z] for z in vInventory if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in StreamGroup))) <= ModelData['MaxInventory'][x] + ShortageMaxInventory[x]
        else:
            print("MaxInventory could not be declared for: "+str(x)+". Check if InventoryCost has been specified for these indices.")
            
    for y in ModelData['Yield']:
        CorrespondingUnit = tuple(list(y)[0:3])
        if ModelData['Yield'][y] > 0:
            model += vProduced[y] == vProcessed[CorrespondingUnit] * ModelData['Yield'][y]
        else:
            model += vConsumed[y] == vProcessed[CorrespondingUnit] * -ModelData['Yield'][y]
            
    for x in ModelData['MinProduction']:
        check = [vProduced[z] for z in vProduced if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in ProductionUnitGroup) and (tuple([z[3],x[3]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vProduced[z] for z in vProduced if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in ProductionUnitGroup) and (tuple([z[3],x[3]]) in StreamGroup))) >= ModelData['MinProduction'][x] - ShortageMinProduction[x]
        else:
            print("MinProduction could not be declared for: "+str(x)+". Check if Yield has been specified for these indices.")
            
    for x in ModelData['MaxProduction']:
        check = [vProduced[z] for z in vProduced if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in ProductionUnitGroup) and (tuple([z[3],x[3]]) in StreamGroup))]
        if len(check) > 0:
            model += pulp.lpSum(vProduced[z] for z in vProduced if ((tuple([z[0],x[0]]) in TimePeriodGroup) and (tuple([z[1],x[1]]) in LocationGroup) and (tuple([z[2],x[2]]) in ProductionUnitGroup) and (tuple([z[3],x[3]]) in StreamGroup))) <= ModelData['MaxProduction'][x] + ShortageMaxProduction[x]
        else:
            print("MaxProduction could not be declared for: "+str(x)+". Check if Yield has been specified for these indices.")
            
    # Create the balance constraint
    for t in TimePeriods:
        if TimePeriods.index(t) > 0:
            t2 = TimePeriods[TimePeriods.index(t) - 1]
            print("t = "+t+" and t2 = "+t2)
        else:
            t2 = "x"
        for l in Locations:
            for s in Streams:
                model += sum(vSupply[z] for z in vSupply if (z[0] == t and z[1] == l and z[2] == s)) + sum(vTransport[z] for z in vTransport if (z[0] == t and z[2] == l and z[3] == s)) + sum(vProduced[z] for z in vProduced if (z[0] == t and z[1] == l and z[3] == s)) + sum(vInventory[z] for z in vInventory if (z[0] == t2 and z[1] == l and z[2] == s)) == sum(vDemand[z] for z in vDemand if (z[0] == t and z[1] == l and z[2] == s)) + sum(vTransport[z] for z in vTransport if (z[0] == t and z[1] == l and z[3] == s)) + sum(vConsumed[z] for z in vConsumed if (z[0] == t and z[1] == l and z[3] == s)) + sum(vInventory[z] for z in vInventory if (z[0] == t and z[1] == l and z[2] == s))

    # Create the model objective
    if ShortageMode == 0:
        model += pulp.lpSum([-ModelData['SupplyCost'][x]*vSupply[x] for x in ModelData['SupplyCost']] + [ModelData['PriceDemand'][x]*vDemand[x] for x in ModelData['PriceDemand']] + [-ModelData['CostTransport'][x]*vTransport[x] for x in ModelData['CostTransport']] + [-ModelData['CostInventory'][x]*vInventory[x] for x in ModelData['CostInventory']])
    elif ShortageMode == 1:
        print("New objective")
   
        
    model.solve()

    for v in model.variables():
        print(v.name, "=", v.varValue)
        
    print(model)
    
    return pulp.LpStatus[model.status]

Status = SolveModel(ModelData, 0)
print(Status)

if Status != "Optimal":
    Status = SolveModel(ModelData, 1)


