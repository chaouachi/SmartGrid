
# coding: utf-8

# In[206]:

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


# In[207]:

import Treader
from coopr.pyomo import *
from pyomo.environ import *
from math import pi
import numpy as np
from numpy.lib.recfunctions import append_fields
#import importlib 
#importlib.reload(Treader)


# In[208]:

fNodes='Data/Tnodes.txt' # file of cdf nodes data
fBranches='Data/Tbranch.txt' # file of cdf branches data
fGenerators='Data/Tgenerators.txt' # file of cdf generators data: tab 7
fnSH = [5,5,29,53,5,29]     #file nodes skip header: number of lines
fnSF = [7,56,32,7,32,7]     #file nodes skip footer: number of lines -1
fbSH = [17,17,58,96,17,58]    #file branches skip header: number of lines
fbSF = [9,89,50,9,50,9]     #file branches skip footer: number of lines -1
fgSH = [5,5,38,71,5,38]     #file generators skip header: number of lines
fgSF = [3,69,36,3,36,3 ]    #file generators skip footer: number of lines -1

if __name__ == "__main__":
    import sys
    area=int(sys.argv[1])

area=5 # zone:0=ALL, i=zone i, i=1,2,3, 4:zone(1+2), 5:zone(2+3)
# Instantiate a reader with two cdf files for nodes and branches consicutively
R= Treader.Treader(fNodes, fBranches,fGenerators)
# Read nodes
R.tReadNodes(fnSH[area],fnSF[area])
#Read branches
R.tReadBranches(fbSH[area],fbSF[area])
#Read generators
R.tReadGenerators(fgSH[area],fgSF[area])
# nodes
n=R.cdfDataNodes
# branches
k=R.cdfDataBranches
# generators
g=R.cdfDataGenerators
#####################
# Smoothing params  #
#####################
deltaV=2e-1
epsilonV=1e-6
epsilonPgj=1e-6
epsilonPhiK=1e-6
epsilonC=1e-6
epsilonSparcity=1e-4
##########
# model  #
##########
model = ConcreteModel()


# #   indexes

# In[209]:

###########
# indexes #
###########
# nodes
def InitNodes(model):
    indexN=[]
    for i in n:
        indexN.append(i['cdfNum'])
    return indexN 
model.nodes=Set(initialize= InitNodes , doc='Nodes index: cdfNum')
# Neighbour nodes
def InitNeighbours(model, node):
    retval = []
    for link in k:
        if link['fromBus'] == node and link['toBus']  in model.nodes :
            retval.append( link['toBus'])
    return retval
model.neighbours=Set(model.nodes,initialize=InitNeighbours,doc='Neighbours of each node' )
#PQ busses :
def PQbus_rule(model):
    retval=[]
    for i in n:
        if i['busType']==1:
            retval.append(i['cdfNum'])
    return retval
model.PQbuses=Set(initialize=PQbus_rule,doc='PQ busses')
#PV busses :
def PVbus_rule(model):
    retval=[]
    for i in n:
        if i['busType']==2:
            retval.append(i['cdfNum'])
    return retval
model.PVbuses=Set(initialize=PVbus_rule,doc='PV busses')
#SWING busses:
def SWING_rule(model):
    retval=[]
    for i in n:
        if i['busType']==3:
            retval.append(i['cdfNum'])
    return retval
model.SWINGbuses=Set(initialize=SWING_rule,doc='SWING busses')

# Branches
def InitBranchesIndex(model):
    numB=[]
    for j in k:
        if j['fromBus'] in model.nodes and j['toBus'] in model.nodes:
            numB.append(j['cdfNum'])
    return numB
model.branches=Set(initialize=InitBranchesIndex, doc='cdfNum of ALL Branches: number in the cdf file, Branch identifier.                      Inter area branches are indicated by double letter ID.                      Circuits on a common tower have hyphenated ID#.' )
#PAssive Branches
def PassiveBranch_rule(model):
    retval=[]
    for j in k:
        if j['TR']==0 and j['cdfNum'] in model.branches :
            retval.append(j['cdfNum'])
    return retval
model.PassiveBranches=Set(initialize=PassiveBranch_rule, doc='Passive lines')
# Active Branches
def ActiveBranch_rule(model):
    retval=[]
    for j in k:
        if j['TR']!=0 and j['cdfNum'] in model.branches:
            retval.append(j['cdfNum'])
    return retval
model.ActiveBranches=Set(initialize=ActiveBranch_rule, doc='Active lines')
# Connected branches to each node
def InitConn(model,node):
    retval=[]
    for j in k:
        if j['fromBus']==node and j['cdfNum'] in model.branches:
            retval.append(j['cdfNum'])
    return retval
model.kp=Set(model.nodes,initialize=InitConn, doc='cdfNum of branches connected to ONE node' )
# Connected ACTIVE branches to each node
def InitConnActive(model,node):
    retval=[]
    for j in k:
        if j['fromBus']==node and j['cdfNum'] in model.ActiveBranches:
            retval.append(j['cdfNum'])
    return retval
def InitConnPassive(model,node):
    retval=[]
    for j in k:
        if j['fromBus']==node and j['cdfNum'] in model.PassiveBranches:
            retval.append(j['cdfNum'])
    return retval
model.kpActive=Set(model.nodes, initialize=InitConnActive, doc='cdfNum of Active branches connected to ONE node')
model.kpPassive=Set(model.nodes,initialize= InitConnPassive, doc='cdfNum of Passive branches connected to ONE node')
# generators
def InitGen_rule(self):
    retval=[]
    for l in g:
        if l['locBus'] in model.nodes:
            retval.append(l['genID'])
    return retval
model.generators=Set(initialize=InitGen_rule,doc='genrators index by name')
def InitNodeGens_rule(self,node):
    retval=[]
    for j in g:
        if j['locBus'] == node:
            retval.append(j['genID'])
    return retval
model.nodeGens=Set(model.nodes,initialize=InitNodeGens_rule, doc='Generators of each node')


# #   params  for busses

# In[210]:

def populateNodes_1(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busType']
model.busType=Param(model.nodes, initialize=populateNodes_1, default=-1, doc='[1]PQ ,  [2]PV, [3]SWING, [4]PQV' )
def populateNodes_2(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busName']
model.busName=Param(model.nodes, initialize=populateNodes_2, default='Unknown', doc='cdf bus name: Abel, Adams, etc.' )
def populateNodes_3(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busLoadMW']
model.busPload=Param(model.nodes, initialize=populateNodes_3, default=0, doc='cdf bus active load (MW).' )
def populateNodes_4(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busLoadMVAR']
model.busQload=Param(model.nodes, initialize=populateNodes_4, default=0, doc='cdf bus reactive load (MVAR).' )
def populateNodes_5(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busGL']
model.busGL=Param(model.nodes, initialize=populateNodes_5, default=0, doc='cdf real component of shunt admittance to ground.' ) 
def populateNodes_6(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busBL']
model.busBL=Param(model.nodes, initialize=populateNodes_6, default=0, doc='cdf imaginary component of shunt admittance to ground.' )
def populateNodes_7(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busKV']
model.busBaseKV=Param(model.nodes, initialize=populateNodes_7, default=0, doc='cdf base kV.')
def populateNodes_8(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busSubArea']
model.busSubArea=Param(model.nodes, initialize=populateNodes_8, default=0, doc='cdf base subArea: 11,12 21,22 31,32 ')
def populateNodes_9(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busArea']
model.busArea=Param(model.nodes, initialize=populateNodes_9, default=0, doc='cdf base Area: 1, 2 or 3.')
def populateNodes_10(model,node):
    for i in n:
        if i['cdfNum']==node:
            return i['busZone']
model.busZone=Param(model.nodes, initialize=populateNodes_10, default=0, doc='cdf base zone:                     cdf zones (area1: 11-17), (area2: 21-27) and (area3:31-37)')
def populateNodes_11(model,node):
    qmin=0
    for j in g:
        if j['locBus']==node:
            qmin += j['genQMIN']
    return qmin
model.busQMIN=Param(model.nodes,initialize=populateNodes_11,default=0,doc='Node QMIN')
def populateNodes_12(model,node):
    qmax=0
    for j in g:
        if j['locBus']==node:
            qmax += j['genQMAX']
    return qmax
model.busQMAX=Param(model.nodes,initialize=populateNodes_12,default=0,doc='Node QMAX')
def populateNodes_13(model,node):
    for j in g:
        if j['locBus']==node:
            return j['genVolt']
model.busVsetPoint=Param(model.nodes,initialize=populateNodes_13,default=1.0,doc='Node V set-point')


# # Generator params
# 
# 

# In[211]:

def populateGenerators_1(model,gen):
    for j in g:
        if j['genID']==gen:
            return j['locBus']
model.GenLocBus=Param(model.generators, initialize=populateGenerators_1, default=-1, doc='In which node this generator is located?' )
def populateGenerators_2(model,gen):
    for j in g:
        if j['genID']==gen:
            return j['genName']
#model.GenUnitNumber=Param(model.generators, initialize=populateGenerators_2, default="noname", doc='Name of the unit belonging to')
def populateGenerators_3(model,gen):
    for j in g:
        if j['genID']==gen:
            return j['genIdInBus']
model.GenIdInBus=Param(model.generators, initialize=populateGenerators_3, default=-1, doc='The generatos of each node are identified: 1,2, ..' )
def populateGenerators_4(model,gen):
    for j in g:
        if j['genID']==gen:
            return j['genPg']
model.GenPgSetPoint=Param(model.generators, initialize=populateGenerators_4, default=0.0, doc='Plannified Active power')
def populateGenerators_5(model,gen):
    for j in g:
        if j['genID']==gen:
            return j['genQg']
model.GenQgSetPoint=Param(model.generators, initialize=populateGenerators_5, default=0.0, doc='Plannified Reactive power')
def populateGenerators_6(model,gen):
    for j in g:
        if j['genID']==gen:
            return j['genQMIN']
model.GenQMIN=Param(model.generators, initialize=populateGenerators_6, default=0, doc='Minimum of Reactive power')
def populateGenerators_7(model,gen):
    for j in g:
        if j['genID']==gen:
            if model.busType[j['locBus']]==3:#slack bus
                return 10000
            return j['genQMAX']
model.GenQMAX=Param(model.generators, initialize=populateGenerators_7, default=0, doc='Maximum of Reactive power')
def populateGenerators_8(model,gen):
    for j in g:
        if j['genID']==gen:
            return j['genVolt']
model.GenVsetPoint=Param(model.generators,initialize=populateGenerators_8,default=0,doc='Voltage set point of each Generator')
def populateGenerators_9(model,gen):
    for j in g:
        if j['genID']==gen:
            if model.busType[j['locBus']]==3:#slack bus
                return 10000
            return j['genPg']*1.5 # TO DO: check the PMAX values
model.GenPMAX=Param(model.generators,initialize=populateGenerators_9,default=0,doc='Max Active Power capacity')


# #   params  for branches

# In[212]:

def populateBranches_1(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['fromBus']
model.BranchFrom=Param(model.branches, initialize=populateBranches_1, default=0, doc='from bus')
def populateBranches_18(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['toBus']
model.BranchTo=Param(model.branches, initialize=populateBranches_18, default=0, doc='to bus')
def populateBranches_17(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['lengthMiles']
model.BranchLengthMiles=Param(model.branches, initialize=populateBranches_17, default=0, doc='branch length in miles')
def populateBranches_16(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['outageRateYear']
model.BranchOutageRateYear=Param(model.branches, initialize=populateBranches_16, default=0, doc='Lam-p =  Permanent Outage Rate (outages/year).')
def populateBranches_15(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['outageDuration']
model.BranchOutageDuration=Param(model.branches, initialize=populateBranches_15, default=0, doc='Dur =  Permanent Outage Duration (Hours).')
def populateBranches_14(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['outageTransientRateYear']
model.BranchOutageTransientRateYear=Param(model.branches, initialize=populateBranches_14, default=0, doc='Transient Outage Rate (outages/year)')
def populateBranches_13(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['R']
model.BranchR=Param(model.branches, initialize=populateBranches_13, default=0, doc='Resistance (p.u)=1/G')
def populateBranches_12(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            if i['X'] ==0:
                return 999
            return 1/float(i['X'])
model.BranchG=Param(model.branches, initialize=populateBranches_12, default=0, doc='Conducance (p.u)=1/R')
def populateBranches_11(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            if i['X'] ==0:
                return 999
            return 1/float(i['X']) *0.5
model.BranchMING=Param(model.branches, initialize=populateBranches_11, default=0, doc='MIN Conducance (p.u)=1/R')
def populateBranches_10(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            if i['X'] ==0:
                return 999
            return 1/float(i['X']) *1.5
model.BranchMAXG=Param(model.branches, initialize=populateBranches_10, default=0, doc='MAX Conducance (p.u)=1/R')
def populateBranches_9(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['X']
model.BranchX=Param(model.branches, initialize=populateBranches_9, default=0, doc='Reactance (p.u)')

def populateBranches_8(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['B']
model.BranchB=Param(model.branches, initialize=populateBranches_8, default=0, doc='Susceptance (p.u)')
def populateBranches_7(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['contRating']
model.BranchContRating=Param(model.branches, initialize=populateBranches_7, default=0, doc='Continious rating (MVA)')
def populateBranches_6(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['LTemergency']
model.BranchLTemergency=Param(model.branches, initialize=populateBranches_6, default=0, doc='(MVA) LTE       =  Long-time emergency rating  (24 hour).')
def populateBranches_5(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['STemergency']
model.BranchSTemergency=Param(model.branches, initialize=populateBranches_5, default=0, doc='STemergency   - (MVA) STE       =  Short-time emergency rating (15 minute).')
def populateBranches_4(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['TR']
model.BranchTR=Param(model.branches, initialize=populateBranches_4, default=0, doc='- (pu)TR=  Transformer off-nominal Ratio. Transformer branches are indicated by Tr != 0.')
def populateBranches_3(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['B']*0.5
model.BranchMINB=Param(model.branches, initialize=populateBranches_3, default=0, doc='MIN Susceptance (p.u)')
def populateBranches_2(model,branch):
    for i in k:
        if i['cdfNum']==branch:
            return i['B']*1.5
model.BranchMAXB=Param(model.branches, initialize=populateBranches_2, default=0, doc='MAX Susceptance (p.u)')


# #   Variables
# 

# In[213]:

#x:state variable - c:control variable: !TO DO: bounds to be fixed later on!
#nodes
def init_xcv(model,node):
    if node in model.PQbuses:
        return model.busVsetPoint[node]
    return 1
model.xcV   =Var(model.nodes, initialize=init_xcv , domain=Reals ,bounds=(0.9 , 1.1), doc='Voltage magnitude on each node (p.u)' )
model.xTheta=Var(model.nodes, domain=Reals, bounds=(-pi,pi), doc='Voltage angle on each node (deg)')
def xQgLimits(model,node):
    return (model.busQMIN[node],model.busQMAX[node])
model.xQg   =Var(model.nodes, domain=Reals, bounds=xQgLimits,doc='Reactive power generation - state variable (MVAr)')
model.cPg   =Var(model.nodes, domain=NonNegativeReals,doc='Active power generation - control variable (MW)')
#branches
model.cPhi  =Var(model.branches, domain=Reals, bounds=(-pi,pi), doc='control var- phase shift (deg)')
model.cA    =Var(model.branches, domain=NonNegativeReals, bounds=(1,1), doc='control var- transformer branches                                                                                 params t=a exp^(jV)- decide on a (p.u)                                                                                =1 for non-active branches' )
model.xcTheta=Var(model.branches, domain=Reals, bounds=(-pi,pi), doc='Voltage angle difference on each branch (deg)')
def cBlimits(model,branch):
    return (model.BranchMINB[branch],model.BranchMAXB[branch])
model.cB    =Var(model.branches, domain=NonNegativeReals, bounds=cBlimits, doc='control var- susceptance of active branch (p.u)' )
def cGlimits(model,branch):
    return (model.BranchMING[branch],model.BranchMAXG[branch])
model.cG    =Var(model.branches, domain=NonNegativeReals, bounds=cGlimits, doc='control var- admittance of active branch (p.u)' )
#generators
def cPgjlimits(model,gen):
    return (0,model.GenPMAX[gen])
model.cPgj   =Var(model.generators, domain=NonNegativeReals, bounds=cPgjlimits,doc='Active power of each generator - control variable (MW)')
def xQgjlimits (model,gen):
    return (model.GenQMIN[gen], model.GenQMAX[gen])
model.xQgj   =Var(model.generators, domain=Reals, bounds=xQgjlimits,doc='Reactive power of each generator - control variable (MW)')
#model.xcVj   =Var(model.generators,domain=Reals, bounds=(0.9,1.1),doc='Volt of each Generator')


# # Constraints:

# In[214]:

# Full AC power fow constraints: active lines
#Active
def PassiveL_APF_rule(model,node):
    return model.xcV[node] * sum(                                 model.xcV[ model.BranchTo[l]]*                                  model.cG[l]* cos(model.xcTheta[l])+                                 model.cB[l]* sin(model.xcTheta[l])                                    for l in model.kpPassive[node]                                )                                - model.cPg[node] + model.busPload[node]==0                              
model.PassiveL_APF= Constraint(model.nodes, rule=PassiveL_APF_rule,                                doc='Passive line - Active component PF constraints')
#model.PassiveL_APF.deactivate()
# Reactive
def PassiveL_RPF_rule(model,node):
    return model.xcV[node] * sum(                                 model.xcV[ model.BranchTo[l]]*                                  model.cG[l]* sin(model.xcTheta[l])-                                 model.cB[l]* cos(model.xcTheta[l])                                    for l in model.kpPassive[node]                                )                                - model.xQg[node] + model.busQload[node]==0                                                           
model.PassiveL_RPF= Constraint(model.nodes, rule=PassiveL_RPF_rule,                                doc='Passive line - Reactive component PF constraints')
#model.PassiveL_RPF.deactivate()


# In[215]:

# Full AC power fow constraints: active lines
#Active component
def ActiveL_APF_rule(model,node):
    return model.xcV[node] * sum(                                 model.cA[l]**2 *                                 model.xcV[ model.BranchTo[l]]*                                  (model.cG[l]* cos(model.xcTheta[l])+                                 model.cB[l]* sin(model.xcTheta[l]) )                                    -  model.cA[l]**2 * model.cG[l] * model.xcV[node]**2                                for l in model.kpActive[node]                                )                                - model.cPg[node] + model.busPload[node]==0                              
model.ActiveL_APF= Constraint(model.nodes, rule=ActiveL_APF_rule,                                             doc='Active line - Active component PF constraints' )
#model.ActiveL_APF.deactivate()
# Reactive component 
def ActiveL_RPF_rule(model,node):
    return model.xcV[node] * sum(                                 model.cA[l]**2 *                                 model.xcV[ model.BranchTo[l]]*                                  (model.cG[l]* sin(model.xcTheta[l])-                                 model.cB[l]* cos(model.xcTheta[l]) )                                     +  model.cA[l]**2 * model.cG[l] * model.xcV[node]**2                                for l in model.kpActive[node]                                )                                - model.xQg[node] + model.busQload[node]==0                                                           
model.ActiveL_RPF= Constraint(model.nodes, rule=ActiveL_RPF_rule,                                    doc='Active line - Reactive component PF constraints' )
#model.ActiveL_RPF.deactivate()


# In[216]:

# Define the xcTheta [n,m] = xTheta[n] - xTheta[m] - cPhi[n,m]


# In[217]:

def AngleBranch_rule(model,branch):
#if model.BranchTR[branch] == 0: #  Transformer branches are indicated by Tr <> 0.
    return model.xcTheta[branch] == model.xTheta[model.BranchFrom[branch]] -            model.xTheta[model.BranchTo[branch]] - model.cPhi[branch]
#return model.xcTheta[branch] == model.xTheta[model.BranchFrom[branch]] - model.xTheta[model.BranchTo[branch]]
            
model.AngleBranch= Constraint(model.branches, rule=AngleBranch_rule)


# In[218]:

#Set the control variables to their nominal values according to the type of the bus


# In[219]:

# PQ bus: xQg=0 
def FixPQ1_rule(model,node):
#if model.busType[node] == 1:#PQ bus
    return model.xQg[node]==0 #NOT IF THE PQ is a generator with fixed output
#return Constraint.Skip
try:
    model.FixPQ1=Constraint(model.PQbuses,rule=FixPQ1_rule,doc='PQ bus: xQg=0 [hyp:load bus not a fixed output generator ]')
    model.FixPQ1.deactivate()
except:
    print('error')


# In[220]:

#PQ bus: cPg=0 
def FixPQ2_rule(model,node):
#if model.busType[node] == 1:#PQ bus
    return model.cPg[node]==0 #NOT IF THE PQ is a generator with fixed output
#return Constraint.Skip
try:
    model.FixPQ2=Constraint(model.PQbuses,rule=FixPQ1_rule,doc='PQ bus: cPg=0 [hyp:load bus not a fixed output generator ]')
    model.FixPQ2.deactivate()
except:
    print('error')


# In[221]:

#slack bus: xTheta=0
def FixSlack1_rule(model,node):
#if model.busType[node] == 3:#Slack
    return model.xTheta[node]==0 
#return Constraint.Skip
try:
    model.FixSlack1=Constraint(model.SWINGbuses,rule=FixSlack1_rule,doc='Slack bus: cPg=0')
except:
    print('error')


# In[222]:

#slack bus: xcV is known
def FixSlack2_rule(model,node):
#if model.busType[node] == 3:#Slack
    #return model.xcV[node]== model.busBaseKV[node]
    return model.xcV[node]==1
#return Constraint.Skip
try:
    model.FixSlack2=Constraint(model.SWINGbuses,rule=FixSlack2_rule,doc='Slack bus:xcV=Param(busBaseKV) ')
except:
    pass


# In[223]:

#Passive branches: model.cPhi =0
def FixPassiveBranch_rule(model,branch):
#if model.BranchTR[branch] == 0: #  Transformer branches are indicated by Tr != 0.
    return model.cPhi[branch]==0
#return Constraint.Skip
try:
    model.FixPassiveBranch_1=Constraint(model.PassiveBranches, rule=FixPassiveBranch_rule,doc='Passive branch: cPhi=0')
    #model.FixPassiveBranch_1.deactivate()
except:
    print('error')


# In[224]:

# Passive branch: cA=1
def FixPassiveBranch2_rule(model,branch):
#if model.BranchTR[branch] == 0: #  Transformer branches are indicated by Tr <> 0.
    return model.cA[branch] ==1
#return Constraint.Skip
try:
    model.FixPassiveBranch_2=Constraint(model.PassiveBranches, rule=FixPassiveBranch2_rule,doc='Passive branch: cA=1')
except:
    pass    


# In[225]:

# Passive branch: cG=1/R
def FixPassiveBranch3_rule(model,branch):
#if model.BranchTR[branch] == 0: #  Transformer branches are indicated by Tr <> 0.
    return model.cG[branch] == model.BranchG[branch]
#return Constraint.Skip
try:
    model.FixPassiveBranch_3=Constraint(model.PassiveBranches, rule=FixPassiveBranch3_rule,doc='Passive branch: cG=1/Param(R)')
except:
    pass 


# In[226]:

# Generation in a node is the sum of the generators


# In[227]:

def InitSumGensActive(model,node):
    return model.cPg[node] == sum(model.cPgj[j] for j in model.nodeGens[node])
model.sumGensActive=Constraint(model.PVbuses, rule=InitSumGensActive, doc='Sum Active Generation per node')


# In[228]:

def InitSumGensReactive(model,node):
    return model.xQg[node] == sum(model.xQgj[j] for j in model.nodeGens[node])
model.sumGensReactive=Constraint(model.PVbuses, rule=InitSumGensReactive, doc='Sum Active Generation per node')


# In[229]:

# Objective function: penalty term


# In[230]:

def Obj_Penalty_Constraints(model):
    c1=1.0/(float(len(model.nodes))*deltaV)
    c2=1.0/(float(len(model.generators)))
    c3=1.0/(float(len(model.branches))*pi)
    return c1*sum((model.xcV[node]- model.busVsetPoint[node] )**2 for node in model.PVbuses)         + c2*sum(((model.cPgj[gen] - model.GenPgSetPoint[gen])/max(epsilonPgj,model.GenPMAX[gen]))**2 for gen in model.generators)         + c3*sum((model.xcTheta[br])**2 for br in model.ActiveBranches)


# In[231]:

def Obj_Sparcity(model):
    return 1.0/float(len(model.branches))*sum( sqrt(( (model.cB[k] - model.BranchB[k])/max(epsilonC,model.BranchMAXB[k]-model.BranchMINB[k])  )**2+epsilonSparcity) for k in model.ActiveBranches )+1.0/float(len(model.branches))*sum( sqrt(( (model.cG[k] - model.BranchG[k])/max(epsilonC,model.BranchMAXG[k]-model.BranchMING[k])  )**2+epsilonSparcity) for k in model.ActiveBranches )+1.0/float(len(model.branches))*sum( sqrt(( model.cPhi[k] / pi  )**2+epsilonSparcity) for k in model.ActiveBranches) 


# In[232]:

def obj_both(model):
    return Obj_Penalty_Constraints(model)+Obj_Sparcity(model) 


# 

# In[233]:

model.obj=Objective(rule=obj_both, sense=minimize )


# for node in model.nodes:
#     print(node," : ")
#     for np in model.neighbours[node]:
#         print("    ",np)

# gen=0
# demand=0
# for i in model.generators:
#     gen += model.GenPMAX[i]
# for i in model.nodes:
#     demand+= model.busPload[i]
# print(demand)    
# print(gen)

# for i in model.nodes:
#     print (i)

# In[ ]:



