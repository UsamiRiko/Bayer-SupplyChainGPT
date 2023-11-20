import time
from gurobipy import GRB, Model

# Example data

suppliers = ['supplier1', 'supplier2']
farms = ['farm1', 'farm2']
markets = ['market1', 'market2']

seed_supply_capacity = {'supplier1': 1000, 'supplier2': 1500}
planting_cost = {'farm1': 20, 'farm2': 25}
storage_preservation_cost = {'market1': 10, 'market2': 15}

transport_cost_supplier_to_farm = {
    ('supplier1', 'farm1'): 2,
    ('supplier1', 'farm2'): 3,
    ('supplier2', 'farm1'): 2,
    ('supplier2', 'farm2'): 4
}

transport_cost_farm_to_market = {
    ('farm1', 'market1'): 5,
    ('farm1', 'market2'): 6,
    ('farm2', 'market1'): 4,
    ('farm2', 'market2'): 3
}

market_demand = {'market1': 800, 'market2': 1200}

# Create a new model
model = Model("bayer_crop_distribution")

# OPTIGUIDE DATA CODE GOES HERE

# Create variables
x = model.addVars(transport_cost_supplier_to_farm.keys(), vtype=GRB.INTEGER, name="x")
y = model.addVars(transport_cost_farm_to_market.keys(), vtype=GRB.INTEGER, name="y")

# Set objective
model.setObjective(
    sum(x[i] * transport_cost_supplier_to_farm[i] for i in transport_cost_supplier_to_farm.keys()) +
    sum(y[j] * transport_cost_farm_to_market[j] for j in transport_cost_farm_to_market.keys()) +
    sum(planting_cost[f] * sum(y[f, m] for m in markets) for f in farms) +
    sum(storage_preservation_cost[m] * market_demand[m] for m in markets),
    GRB.MINIMIZE)

# Conservation of flow constraint
# Add supply constraints
for s in suppliers:
    model.addConstr(sum(x[s, f] for f in farms) <= seed_supply_capacity[s], f"seed_supply_{s}")

# Add demand constraints
for m in markets:
    model.addConstr(sum(y[f, m] for f in farms) >= market_demand[m], f"market_demand_{m}")

# Optimize model
model.optimize()
m = model

# OPTIGUIDE CONSTRAINT CODE GOES HERE

# Solve
m.update()
model.optimize()

print(time.ctime())
if m.status == GRB.OPTIMAL:
    print(f'Optimal cost: {m.objVal}')
else:
    print("Not solved to optimality. Optimization status:", m.status)