import pulp

## Icecream problem

##Two types of ice cream: cones & sorbets
##Cones: 1 scoop plus biscuit
##Sorbets: 2 scoops plus fruit
##Costs: scoop x, biscuit y, fruit z

model_icecream = pulp.LpProblem("Icecream van profit optimisation", pulp.LpMaximize)

## Two variables: Cones & Sorbets

icecream_types = ['Cones','Sorbets']

## Declare variables

icecream_types = pulp.LpVariable.dicts("Icecream type",((i) for i in icecream_types), lowBound = 0, cat='Continuous')

## Maximize profit

model_icecream += pulp.lpSum(3*icecream_types['Cones'] + 2*icecream_types['Sorbets'])


## Constraints

MaxSupply = {'Cones': 10, 'Sorbets':15}


## MaxSupply

for i in icecream_types:
    model_icecream += icecream_types[i] <= MaxSupply[i]

print(icecream_types['Cones'])


print(model_icecream)

model += pulp.lpSum([ing_weight['premium', j] for j in ingredients]) == 500 * 0.05

# Economy has >= 40% pork, premium >= 60% pork
model += ing_weight['economy', 'pork'] >= (
    0.4 * pulp.lpSum([ing_weight['economy', j] for j in ingredients]))

model += ing_weight['premium', 'pork'] >= (
    0.6 * pulp.lpSum([ing_weight['premium', j] for j in ingredients]))

# Sausages must be <= 25% starch
model += ing_weight['economy', 'starch'] <= (
    0.25 * pulp.lpSum([ing_weight['economy', j] for j in ingredients]))

model += ing_weight['premium', 'starch'] <= (
    0.25 * pulp.lpSum([ing_weight['premium', j] for j in ingredients]))

# We have at most 30 kg of pork, 20 kg of wheat and 17 kg of starch available
model += pulp.lpSum([ing_weight[i, 'pork'] for i in sausage_types]) <= 30
model += pulp.lpSum([ing_weight[i, 'wheat'] for i in sausage_types]) <= 20
model += pulp.lpSum([ing_weight[i, 'starch'] for i in sausage_types]) <= 17

# We have at least 23 kg of pork to use up
model += pulp.lpSum([ing_weight[i, 'pork'] for i in sausage_types]) >= 23
##In [7]:
# Solve our problem
model.solve()
pulp.LpStatus[model.status]
##Out[7]:
##'Optimal'
##In [8]:

for var in ing_weight:
    var_value = ing_weight[var].varValue
    print("The weight of {0} in {1} sausages is {2} kg".format(var[1], var[0], var_value))
    
##The weight of starch in premium sausages is 6.25 kg
##The weight of starch in economy sausages is 4.375 kg
##The weight of wheat in economy sausages is 6.125 kg
##The weight of wheat in premium sausages is 2.75 kg
##The weight of pork in economy sausages is 7.0 kg
##The weight of pork in premium sausages is 16.0 kg
##In [9]:
total_cost = pulp.value(model.objective)

print("The total cost is €{} for 350 economy sausages and 500 premium sausages".format(round(total_cost, 2)))

##The total cost is €140.96 for 350 economy sausages and 500 premium sausages
