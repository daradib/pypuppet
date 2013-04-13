from pickle import dumps

class Memoize:
    """Memoizing decorator class"""
    def __init__(self, f):
        self.f = f
        self.cache = {}
    def __call__(self, *args, **kwargs):
        key = dumps((args, sorted(kwargs.items())), -1)
        if key not in self.cache:
            self.cache[key] = self.f(*args, **kwargs)
        return self.cache[key]
    def __repr__(self):
        return self.f.__doc__

class Lazy(object):
    """Lazy attribute evaluation decorator class"""
    def __init__(self, f):
        self.f = f
        self.cache = {}
    def __get__(self, instance, owner):
        if instance not in self.cache:
            self.cache[instance] = self.f(instance)
        return self.cache[instance]
