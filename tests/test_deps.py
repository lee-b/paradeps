import unittest

from paradeps import Dep, DependencyLoopError, resolve_deps


class DebugDependent(Dep):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return self.name


class TestDependent(unittest.TestCase):
    def test_add_dependency(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        a.add_dependency(b)
        self.assertTrue(a.depends_on(b))
    
    def test_add_dependencies(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        c = DebugDependent("c")
        a.add_dependencies([b, c])
        self.assertTrue(a.depends_on(b))
        self.assertTrue(a.depends_on(c))
    
    def test_depends_on(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        self.assertFalse(a.depends_on(b))
        a.add_dependency(b)
        self.assertTrue(a.depends_on(b))
    
    def test_get_dependencies(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        c = DebugDependent("c")
        a.add_dependencies([b, c])
        self.assertEqual(a.get_dependencies(), {b, c})
    
    def test_sort_dependents_chain(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        c = DebugDependent("c")
        
        a.add_dependency(b)
        b.add_dependency(c)
        
        tiers = resolve_deps([a, b, c])
        self.assertEqual(tiers, [{c}, {b}, {a}])

    def test_sort_dependents_loop(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        c = DebugDependent("c")
        
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(a)
        
        with self.assertRaises(DependencyLoopError):
            resolve_deps([a, b, c])

    def test_sort_dependents_4_items(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        c = DebugDependent("c")
        d = DebugDependent("d")
        
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)

        tiers = resolve_deps([a, b, c, d])

        self.assertEqual(tiers, [{d}, {c}, {b}, {a}])

    def test_sort_dependents_doc_example(self):
        a = DebugDependent("a")
        b = DebugDependent("b")
        c = DebugDependent("c")
        d = DebugDependent("d")
        e = DebugDependent("e")
        f = DebugDependent("f")

        a.add_dependency(f)
        b.add_dependency(f)

        tiers = resolve_deps([a, b, c, d, e, f])

        self.assertEqual(tiers, [{c, d, e, f}, {a, b}])
