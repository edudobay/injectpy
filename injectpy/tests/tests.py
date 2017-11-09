import unittest

import injectpy.di as di

class ProviderTest(unittest.TestCase):

    def test_provide_known_object(self):
        "component can be provided with the name of the provider function"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)

        obj = object()

        @di.component(scope)
        def foo():
            return obj

        provided = graph.provide('foo')
        self.assertIs(obj, provided)

    def test_component_can_be_added_via_component_scoped(self):
        "component can be added via a component_scoped decorator"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)
        scoped = di.component_scoped(scope)

        obj = object()

        @scoped()
        def foo():
            return obj

        self.assertEquals(obj, graph.provide('foo'))

    def test_component_can_be_added_via_scope_provider(self):
        "component can be added via @scope.provider()"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)

        obj = object()

        @scope.provider()
        def foo():
            return obj

        self.assertEquals(obj, graph.provide('foo'))

    def test_provide_unknown_object_should_fail(self):
        "should fail when providing an object not added to the graph"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)
        
        with self.assertRaises(di.ComponentNotMappedError):
            graph.provide('foo')

    def test_provide_object_from_parent_scope(self):
        "an object from the parent scope can be provided in the child scope"
        root = di.Scope()
        child = di.Scope(parent=root)
        root_graph = di.ObjectGraph(root)
        child_graph = di.ObjectGraph(child)

        obj = object()

        @di.component(scope=root)
        def foo():
            return obj

        provided = child_graph.provide('foo')
        self.assertEquals(obj, provided)

    def test_parent_does_not_provide_object_from_child_scope(self):
        "an object from the child scope cannot be provided in the parent scope"
        root = di.Scope()
        child = di.Scope(parent=root)
        root_graph = di.ObjectGraph(root)
        child_graph = di.ObjectGraph(child)

        obj = object()

        @di.component(scope=child)
        def foo():
            return obj

        with self.assertRaises(di.ComponentNotMappedError):
            provided = root_graph.provide('foo')

    def test_object_not_marked_as_singleton_is_initialized_twice(self):
        "a non-singleton object is initialized once per provide()"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)
        
        @scope.provider(singleton=False)
        def foo():
            return object()

        first = graph.provide('foo')
        second = graph.provide('foo')

        self.assertIsNot(first, second)

    def test_object_marked_as_singleton_is_not_initialized_twice(self):
        "a singleton object is initialized only once within its scope"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)

        class Foo: pass
        
        @scope.provider()
        def foo():
            return Foo()

        first = graph.provide('foo')
        second = graph.provide('foo')

        self.assertIsInstance(first, Foo)
        self.assertIs(first, second)

    def test_lookup_by_class(self):
        "lookup an object by its bound class"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)

        class Foo: pass

        @scope.provider(bind_to_class=Foo)
        def foo():
            return Foo()

        provided = graph.provide(Foo)
        self.assertIsInstance(provided, Foo)

    def test_imperative_dependency_declaration(self):
        "imperative dependency declaration"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)

        class Foo: pass

        scope.add_provider(lambda: Foo(), bind_to_class=Foo)

        provided = graph.provide(Foo)
        self.assertIsInstance(provided, Foo)

    def test_object_with_dependencies_cannot_be_provided(self):
        "cannot provide an object with dependencies if they have not been mapped"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)

        class Foo: pass

        @scope.provider(args=['bar'])
        def foo(bar):
            return Foo()

        with self.assertRaises(di.ComponentNotMappedError):
            provided = graph.provide('foo')

class ObjectGraphTest(unittest.TestCase):

    def test_provide_object_with_declared_dependencies(self):
        "an object with dependencies can be provided if the dependencies have been mapped"
        scope = di.Scope()
        graph = di.ObjectGraph(scope)

        class Foo:
            def __init__(self, bar):
                self.bar = bar

        class Bar: pass

        scope.add_provider(lambda: Bar(), bind_to_class=Bar)
        self.assertIsInstance(graph.provide(Bar), Bar)

        @scope.provider(bind_to_class=Foo, args=[Bar])
        def foo(bar):
            return Foo(bar)

        provided = graph.provide(Foo)

        self.assertIsInstance(provided, Foo)
        self.assertIsInstance(provided.bar, Bar)

class AnnotationTest(unittest.TestCase):

    @unittest.skip('incomplete')
    def test_scope_bindings_should_preserve_declared_type_hints(self):
        class Foo: pass

        scope = di.Scope()

        @scope.provider(bind_to_class=Foo)
        def foo() -> Foo:
            return Foo()

        binding = scope.bindings.foo
        signature = inspect.signature(binding)
        self.assertEquals(Foo, signature.return_annotation)

