
# coding: utf-8

# In[82]:

'''
[LICENSE]
Copyright (c) 2016, Ahmed Chaouachi
IREQ: Institut de Recherche d'Hydro Québec
All rights reserved.
[\LICENSE]
'''
MILE_TO_KM = 1.60934
#self.type = {'PQ':0, 'PQV':1, 'PV':2, 'SWING':3}
class Tbranch:
    '''
    The name of this class: T for Transmission , BRANCH for the link
    
    Attributes:
        params: a dictionnary where the KEYS are the names  defined below
         note: we expect len(keys) to return x 
        
        cdfNum      - number in the cdf file, Branch identifier.
                      Inter area branches are indicated by double letter ID.
                      Circuits on a common tower have hyphenated ID#.
        branchType               -  [1]simple link ,  [2] active link (transformer branches)
        fromBus                  - from bus
        toBus                    - to bus
        lengthMiles              - length in miles
        lengthKM                 - length in km
        outageRateYear           - Lam-p     =  Permanent Outage Rate (outages/year).
        outageDuration           - Dur       =  Permanent Outage Duration (Hours).
        outageTransientRateYear  - Transient Outage Rate (outages/year)
        R     - Resistance (p.u)
        X     - Reactance  (p.u)
        B     - Susceptance(p.u)
        contRating    - Continious rating (MVA)
        LTemergency   - (MVA) LTE       =  Long-time emergency rating  (24 hour).
        STemergency   - (MVA) STE       =  Short-time emergency rating (15 minute).
        TR            - (pu)   Tr       =  Transformer off-nominal Ratio.
                      |-------------------> Transformer branches are indicated by Tr != 0.


    '''
    # NUMBER OF branches IN THE TNETWROK
    B_SIZE          =0 # B_SIZE = ACTIVE_B_SIZE +  LINK_SIZE
    ACTIVE_B_SIZE   =0
    LINK_SIZE       =0  
    #def __init__(self, cdfNum, branchType, fromBus, toBus, lengthMiles, lengthKM=0,
    #             outageRateYear, outageDuration,  outageTransientRateYear, 
    #             R, X, B,
    #             contRating, LTemergency, STemergency, TR):
    def __init__(self, params):
        # THE IEEE CDF PROPERTIES: branch DATA
        self.cdfNum = params['cdfNum'] 
        if 'branchType' in params.keys() : self.branchType =params['branchType']
        if 'fromBus' in params.keys() :self.fromBus=params['fromBus']
        if 'toBus' in params.keys() : self.toBus=params['toBus']
        if 'lengthMiles' in params.keys() : self.lengthMiles=params['lengthMiles']
        if 'lengthKM' in params.keys() and 'lengthMiles' in params.keys() :
            if params['lengthKM'] == 0: self.lengthKM = params['lengthMiles'] * MILE_TO_KM
            else: self.lengthKM = params['lengthKM']
        if 'outageRateYear' in params.keys() :self.outageRateYear=params['outageRateYear']
        if 'outageDuration' in params.keys() :self.outageDuration=params['outageDuration']
        if 'outageTransientRateYear' in params.keys() :self.outageTransientRateYear = params['outageTransientRateYear']
        if 'R' in params.keys() :self.R=params['R']
        if 'X' in params.keys() :self.X=params['X']
        if 'B' in params.keys() :self.B=params['B']
        if 'contRating' in params.keys() :self.contRating= params['contRating']
        if 'LTemergency' in params.keys() :self.LTemergency= params['LTemergency']
        if 'STemergency' in params.keys() :self.STemergency= params['STemergency']
        if 'TR' in params.keys() :
            self.TR= params['TR']
            if self.TR == 0: Tbranch.LINK_SIZE +=1
            else: Tbranch.ACTIVE_B_SIZE +=1
        Tbranch.B_SIZE +=1
    def displayBranches():
        print ('The total number of branches is ', Tbranch.B_SIZE)
        print ('Active of branches: ', Tbranch.ACTIVE_B_SIZE)
        print ('Link branches ', Tbranch.LINK_SIZE)
            


# In[85]:

dict={'cdfNum':1}; dict2={'cdfNum':2, 'branchType':1}


# In[86]:

T=Tbranch(dict)


# In[88]:

T2=Tbranch(dict2)


# In[89]:

print (Tbranch.B_SIZE)


# In[90]:

Tbranch.displayBranches()


# In[ ]:



