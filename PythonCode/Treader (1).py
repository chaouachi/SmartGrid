
# coding: utf-8

# In[5]:

'''
[LICENSE]
Copyright (c) 2016, Ahmed Chaouachi
IREQ: Institut de Recherche d'Hydro Québec
All rights reserved.
[\LICENSE]
'''
if __name__ == "__main__":
    import numpy as np
    from numpy.lib.recfunctions import append_fields
#T_NODE_CDF_KEYS=['cdfNum', 'busName','busType','busLoadMW',
#                               'busLoadMVAR','busGL','busBL','busSubArea',
#                                     'busKV','busZone','busArea']
#T_NODE_NONCDF_KEYS=['desVoltage','busVarAngle','busVarVoltage','busVarGenMW','busVarGenMVAR']


#T_BRANCH_CDF_KEYS=['cdfNum','fromBus','toBus',
#                               'lengthMiles','outageRateYear','outageDuration','outageTransientRateYear',
#                                     'R','X','B','contRating','LTemergency','STemergency','TR']
class Treader:
    '''
    This class is desicated to handle input data file for Tnets: T: Transmission networks
    dynamic *params is adopted, these params in prder means:
            self.filePathNodes        : Path to the cdf nodes file
            self.filePathBranches     : Path to the cdf branches file
    These are the attributes of the Treader:
            self.cdfDataNodes         : list of dictionnaries containing cdf nodes data read from the cdf file
            self.estimatedDataNodes   : list of dictionnaries containing  nodes data read from (to be defines: file or param)
            self.otherDataNodes       : to be defines
            self.cdfDataBranches      : list of dictionnaries containing cdf branches data read from the cdf file
            self.estimatedDataBranches: to be defined
            self.otherDataBranches    : to be defined
    '''
    def __init__ (self, *params):
        try:
            self.filePathNodes    = params[0]
            self.filePathBranches = params[1]
            self.filePathGenerators= params[2] # Table 7 - Data of Generators at Each Bus
            #Nodes attributes
            self.cdfDataNodes=[]
            self.estimatedDataNodes=[{}]
            self.otherDataNodes=[]
            self.T_NODE_CDF_KEYS=['cdfNum', 'busName','busType','busLoadMW',
                               'busLoadMVAR','busGL','busBL','busSubArea',
                                     'busKV','busZone','busArea']
            self.T_NODE_NONCDF_KEYS=['desVoltage','busVarAngle','busVarVoltage','busVarGenMW','busVarGenMVAR']
            #Branches attributes
            self.cdfDataBranches=[]
            self.estimatedDataBranches=[]
            self.otherDataBranches=[]
            self.T_BRANCH_CDF_KEYS=['cdfNum','fromBus','toBus',
                               'lengthMiles','outageRateYear','outageDuration','outageTransientRateYear',
                                     'R','X','B','contRating','LTemergency','STemergency','TR']
            #generetors attributes
            self.cdfDataGenerators=[]
            self.estimatedDataGenerators=[]
            self.otherDataGenerators=[]
            #Bus    Unit    ID    PG     QG     Qmax    Qmin    VS
            #ID     Type     #    MW    MVAR    MVAR    MVAR    pu
            self.T_GENERATORS_CDF_KEYS=['genID','locBus', 'genName','genIdInBus','genPg',
                               'genQg','genQMAX','genQMIN','genVolt']
        except Exception as e:
            print ("Error: Not enough arguments: arg1: filePathNodes, arg2: filePathBranches")
            print ("Details:",e)
    ####### Read Nodes
    def tReadNodes(self, skipHeader, skipFooter):
        dt=[('cdfNum', '<i8'), ('busName', '|S9'), ('busType', '<i8'), ('busLoadMW', '<i8'),
                 ('busLoadMVAR', '<i8'), ('busGL', '<i8'), ('busBL', '<f8'), ('busSubArea', '<i8'),
                 ('busKV', '<i8'), ('busZone', '<i8')]
        try:
            with open (self.filePathNodes) as f:
                a=np.genfromtxt(self.filePathNodes , dtype=dt, skip_header=skipHeader, autostrip=True,
                                #names=keys,
                                skip_footer=skipFooter)
                for values in a:
                    # add the area to the values depanding on the 'cdfNum'
                    listarea=[]
                    listarea.append(int(values['cdfNum']/100))
                    values = values.tolist() + tuple(listarea)
                    self.cdfDataNodes.append (dict(zip(self.T_NODE_CDF_KEYS ,values)))            
            f.close()
            #return a
        except IOError:
            print ("Error: can\'t find file or read data")
            
    ####### Read Branches (how many lines to jump in the header, how many lines to jump in the footer)
    def tReadBranches(self, skipHeader, skipFooter):
        dtb=[('cdfNum', '|S9'), ('fromBus', '<i8'), ('toBus', '<i8'), ('lengthMiles', '<f8'), 
                  ('outageRateYear', '<f8'), ('outageDuration', '<i8'), ('outageTransientRateYear', '<f8'), 
                  ('R', '<f8'), ('X', '<f8'), ('B', '<f8'), ('contRating', '<i8'), ('LTemergency', '<i8'), 
                  ('STemergency', '<i8'), ('TR', '<f8')]
        try:
            with open (self.filePathBranches) as f:
                a=np.genfromtxt(self.filePathBranches , dtype=dtb ,skip_header=skipHeader, 
                                names=self.T_BRANCH_CDF_KEYS,
                                skip_footer=skipFooter)
                for values in a:
                    self.cdfDataBranches.append (dict(zip(self.T_BRANCH_CDF_KEYS,values)))            
            f.close()
            #return a
        except IOError:
            print ("Error: can\'t find file or read data")
    
    
    ####### Read Generators (how many lines to jump in the header, how many lines to jump in the footer)
    def tReadGenerators(self, skipHeader, skipFooter):
        dtb=[('genID','|S4'),('locBus', '<i8'), ('genName', '|S10'), ('genIdInBus', '<i8'), ('genPg', '<f8'), 
                  ('genQg', '<f8'), ('genQMAX', '<f8'), ('genQMIN', '<f8'), ('genVolt', '<f8')]
        #dtb2=[int,string,int,float,float,float,float,float ]
        try:
            with open (self.filePathGenerators) as f:
                a=np.genfromtxt(self.filePathGenerators , 
                                dtype=dtb, 
                                skip_header=skipHeader, 
                                names=self.T_GENERATORS_CDF_KEYS,
                                skip_footer=skipFooter)
                for values in a:
                    self.cdfDataGenerators.append (dict(zip(self.T_GENERATORS_CDF_KEYS,values)))            
            f.close()
            #return a
        except IOError:
            print ("Error: can\'t find file or read data")


# In[7]:

#R=T_reader('Data/Tnodes.txt', 'Data/Tbranch.txt', 'Data/Tgenerators.txt')
#R.tReadNodes(5,7)
#R.tReadBranches(17,9)
#R.tReadGenerators(5,3)
#R.cdfDataGenerators
#x=[]
#print (len(R.cdfDataBranches))
#for node in R.cdfDataGenerators :
#        print (node['genID'])
#for node in b:
#    print (int(node['cdfNum']/100))
#    x=node.tolist()
#    x+= tuple([1])
#    print (x)
#aa=b['cdfNum']
#append_fields(b,'NEWWW', aa, np.int)


# In[ ]:




# In[99]:

#for i,node in enumerate(R.cdfDataNodes ):
#    print ("*"*6, "Bus :", i, "*"*6)
#    for j,k in node.items():
#        print (j, " ", k)


# In[100]:

#b=R.tReadBranches(17,9,T_BRANCH_CDF_KEYS)
#b['R']


# In[101]:

#for i,node in enumerate(R.cdfDataBranches):
#    print (i)
#    for j,k in node.items():
#        print (j,k)


# In[102]:

#R.cdfDataBranches


# In[ ]:




# In[ ]:



