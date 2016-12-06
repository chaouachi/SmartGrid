
# coding: utf-8

# In[44]:

from coopr.pyomo import *
import coopr.environ
from coopr.opt import SolverFactory


# In[45]:

model = AbstractModel ( )


# In[46]:

model.vertices= Set(initialize=['N1','N2','N3'], doc='nodes')


# In[47]:

model.edges= Set(within=model.vertices*model.vertices)


# In[48]:

model.ncolors = 3


# In[49]:

model.colors= RangeSet(1,model.ncolors)


# In[50]:

#Defin model variables
model.x= Var(model.vertices, model.colors, within=Binary)
model.y=Var()


# In[51]:

# (Constraint 1) Each node is colored with one color
def node_coloring_rule(model,v):
    return sum(model.x[v,c] for c in model.colors) ==1
model.node_coloring=Constraint(model.vertices, rule=node_coloring_rule)


# In[52]:

# (Constraint 2) Nodes t h a t share an edge cannot be c o l o r e d t he same color
def different_colors(model,v,w,c):
    return model.x[v,c] + model.x[w,c] <= 1
model.edge_coloring=Constraint(model.edges, model.colors, rule=different_colors)


# In[53]:

# (Constraint 3) Provide a lower bound on the minimum number of c o l o r s
def lower_bound(model,v,c):
    return c* model.x[v,c] <= model.y
model.lower_bound=Constraint(model.vertices,model.colors, rule=lower_bound)


# In[54]:

model.obj=Objective(expr=model.y, sense=minimize)
opt=SolverFactory("glpk")
results = opt.solve(model)

# In[ ]:



