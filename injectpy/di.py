import inspect
from functools import partial
from typing import TypeVar, Generic, Callable, Optional, Dict, List, Type
from typing_extensions import Protocol
from abc import ABCMeta, abstractmethod
import itertools

from .lookup import *

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

KeyPredicate = Callable[[K], bool]

class ObjectGraph:
    def __init__(self, scope):
        self.scope = scope

    def provide(self, key):
        # TODO: Refactor this method

        mapping = self.scope._mapping(key)
        if mapping is None:
            raise _component_not_mapped(key)

        dependencies = {k: self.provide(k) for k in mapping.get_dependencies()}

        args = [dependencies[k] for k in mapping.args]
        kwargs = {k: dependencies[k] for k in mapping.kwargs}

        return mapping.provider()(*args, **kwargs)

class Mapping:
    def __init__(self, factory, *,
            name: Optional[str] = None,
            bind_to_class: Optional[Type] = None,
            singleton: bool = True,
            args: Optional[List] = None,
            kwargs: Optional[Dict] = None
    ):
        self.factory = factory
        self.name = name
        self.bind_to_class = bind_to_class
        self.singleton = singleton
        self.args = args or []
        self.kwargs = kwargs or {}

    def provider(self):
        if self.singleton:
            return SingletonProvider(self.factory)
        else:
            return self.factory

    def get_dependencies(self):
        return list(itertools.chain(self.args, self.kwargs.values()))

class ComponentNotMappedError(Exception): pass

class DependenciesRequiredError(Exception): pass

def _component_not_mapped(name):
    return ComponentNotMappedError(f'Not mapped: {name}')

def _dependencies_required(name):
    return DependenciesRequiredError(f'Component {name!r} cannot be instantiated here without dependencies')

class SingletonProvider(Generic[T]):
    def __init__(self, provider: Callable[[], T]) -> None:
        self.provider = provider
        self._instance = None # type: Optional[T]

    def __call__(self, *args, **kwargs) -> T:
        if self._instance is None:
            self._instance = self.provider(*args, **kwargs)
        return self._instance

class Registry:
    def __init__(self):
        self._by_name = {}
        self._by_class = {}

        self._name_lookup = DictLookup(self._by_name)
        self._class_lookup = DictLookup(self._by_class)

        self._lookup = self._name_lookup.only_if(lambda it: isinstance(it, str)) \
                    .or_else(self._class_lookup)

    def contains(self, key):
        return self._lookup.contains(key)

    def get(self, key):
        return self._lookup.get(key)
    
    def add(self, mapping: Mapping):

        if mapping.name is not None:
            self._by_name[mapping.name] = mapping

        if mapping.bind_to_class is not None:
            self._by_class[mapping.bind_to_class] = mapping

class Scope:
    def __init__(self, parent=None):
        self._registry = Registry()
        self._parent = parent

    def add_mapping(self, mapping: Mapping):
        self._registry.add(mapping)

    def add_provider(self, f, *args, **kwargs):
        self.add_mapping(_build_mapping(f, *args, **kwargs))

    def contains(self, key):
        return self._registry.contains(key)

    def _mapping(self, key):
        mapping = self._registry.get(key)
        if mapping is not None:
            return mapping
        elif self._parent is not None:
            return self._parent._mapping(key)
        else:
            return None

    def provide(self, key):
        mapping = self._mapping(key)
        if mapping is None:
            raise _component_not_mapped(key)

        dependencies = mapping.get_dependencies()
        if dependencies:
            raise _dependencies_required(key)

        return mapping.factory()

    def provider(self, *args, **kwargs):
        return component(self, *args, **kwargs)

def _build_mapping(f, name=None, **kwargs):

    if name is None:
        name = f.__name__

    return Mapping(f, name=name, **kwargs)

def component(scope, *args, **kwargs):

    def decorator(f):
        mapping = _build_mapping(f, *args, **kwargs)
        scope.add_mapping(mapping)

    return decorator

def component_scoped(scope):
    return partial(component, scope=scope)
