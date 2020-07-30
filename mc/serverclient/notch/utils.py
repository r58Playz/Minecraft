from collections import namedtuple


class Vector(namedtuple('BaseVector', ('x', 'y', 'z'))):
    """An immutable type usually used to represent 3D spatial coordinates.
       NOTE: subclasses of 'Vector' should have '__slots__ = ()' to avoid the
       creation of a '__dict__' attribute, which would waste space.
    """
    __slots__ = ()

    def __add__(self, other):
        return NotImplemented if not isinstance(other, Vector) else \
               type(self)(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return NotImplemented if not isinstance(other, Vector) else \
               type(self)(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return type(self)(-self.x, -self.y, -self.z)

    def __mul__(self, other):
        return type(self)(self.x*other, self.y*other, self.z*other)

    def __rmul__(self, other):
        return type(self)(other*self.x, other*self.y, other*self.z)

    def __truediv__(self, other):
        return type(self)(self.x/other, self.y/other, self.z/other)

    def __floordiv__(self, other):
        return type(self)(self.x//other, self.y//other, self.z//other)

    __div__ = __floordiv__

    def __repr__(self):
        #TODO: use f-strings
        return '%s(%r, %r, %r)' % (type(self).__name__, self.x, self.y, self.z) 
