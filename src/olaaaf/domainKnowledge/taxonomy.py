from __future__ import annotations

from .domainKnowledge import DomainKnowledge
from ..formula import Formula, PropositionalVariable, And, Not

from collections import namedtuple

class Taxonomy(DomainKnowledge):
    
    _elements = dict()

    ElementTuple = namedtuple("element", "children parents")

    def __init__(self) -> None:
        pass

    def addElement(self, propVar):

        # TODO error checking and handling

        if isinstance(propVar, PropositionalVariable):
            propVar = propVar.name
        
        self._elements[propVar] = self.ElementTuple(children=set(), parents=set())

    def addElements(self, propVars):

        for propVar in propVars:
            self.addElement(propVar)

    def addChild(self, src, trgt):

        # TODO error checking and handling

        if isinstance(src, PropositionalVariable):
            src = src.name
        if isinstance(trgt, PropositionalVariable):
            trgt = trgt.name

        self._elements[src].children.add(trgt)
        self._elements[trgt].parents.add(src)

    def addChildren(self, src, trgts):

        for trgt in trgts:
            self.addChild(src, trgt)

    def addParent(self, src, trgt):

        # TODO error checking and handling

        if isinstance(src, PropositionalVariable):
            src = src.name
        if isinstance(trgt, PropositionalVariable):
            trgt = trgt.name

        self._elements[src].parents.add(trgt)
        self._elements[trgt].children.add(src)

    def addParents(self, src, trgts):

        for trgt in trgts:
            self.addParent(src, trgt)

    def removeElement(self, propVar):

        # TODO error checking and handling

        if isinstance(propVar, PropositionalVariable):
            propVar = propVar.name

        for child in self._elements[propVar].children:
            self._elements[child].parents.remove(propVar)
        for parent in self._elements[propVar].parents:
            self._elements[parent].children.remove(propVar)

        del self._elements[propVar]

    def removeElements(self, propVars):

        for propVar in propVars:
            self.removeElement(propVar)

    def removeChild(self, src, trgt):

        # TODO error checking and handling

        if isinstance(src, PropositionalVariable):
            src = src.name
        if isinstance(trgt, PropositionalVariable):
            trgt = trgt.name

        self._elements[src].children.remove(trgt)
        self._elements[trgt].parents.remove(src)

    def removeChildren(self, src, trgts):

        for trgt in trgts:
            self.removeChild(src, trgt)

    def removeParent(self, src, trgt):

        # TODO error checking and handling

        if isinstance(src, PropositionalVariable):
            src = src.name
        if isinstance(trgt, PropositionalVariable):
            trgt = trgt.name

        self._elements[src].parents.remove(trgt)
        self._elements[trgt].children.remove(src)

    def removeParents(self, src, trgts):

        for trgt in trgts:  
            self.removeParent(src, trgt)

    def getAncestors(self, src):

        if isinstance(src, PropositionalVariable):
            src = src.name
        
        ancestors = self._elements[src].parents.copy()
        toCheck = ancestors.copy()

        while len(toCheck) != 0:
            
            a = toCheck.pop()
            parents = self._elements[a].parents

            for p in parents:
                if not p in ancestors:
                    toCheck.add(p)

            ancestors |= parents

        return ancestors

    def getDescendants(self, src):

        if isinstance(src, PropositionalVariable):
            src = src.name
        
        ancestors = self._elements[src].children.copy()
        toCheck = ancestors.copy()

        while len(toCheck) != 0:
            
            a = toCheck.pop()
            children = self._elements[a].children

            for c in children:
                if not c in ancestors:
                    toCheck.add(c)

            ancestors |= children

        return ancestors

    def toConstraints(self) -> Formula:

        fmSet = set()

        for elem in self._elements:
            for parent in self._elements[elem].parents:
                fmSet.add(PropositionalVariable(elem) >> PropositionalVariable(parent))

        return And(*fmSet)
    
    def inferFrom(self, psi: Formula) -> Formula:
                
        inferedChildren = set()

        if isinstance(psi, And):
            
            for c in psi.children:

                if isinstance(c, Not) and isinstance(c.children, PropositionalVariable):
                    try:
                        inferedChildren |= {~PropositionalVariable(d) for d in self.getDescendants(c.children)}
                    except KeyError:
                        pass
                elif isinstance(c, PropositionalVariable):
                    try:
                        inferedChildren |= {PropositionalVariable(a) for a in self.getAncestors(c)}
                    except KeyError:
                        pass

        if len(inferedChildren) != 0:
            return psi & And(*inferedChildren)
        
        return psi

    def getElements(self) -> dict:
        return self._elements

    def __getitem__(self, key: str):

        # TODO check erreur
        return (key, self._elements[key])