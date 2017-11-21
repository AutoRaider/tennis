import geometry as ge
import numpy


class PointP(ge.Point):
    def __init__(self, x, y):
        if isinstance(x, int):
            self.x = x
        else:
            self.x = int(round(x))

        if isinstance(y, int):
            self.y = y
        else:
            self.y = int(round(y))

    def __str__(self):
        return 'PointP: (%d, %d)' % (self.x, self.y)

    def __add__(self, other):
        return PointP(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return PointP(self.x - other.x, self.y - other.y)

    def perspective(self, mat):
        pt = ge.Point.perspective(self, mat)
        return PointP(pt.x, pt.y)


def get_random_number(low, high):
    """
    get a random in [low, high]
    :param low: low boundary
    :param high: high boundary
    :return: random number
    """
    return numpy.random.randint(int(low), int(high))


class Corner(object):

    def __init__(self):
        self.p1 = PointP(0, 0)
        self.p2 = PointP(100, 0)
        self.p3 = PointP(0, 100)
        self.p4 = PointP(100, 100)

    def randomize(self, width, height):
        self.p1.update(get_random_number(0, width * 0.25), get_random_number(0, height * 0.25))
        self.p2.update(get_random_number(width * 0.75, width), get_random_number(0, height * 0.25))
        self.p3.update(get_random_number(0, width * 0.25), get_random_number(height * 0.75, height))
        self.p4.update(get_random_number(width * 0.75, width), get_random_number(height * 0.75, height))

    def __str__(self):
        return '%s, %s, %s, %s' % (self.p1, self.p2, self.p3, self.p4)

    def list(self):
        return [self.p1.tuple(), self.p2.tuple(), self.p3.tuple(), self.p4.tuple()]


class Block(object):
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def __str__(self):
        return '%s - %s' % (self.point1, self.point2)

    def center(self):
        return PointP((self.point1.x + self.point2.x) / 2, (self.point1.y + self.point2.y) / 2)
