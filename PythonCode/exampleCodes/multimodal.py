from coopr.pyomo import *
from math import pi, cos
#model = ConcreteModel()
i=2
model = ConcreteModel()
model.m= Param(default=i)
model.x = Var(initialize = 0.25, within=Reals ,bounds=(-4,4.0))
model.y = Var(initialize = 0.25, within=Reals ,bounds=(-4,4.0))
model.z = Var(initialize=4.0, within=Reals, bounds=(-10.0,10.0)) 
def multimodal(model):
	return (2- cos(pi*model.x)-cos(pi*model.y))* (model.x-model.m)**2
def quad(model):
	return	(model.z - model.m)**2
model.obj = Objective(rule=multimodal, sense=minimize)
if __name__ == '__main__':
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    opt = SolverFactory("ipopt")
    results = opt.solve(model)
    #sends results to stdout
    results.write()
