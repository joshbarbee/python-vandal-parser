# implemented as adjacency list for increased performance
# versus maintaing preds / succs for each node
from typing import Any, Union


class MetaVariable:
    def __init__(self, name: str, value: int, parents: list["MetaVariable"]):
        self.name = name
        self.value = value
        self._parents = parents
        self._children = []

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, MetaVariable):
            return False
        return self.name == __value.name
    
    def to_dict(self):
        return {self.name: self.value}
    
    @staticmethod
    def value_eq(var1: "MetaVariable", var2: "MetaVariable") -> bool:
        return var1.value == var2.value

    @staticmethod
    def value_ne(var1: "MetaVariable", var2: "MetaVariable") -> bool:
        return var1.value != var2.value
    
    @staticmethod
    def value_gt(var1: "MetaVariable", var2: "MetaVariable") -> bool:
        return var1.value > var2.value
    
    @staticmethod
    def value_lt(var1: "MetaVariable", var2: "MetaVariable") -> bool:
        return var1.value < var2.value
    
    @staticmethod
    def value_gte(var1: "MetaVariable", var2: "MetaVariable") -> bool:
        return var1.value >= var2.value
    
    @staticmethod
    def value_lte(var1: "MetaVariable", var2: "MetaVariable") -> bool:
        return var1.value <= var2.value
    

    def is_ancestor(
        self, parent_vars: Union[list["MetaVariable"], "MetaVariable"]
    ) -> bool:
        """Return true if any Variable instance in parent_vars is a parent
        of the Variable instance. Uses BFS for searching

        Args:
            parent_vars (List[Variable;] | Variable): A List of variables or a
            single variable that should be a parent of `self`.

        Returns:
            bool: whether any of the Variables in parent_vars are a parent of
            `self`
        """

        if not isinstance(parent_vars, list):
            parent_vars = [parent_vars]

        queue = [self]

        while queue:
            current = queue.pop(0)

            if current in parent_vars:
                return True

            queue.extend(current._parents)
        return False

    def is_predecessor(self, child_vars: Union[list["MetaVariable"], "MetaVariable"]) -> bool:
        """Return true if any Variable instance in child_vars is a child
        of the Variable instance. Uses BFS for searching

        Args:
            child_vars (List[Variable;] | Variable): A List of variables or a
            single variable that should be a child of `self`.

        Returns:
            bool: whether any of the Variables in child_vars are a child of
            `self`
        """

        if not isinstance(child_vars, list):
            child_vars = [child_vars]

        queue = [self]

        while queue:
            current = queue.pop(0)

            if current in child_vars:
                return True

            queue.extend(current._children)

    def descendants(self):
        """Return a list of all descendants of the Variable instance

        Returns:
            List[Variable]: A list of all descendants of the Variable instance
        """

        descendants = []
        queue = [self]

        while queue:
            current = queue.pop(0)
            descendants.append(current)
            queue.extend(current._children)

        return descendants

    def ancestors(self, end: "MetaVariable" = None):
        """Return a list of all ancestors of the Variable instance

        Returns:
            List[Variable]: A list of all ancestors of the Variable instance
        """

        ancestors = []
        queue = [self]

        while queue:
            current = queue.pop(0)

            if end and current == end:
                break

            ancestors.append(current)
            queue.extend(current._parents)

        return ancestors

    def children(self):
        return self._children
    
    def parents(self):
        return self._parents