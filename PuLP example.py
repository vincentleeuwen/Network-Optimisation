import pulp

##In [2]:
# Instantiate our problem class

model = pulp.LpProblem("Cost minimising blending problem", pulp.LpMinimize)

##Here we have 6 decision variables, we could name them individually but this wouldn’t scale up if we had hundreds/thousands of variables (you don’t want to be entering all of these by hand multiple times).
##
##We’ll create a couple of lists from which we can create tuple indices.
##
##In [3]:
# Construct our decision variable lists

sausage_types = ['economy', 'premium']
ingredients = ['pork', 'wheat', 'starch']

##Each of these decision variables will have similar characteristics (lower bound of 0, continuous variables). Therefore we can use PuLP’s LpVariable object’s dict functionality, we can provide our tuple indices.
##
##These tuples will be keys for the ing_weight dict of decision variables
##
##In [4]:

ing_weight = pulp.LpVariable.dicts("weight kg",
                                     ((i, j) for i in sausage_types for j in ingredients),
                                     lowBound=0,
                                     cat='Continuous')

##PuLP provides an lpSum vector calculation for the sum of a list of linear expressions.
##
##Whilst we only have 6 decision variables, I will demonstrate how the problem would be constructed in a way that could be scaled up to many variables using list comprehensions.
##
##In [5]:

# Objective Function
model += (
    pulp.lpSum([
        4.32 * ing_weight[(i, 'pork')]
        + 2.46 * ing_weight[(i, 'wheat')]
        + 1.86 * ing_weight[(i, 'starch')]
        for i in sausage_types])
)
##Now we add our constraints, bear in mind again here how the use of list comprehensions allows for scaling up to many ingredients or sausage types
##
##In [6]:
# Constraints
# 350 economy and 500 premium sausages at 0.05 kg
model += pulp.lpSum([ing_weight['economy', j] for j in ingredients]) == 350 * 0.05
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

print(model)

##The total cost is €140.96 for 350 economy sausages and 500 premium sausages
