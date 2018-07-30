#!/usr/bin/python3








def getEquivalenceClasses(universe, isEquivalent):
  universe2 = list(universe)
  equivalenceClasses = []
  
  while len(universe2) > 0:
    element = universe2[0]
    added = False
    
    for equivalenceClass in equivalenceClasses:
      if isEquivalent(element, equivalenceClass[0]):
        equivalenceClass.append(element)
        added = True
        break
    
    if not added: equivalenceClasses.append([element])
    del universe2[0]
  
  return equivalenceClasses
