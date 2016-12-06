
# coding: utf-8

# In[ ]:

'''
[LICENSE]
Copyright (c) 2016, Ahmed Chaouachi
IREQ: Institut de Recherche d'Hydro Québec
All rights reserved.
[/LICENSE]
[OBJECTIF]
[/OBJECTIF]

'''
#self.type = {'PQ':0, 'PQV':1, 'PV':2, 'SWING':3}
class Tnode:
    '''
    The name of this class: T for Transmission , node for node
    This is a mother class of the classes TnodePQ, TnodePV, TnodePQV, TnodeSWING
    
    Attributes:
        cdfNum      - number in the cdf file
        busType     -  [1]PQ ,  [2]PV, [3]SWING, [4]PQV
        busName     - name
        busArea     - geographic Area, the areas are separable
        busSubArea  - geographic subArea
        busZone     - geographic zone
        busLoadMW   - P^d : active load
        busLoadMVAR - Q^d : reactive load
        busGL       - GL:  real component of shunt admittance to ground.
        busBL       - BL:  imaginary component of shunt admittance to ground.
        busKV       - V: base kV
        --------------------------
        busVarAngle       - voltage magnitude
        busVarVoltage     - voltage magnitude
        busVarGenMW       - active generation (MW)
        busVarGenMVAR     - reactive generation (MVAR)

    '''
    """ NUMBER OF NODES IN THE TNETWROK """
    N_SIZE    =0
    PQ_SIZE   =0
    PV_SIZE   =0
    PQV_SIZE  =0
    SWING_SIZE=0   
    def __init__(self, cdfNum, busType, busName, 
                 busArea, busSubArea, busZone, busLoadMW, busLoadMVAR, busGL, busBL,busKV,
                 busVarAngle,busVarVoltage, busVarGenMW, busVarGenMVAR):
        """ THE IEEE CDF PROPERTIES: BUS DATA """
        self.cdfNum = cdfNum 
        self.busType   = busType
        self.busName   = busName
        self.busArea   = busArea
        self.busSubArea= busSubArea
        self.busZone   = busZone
        self.busLoadMW = busLoadMW
        self.busLoadMVAR = busLoadMVAR
        self.busGL  = busGL
        self.busBL  = busBL
        self.baseKV = busKV
        """ OTHER PROPERTIES - variables """
        self.busVarAngle = busVarAngle
        self.busVarVoltage = busVarVoltage
        self.busVarGenMW = busVarGenMW
        self.busVarGenMVAR =busVarGenMVAR
        
        
        """ Update the nodes' number """
        Tnode.N_SIZE+=1
        if busType = 1: """ PQ """
            Tnode.PQ_SIZE +=1
        else if busType = 2: """ PV """
            Tnode.PV_SIZE+=1
        else if busType = 3: """ SWING """
            Tnode.SWING_SIZE +=1
        else: """ PQV """
            Tnode.PQV_SIZE+=1
        
        
            
        
        
        
        

