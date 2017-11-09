"""
This module was inspired by `pinject`_, a dependency injection library
developed by Google but no longer maintained. It didn‘t support Python 3, so this is an attempt to mimic some basic functionality that library could provide.

.. _pinject: https://github.com/google/pinject

"""

import inspect

def _get_dependencies(provider):
    sig = inspect.signature(provider)
    names = set(sig.parameters.keys())
    return names

class Provider:
    def __init__(self, name, callable):
        self.name = name
        self.callable = callable

    def dependencies(self):
        return _get_dependencies(self.callable)

    def provide(self, dependencies):
        return (self.callable)(**dependencies)

class InstanceProvider:
    def __init__(self, name, instance):
        self.name = name
        self.instance = instance

    def dependencies(self):
        return set()

    def provide(self, dependencies={}):
        return self.instance

class SpecReader:
    def __init__(self, spec):
        self.providers = self._get_providers(spec)
        if hasattr(spec, 'configure') and callable(getattr(spec, 'configure')):
            spec.configure(self.bind)

    def bind(self, name, *, to_class=None, to_instance=None):
        if to_class is not None and to_instance is not None:
            raise ValueError('to_class and to_instance can\'t be both != None')
        if to_class is not None:
            self.providers.append(Provider(name, to_class))
        elif to_instance is not None:
            self.providers.append(InstanceProvider(name, to_instance))
        else:
            raise ValueError('either to_class or to_instance must be != None')

    def _get_providers(self, spec):
        return [
            Provider(name[8:], member)
            for (name, member) in inspect.getmembers(spec, inspect.ismethod)
            if name.startswith('provide_')
        ]

class ServiceLocator:
    def __init__(self, graph):
        self.graph = graph

    def __getattr__(self, key):
        return self.graph.provide(key)

class ObjectGraph:
    def __init__(self, providers, parent=None):
        self.providers = {}
        self.dependencies = set()
        self.registry = {}
        self.parent = parent

        for provider in providers:
            self.providers[provider.name] = provider
            self.dependencies.update(provider.dependencies())

    def provide(self, provider_name):
        if provider_name not in self.providers:
            if self.parent is not None:
                try:
                    return self.parent.provide(provider_name)
                except KeyError as e:
                    raise self._provider_not_found(provider_name)
            else:
                raise self._provider_not_found(provider_name)

        if provider_name in self.registry:
            return self.registry[provider_name]

        provider = self.providers[provider_name]
        dependencies = {dependency_name: self.provide(dependency_name) for dependency_name in provider.dependencies()}
        obj = provider.provide(dependencies)
        self.registry[provider_name] = obj
        return obj

    def locator(self):
        return ServiceLocator(self)

    @classmethod
    def create(cls, specs, parent=None):
        providers = []
        for spec in specs:
            reader = SpecReader(spec)
            providers.extend(reader.providers)

        return cls(providers, parent)

    def _provider_not_found(self, provider_name):
        return KeyError('provider not registered: %s' % provider_name)

