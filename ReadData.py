# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 14:09:13 2018

@author: tcvandongen

This is an attempt to read the model data from excel into format needed for simple LP model
"""

import pandas as pd

SheetsToRead = ["Supply","TransportPrimary","Depots","TransportSecondary","Customers"]
DataPath = "C:\\Users\\tcvandongen\\Desktop\\Project X\\Network Optimisation\\ModelData.xlsx"
#data = pd.read_excel(DataPath, SheetsToRead,header = 1,index_col =1)

# Read the entire excel file in a dataframe
df = pd.read_excel(DataPath,SheetsToRead)

ModelData = {}

# Now we loop through the sheets
for i in SheetsToRead:
    # Determine headernames
    a = df[i].columns
    
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

    print("Added: "+a[a.size-1])
    ModelData[a[a.size-1]] = tmpDict
        
print("This should be all the modeldata")
print(ModelData)
#
#a = df.columns
#print(a[0])
#
#print(df['Location'])
#print(df['MaxSupply'])
#
#for i in a:
#    print(df[i])
#    
#print(df.iloc[1])
#
#MaxSupply = {}
#
#print(MaxSupply)
#
#print(df.shape[0])
#    
#for i in range(0, df.shape[0]):
#    print(df.iloc[i][0])
#    print(df.iloc[i][1])
#    MaxSupply[df.iloc[i][0]]=df.iloc[i][1]
#    
#    
#print(MaxSupply)
    
#print(df[0])


    

#xlsx = pd.ExcelFile(DataPath)
#sheet1 = xlsx.parse(0)
#
#column = sheet1.icol(0).real
#
#print(column)

#print(df.head())




#xl_file = pd.ExcelFile("C:\\Users\\tcvandongen\\Desktop\\Project X\\Network Optimisation\\ModelData.xlsx")
#
#dfs = {sheet_name: xl_file.parse(sheet_name) 
#          for sheet_name in xl_file.sheet_names}