from typing import TypeVar, Generic, Callable, Optional, Dict
from typing_extensions import Protocol
from abc import ABCMeta, abstractmethod

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

KeyPredicate = Callable[[K], bool]

class ILookup(Generic[K, V], metaclass=ABCMeta):
    @abstractmethod
    def contains(self, key: K) -> bool: pass

    @abstractmethod
    def get(self, key: K) -> Optional[V]: pass

    def only_if(self, predicate: KeyPredicate):
        return Lookup.only_if(self, predicate)

    def or_else(self, *lookup: 'ILookup[K, V]') -> 'ILookup[K, V]':
        return Lookup.fallback(self, *lookup)

class Lookup:
    @staticmethod
    def fallback(*lookups: ILookup):
        return FallbackLookup(*lookups)

    @staticmethod
    def only_if(lookup: ILookup, predicate: KeyPredicate):
        return ConditionalLookup(lookup, predicate)

class DictLookup(ILookup[K, V]):
    def __init__(self, source: Dict[K, V]) -> None:
        self._source = source

    def contains(self, key: K) -> bool:
        return key in self._source

    def get(self, key: K) -> Optional[V]:
        return self._source.get(key)

class ConditionalLookup(ILookup[K, V]):
    def __init__(self, delegate: ILookup[K, V], predicate: KeyPredicate) -> None:
        self._delegate = delegate
        self._predicate = predicate

    def contains(self, key: K) -> bool:
        return self._predicate(key) and self._delegate.contains(key)

    def get(self, key: K) -> Optional[V]:
        return self._delegate.get(key) if self._predicate(key) else None

class FallbackLookup(ILookup[K, V]):
    def __init__(self, *args: ILookup[K, V]) -> None:
        assert len(args) >= 2
        self._items = args

    def contains(self, key: K) -> bool:
        return any(lookup.contains(key) for lookup in self._items)

    def get(self, key: K) -> Optional[V]:
        for lookup in self._items:
            item = lookup.get(key)
            if item is not None:
                return item
        return None

