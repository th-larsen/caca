'''
CANTILEVER BEAM BENDING CALCULATOR
ACCOUNTS FOR MATERIAL, DEFLECTION, BUCKLING, & STRESS

Euler's Buckling Formula, Critical Buckling Load: $ P_{cr} = \frac{π^2EI}{(KL)^2} $

Cantilever Deflection, Offset Point Load: $ d=\frac{Pa^2(3L-a)}{6EI} $

Stress, Fatigue Life: $ σ = \frac{yM}{I}, M=PL $
'''
import math as m

# outputs height of cantilever for the allowable deflection, given force, length
def cantilever(d, P, L, a, E, b):
  I=(P*a**2*(3*L-a))/(6*E*d)
  h=(12*I/b)**(1/3)
  return h

# Outputs maximum length before buckling given load, material, and cross sectional area (b & h)
def buckling(P, E, K, b, h):
  L = (m.pi*h)/(6*K*P)*(3*E*b*h*P)**(1/2)
  return L

# Note: moment same as cantilever
def fatigue_stress(y, P, L, b, h):
  stress = (y * P * L)/(1/12*b*h**3)
  return stress

def calculations(distributed_force, allowable_deflection, cantilever_length, distance_applied, youngs_modulus, buckling_constant, buckling_base, change):
  cantilever_height = cantilever(allowable_deflection, distributed_force, cantilever_length, distance_applied, youngs_modulus, change)
  buckling_length = buckling(distributed_force, youngs_modulus, buckling_constant, buckling_base, change)

  return cantilever_height, buckling_length

# converge on value for cantilever base and buckling height
def find_min_thickness(distributed_force, allowable_deflection, cantilever_length, distance_applied, youngs_modulus, buckling_constant, buckling_base, maximum_cantilever_height):
  epsilon = 0.0000001 # threshold for equality
  lower_bound = 0.012 # 1 mm minimum for machining (change for smallest base instead of height)
  upper_bound = 0.1  # 200 mm

  while (upper_bound - lower_bound > epsilon):
    change = (lower_bound + upper_bound) / 2
    cantilever_height, buckling_length = calculations(distributed_force, allowable_deflection, cantilever_length, distance_applied, youngs_modulus, buckling_constant, buckling_base, change)
    # Cantilever height must not... (bottlenecks)
      # Exceed buckling threshold
      # Be greater than the amount of space we have available
    if cantilever_height >= buckling_length or cantilever_height >= maximum_cantilever_height:
      lower_bound = change
    else:
      upper_bound = change

  # Return us the appropriate value for the cantilever base dimension
  return change

def optimize_stress(stress_force, cantilever_length, cantilever_base, maximum_cantilever_height, max_stress):
  # calculate minimum height to handle that force given max stress
  min_height = m.sqrt(6*cantilever_length*stress_force*cantilever_base*max_stress)/(cantilever_base*max_stress)
  # if the min height for stress is less then the space we have, then simply increase the height to that limit
  if min_height <= maximum_cantilever_height:
    return min_height, cantilever_base
  # if more, then set the height to the max we have and update the base to support the stress
  else:
    min_height = maximum_cantilever_height
    stress_base = (6*cantilever_length*stress_force)/(max_stress*min_height**2)
    return min_height, stress_base
  
def optimize_buckling(height, distributed_force, buckling_constant, cantilever_length, youngs_modulus, stress_force, cantilever_base, max_stress):
  buckling_height = ((12*distributed_force*(buckling_constant*height)**2)/(cantilever_length*m.pi**2*youngs_modulus))**(1/3)
  # decrement height until the stress is maximized
  epsilon = 0.0000001
  lower_bound = 0
  upper_bound = height
  while (upper_bound - lower_bound > epsilon):
    change = (lower_bound + upper_bound) / 2
    stress = fatigue_stress((change)/2, stress_force, cantilever_length, buckling_height, (change))
    # print(stress, change)
    if stress < max_stress:
      upper_bound = change
    else:
      lower_bound = change
  return change, buckling_height



### USER INPUTS ###

# Constants
num_arms = 12 # CHANGE FOR # OF CANTILEVERS THE FORCE IS DISTRIBUTED AMONG
youngs_modulus = 7.1*10**10 # CHANGE GIVEN MATERIAL
buckling_constant = 0.5
distributed_force = 4300/num_arms # CHANGE GIVEN FORCE
stress_force = 2900/num_arms # CHANGE LESSER STRESS/FATIGUE FORCE
max_stress = 5.25*10**8 #REFER TO FATIGUE LIFE CHART FOR 1.5*10^6 CYCLES 

# Independents
cantilever_length = 0.01 # BENDING LENGTH
maximum_cantilever_height = .01 # maximum vertical "space" for the cantilever (artifical cap for height)

# Dependents
buckling_base = cantilever_length
distance_applied = cantilever_length
allowable_deflection = cantilever_length/180 # CIVIL ENGINEERING CODE, CHANGE FOR NEEDS



### RUN FUNCTIONS ###

# Run optimization
equal_value = find_min_thickness(distributed_force, allowable_deflection, cantilever_length, distance_applied, youngs_modulus, buckling_constant, buckling_base, maximum_cantilever_height)

# Get Minimum Cantilever Height
height = cantilever(allowable_deflection, distributed_force, cantilever_length, distance_applied, youngs_modulus, equal_value)

# Adjust for Stress
stress = fatigue_stress(height/2, stress_force, cantilever_length, equal_value, height)
if stress > max_stress:
  height, equal_value = optimize_stress(stress_force, cantilever_length, equal_value, maximum_cantilever_height, max_stress)

# Adjust for Buckling
buckling_height = buckling(distributed_force, youngs_modulus, buckling_constant, buckling_base, equal_value)
if height > buckling_height:
  height, equal_value = optimize_buckling(height, distributed_force, buckling_constant, cantilever_length, youngs_modulus, stress_force, equal_value, max_stress)

# Result
print(f"The minimum base of the cantilever must be at least {round(equal_value*1000,3)}mm thick, with a height of {round(height*1000, 3)}mm")

stress = fatigue_stress(height/2, stress_force, cantilever_length, equal_value, height)
buckling_height = buckling(distributed_force, youngs_modulus, buckling_constant, buckling_base, equal_value)
deflection = (distributed_force*distance_applied**2*(3*cantilever_length-distance_applied))/(6*youngs_modulus)*1/(1/12*equal_value*height**3)
print(stress, buckling_height*1000, deflection*1000)