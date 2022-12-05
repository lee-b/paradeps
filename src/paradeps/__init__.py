"""
Manages dependencies, resolving them into tiers,
where items within each tier can run in parallel,
but each tier must execute before subsequent tiers.
"""

from typing import Any, Callable, Iterable, List, Set


class DependencyResolutionError(ValueError):
    """Raised when a dependency cannot be resolved."""
    pass


class DependencyLoopError(DependencyResolutionError):
    """Raised when a dependency loop is detected."""
    def __init__(self, *items: List['Dep']):
        super().__init__('Loop detected between {!r}'.format(*items))
        self.items = items
    

class Dep(object):
    """Base class for objects which have dependencies."""

    def __init__(self):
        self._deps: Set[Dep] = set()

    def add_dependency(self, dep: 'Dep'):
        """Add a dependency."""
        self._deps.add(dep)

    def add_dependencies(self, deps: 'Iterable[Dep]'):
        """Add multiple dependencies."""
        self._deps.update(deps)

    def depends_on(self, dep: 'Dep') -> bool:
        """Return True if this object depends on the given object."""
        return dep in self._deps

    def get_dependencies(self):
        """Return the dependencies."""
        return self._deps


def resolve_deps(deps: Set[Dep]) -> List[Set[Dep]]:
    """Resolve dependencies into tiers which only depend upon prior tiers.

    :param deps: The dependencies to resolve.
    :return: A list of sets of dependencies, where each set depends only on
             dependencies in prior sets.  i.e., the sequence of sets must
             be executed in order, but each set within it can be divided
            into parallel tasks.
    """
    assert isinstance(deps, set), "resolve_deps expects a set"

    # build the set of all dependencies from deps and their dependencies
    all_deps = set(deps) | set(d for dep in deps for d in dep.get_dependencies())

    # sort the deps by their dependencies
    unresolved = set(all_deps)

    tiers = []
    resolved = set()

    while len(unresolved) > 0:
        tier = set()

        tier = set(d for d in unresolved if all(dep in resolved for dep in d.get_dependencies()))
        if len(tier) == 0:
            raise DependencyLoopError(*unresolved)

        tiers.append(tier)

        unresolved -= tier
        resolved |= tier

    return tiers
