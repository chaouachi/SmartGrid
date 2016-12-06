
# coding: utf-8

# In[1]:

'''
    [LICENSE]
    Copyright (c) 2016, Ahmed Chaouachi
    IREQ: Institut de Recherche d'Hydro Québec
    All rights reserved.
    [/LICENSE]
    [OBJECTIF]
    This script contaisn the pyomo (PythonOptimModelling) model of the Topf: Transmission Optimal Power Flow
    [/OBJECTIF]
    
'''


import Treader
from pyomo.environ import *
from math import pi, cos, sin

fNodes='Data/Tnodes.txt' # file of cdf nodes data
fBranches='Data/Tbranch.txt' # file of cdf branches data
fnSH = 5     #file nodes skip header: number of lines
fnSF = 7     #file nodes skip footer: number of lines -1
fbSH = 17    #file branches skip header: number of lines
fbSF = 9     #file branches skip footer: number of lines -1

# Instantiate a reader with two cdf files for nodes and branches consicutively
R= Treader.Treader(fNodes, fBranches)
# Read nodes
R.tReadNodes(fnSH,fnSF)
#Read branches
R.tReadBranches(fbSH,fbSF)
##########
# model  #
##########
model = AbstractModel()


# #   indexes

# In[2]:

###########
# indexes #
###########
# nodes
n=R.cdfDataNodes
def InitNodes(model):
    indexN=[]
    for i in n:
        indexN.append(i['cdfNum'])
    return indexN 
model.nodes=Set(initialize= InitNodes , doc='Nodes index: cdfNum')
# branches
k=R.cdfDataBranches
def InitBranchesIndex(model):
    numB=[]
    for j in k:
        numB.append(j['cdfNum'])
    return numB
module.branchesIndex=Set(initialize=InitBranchesIndex, doc='cdfNum of Branches' )
def InitBranches(model):
    indexK=[]
    for j in k:
        indexK.append((j['fromBus'], j['toBus'], j['cdfNum'] ))
    return indexK
model.branches=Set(within=model.nodes*model.nodes*model.branchesIndex ,initialize=InitBranches,                    doc='Branches index (fromBus,toBus)',dimen=3)
# Neighbours 
def InitNeighbours(model, node):
    retval = []
    for link in k:
        if link['fromBus'] == node:
            retval.append( link['toBus'])
    return retval
model.neighbours=Param(model.nodes,initialize=InitNeighbours )


# #   params  for busses

# In[3]:


model.busType=Param(model.nodes, initialize=[], default='Unknown', doc='[1]PQ ,  [2]PV, [3]SWING, [4]PQV' )
model.busName=Param(model.nodes, initialize=[], default='Unknown', doc='cdf bus name: Abel, Adams, etc.' )
model.busPload=Param(model.nodes, initialize=[], default=0, doc='cdf bus active load (MW).' )
model.busQload=Param(model.nodes, initialize=[], default=0, doc='cdf bus reactive load (MVAR).' )
model.busGL=Param(model.nodes, initialize=[], default=0, doc='cdf real component of shunt admittance to ground.' ) 
model.busBL=Param(model.nodes, initialize=[], default=0, doc='cdf imaginary component of shunt admittance to ground.' )
model.busBaseKV=Param(model.nodes, initialize=[], default=0, doc='cdf base kV.')
model.busSubArea=Param(model.nodes, initialize=[], default=0, doc='cdf base subArea: 11,12 21,22 31,32 ')
model.busArea=Param(model.nodes, initialize=[], default=0, doc='cdf base Area: 1, 2 or 3.')
model.busZone=Param(model.nodes, initialize=[], default=0, doc='cdf base zone:                     cdf zones (area1: 11-17), (area2: 21-27) and (area3:31-37)')
def populateNodes(model,node):
    for i in n:
        if i['cdfNum']==node:
            model.busType.add(i['busType'])
            model.busName.add( i['busName'])
            model.busPload.add(i['busLoadMW'])
            model.busQload.add(i['busLoadMVAR'])
            model.busGL.add(i['busGL'])
            model.busBL.add(i['busBL'])
            model.busBaseKV.add(i['busKV'])
            model.busArea.add(i['busArea'])
            model.busSubArea.add(i['busSubArea'])
            model.busZone.add(i['busZone'])
model.getNodesParam=BuildAction(rule = populateNodes)


# # Other alternative:
# def InitBusType(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busType']
# 
# model.busType=Param(model.nodes, initialize=InitBusType, default='Unknown', doc='[1]PQ ,  [2]PV, [3]SWING, [4]PQV' )
# 
# def InitBusName(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busName']
# model.busName=Param(model.nodes, initialize=InitBusName, default='Unknown', doc='cdf bus name: Abel, Adams, etc.' )
# 
# def InitbusLoadMW(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busLoadMW']
# model.busPload=Param(model.nodes, initialize=InitbusLoadMW, default=0, doc='cdf bus active load (MW).' )
# 
# def InitbusLoadMVAR(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busLoadMVAR']
# model.busQload=Param(model.nodes, initialize=InitbusLoadMVAR, default=0, doc='cdf bus reactive load (MVAR).' )
# 
# def InitbusGL(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busGL']
# model.busGL=Param(model.nodes, initialize=InitbusGL, default=0, doc='cdf real component of shunt admittance to ground.' )
# 
# def InitbusBL(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busBL']
# model.busBL=Param(model.nodes, initialize=InitbusGL, default=0, doc='cdf imaginary component of shunt admittance to ground.' )
# 
# def InitbusKV(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busKV']
# model.busBaseKV=Param(model.nodes, initialize=InitbusKV, default=0, doc='cdf base kV.')
# 
# def InitbusArea(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busArea']
# model.busArea=Param(model.nodes, initialize=InitbusArea, default=0, doc='cdf base Area: 1, 2 or 3.')
# 
# def InitbusSubArea(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busSubArea']
# model.busSubArea=Param(model.nodes, initialize=InitbusSubArea, default=0, doc='cdf base subArea: 11,12 21,22 31,32 ')
# 
# def InitbusZone(model,node):
#     for i in n:
#         if i['cdfNum']==node:
#             return i['busZone']
# model.busZone=Param(model.nodes, initialize=InitbusZone, default=0, doc='cdf base zone: \
#                     cdf zones (area1: 11-17), (area2: 21-27) and (area3:31-37)')
# 

# #   params  for branches

# In[4]:

model.BranchCdfNum=Param(model.branches, initialize=[], default="Unknown", doc='number in the cdf file, Branch identifier.                      Inter area branches are indicated by double letter ID.                      Circuits on a common tower have hyphenated ID#.')
model.BranchFrom=Param(model.branches, initialize=[], default=0, doc='from bus')
model.BranchTo=Param(model.branches, initialize=[], default=0, doc='to bus')
model.BranchLengthMiles=Param(model.branches, initialize=[], default=0, doc='branch length in miles')
model.BranchOutageRateYear=Param(model.branches, initialize=[], default=0, doc='Lam-p =  Permanent Outage Rate (outages/year).')
model.BranchOutageDuration=Param(model.branches, initialize=[], default=0, doc='Dur =  Permanent Outage Duration (Hours).')
model.BranchOutageTransientRateYear=Param(model.branches, initialize=[], default=0, doc='Transient Outage Rate (outages/year)')
model.BranchR=Param(model.branches, initialize=[], default=0, doc='Resistance (p.u)')
model.BranchX=Param(model.branches, initialize=[], default=0, doc='Reactance (p.u)')
model.BranchB=Param(model.branches, initialize=[], default=0, doc='Susceptance (p.u)')
model.BranchContRating=Param(model.branches, initialize=[], default=0, doc='Continious rating (MVA)')
model.BranchLTemergency=Param(model.branches, initialize=[], default=0, doc='(MVA) LTE       =  Long-time emergency rating  (24 hour).')
model.BranchSTemergency=Param(model.branches, initialize=[], default=0, doc='STemergency   - (MVA) STE       =  Short-time emergency rating (15 minute).')
model.BranchTR=Param(model.branches, initialize=[], default=0, doc='- (pu)   Tr       =  Transformer off-nominal Ratio.                       |-------------------> Transformer branches are indicated by Tr != 0.')

def populateBranches(model,branch):
    (l,m)=branch
    for i in k:
        if i['fromBus']==l and i['toBus']==branch[1] :
            model.BranchCdfNum.add(i['cdfNum'])
            model.BranchFrom.add(i['fromBus'])
            model.BranchTo.add(i['toBus'])
            model.BranchLengthMiles.add(i['lengthMiles'])
            model.BranchOutageRateYear.add(i['outageRateYear'])
            model.BranchOutageDuration.add(i['outageDuration'])
            model.BranchOutageTransientRateYear.add(i['outageTransientRateYear'])
            model.BranchR.add(i['R'])
            model.BranchX.add(i['X'])
            model.BranchB.add(i['B'])
            model.BranchContRating.add(i['contRating'])
            model.BranchLTemergency.add(i['LTemergency'])
            model.BranchSTemergency.add(i['STemergency'])
            model.BranchTR.add(i['TR'])
model.getBranchesParam=BuildAction(rule=populateBranches)


# #   Variables
# 

# In[5]:

#x:state variable - c:control variable
# Voltage xV
model.xcV   =Var(model.nodes, domain=Reals ,bounds=(0.9 , 1.1), doc='Voltage magnitude on each node (p.u)' )
model.xTheta=Var(model.nodes, domain=Reals, bounds=(-pi,pi), doc='Voltage angle on each node (deg)')
model.xQg   =Var(model.nodes, domain=NonNegativeReals, bounds=(1,2),doc='Reactive power generation - state variable (MVAr)')
model.cPg   =Var(model.nodes, domain=NonNegativeReals, bounds=(1,2),doc='Active power generation - control variable (MW)')
model.cPhi  =Var(model.branches, domain=Reals, bounds=(-pi,pi), doc='control var- phase shift (deg)')
model.cA    =Var(model.branches, domain=NonNegativeIntegers, bounds=(1,2), doc='control var- transformer branches                                                                                 params t=a exp^(jV)- decide on a (p.u)                                                                                =1 for non-active branches' )
model.xcTheta=Var(model.branches, domain=Reals, bounds=(-pi,pi), doc='Voltage angle difference on each branch (deg)')
model.cB    =Var(model.branches, domain=NonNegativeReals, bounds=(1,2), doc='control var- susceptance of active branch (p.u)' )
model.cG    =Var(model.branches, domain=NonNegativeReals, bounds=(1,2), doc='control var- admittance of active branch (p.u)' )


# # Constraints:

# In[6]:

# Full AC power fow constraints
#Active
def ActivepowerFlow_rule(model,node):
    return model.xcV[node]*sum(model.xcV[m]* ( model.cG[node,m] * cos(model.xcTheta[node,m] ) +           model.BranchB[node,m]*sin(model.xcTheta[node,m]))            for m in model.neighbours[node]) -            model.cPg[node] + model.busPload[node]==0                              
model.ActivePowerFlow= Constraint(model.nodes, rule=ActivepowerFlow_rule)
# Reactive
def ReactivepowerFlow_rule(model,node):
    return model.xcV[node]*sum(model.xcV[m]* ( model.cG[node,m] * sin(model.xcTheta[node,m] ) -           model.BranchB[node,m]*cos(model.xcTheta[node,m]))            for m in model.neighbours[node]) -            model.xQg[node] + model.busQload[node]==0                              
model.ReactivePowerFlow= Constraint(model.nodes, rule=ReactivepowerFlow_rule)


# In[7]:

# Define the xcTheta [n,m] = xTheta[n] - xTheta[m] - cPhi[n,m]


# In[8]:

def AngleBranch_rule(model,branch):
    return model.xcTheta[branch] == model.xTheta[model.BranchFrom[branch]] -            model.xTheta[model.BranchTo[branch]] - model.cPhi[branch]
model.AngleBranch= Constraint(model.branches, rule=AngleBranch_rule)


# 

# In[ ]:



