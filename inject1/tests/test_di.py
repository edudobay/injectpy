import unittest

from inject1.di import *

class Foo:
    def __init__(self, bar):
        self.bar = bar

class ExplicitSpecs:
    def __init__(self, bar):
        self.bar = bar

    def provide_bar(self):
        return self.bar

    def provide_foo(self, bar):
        return Foo(bar)

class BoundToInstanceFooSpecs:
    def __init__(self, foo):
        self.foo = foo

    def configure(self, bind):
        bind('foo', to_instance=self.foo)

class BoundToClassFooSpecs:
    def __init__(self, bar):
        self.bar = bar

    def provide_bar(self):
        return self.bar

    def configure(self, bind):
        bind('foo', to_class=Foo)

class ParentDependentFooSpecs:
    def configure(self, bind):
        bind('foo', to_class=Foo)

class BarSpecs:
    def __init__(self, bar):
        self.bar = bar

    def configure(self, bind):
        bind('bar', to_instance=self.bar)

class DependencyInjectionTestSuite(unittest.TestCase):
    def test_provide_object_with_dependency(self):
        bar = object()
        graph = ObjectGraph.create([ExplicitSpecs(bar=bar)])

        self.assertIs(bar, graph.provide('bar'))

        foo = graph.provide('foo')
        self.assertIs(bar, foo.bar)

    def test_bind_to_instance(self):
        foo = Foo(object())
        graph = ObjectGraph.create([BoundToInstanceFooSpecs(foo=foo)])

        self.assertIs(foo, graph.provide('foo'))

    def test_bind_to_class(self):
        bar = object()
        graph = ObjectGraph.create([BoundToClassFooSpecs(bar=bar)])

        foo = graph.provide('foo')
        self.assertIsInstance(foo, Foo)
        self.assertIs(bar, foo.bar)

    def test_dependency_on_object_from_parent_object_graph(self):
        bar = object()
        graph = ObjectGraph.create([ParentDependentFooSpecs()],
            parent=ObjectGraph.create([BarSpecs(bar=bar)]))

        foo = graph.provide('foo')
        self.assertIsInstance(foo, Foo)
        self.assertIs(bar, foo.bar)
