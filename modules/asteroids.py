"""Programm module that cointains Asteroid class,
Quad asteroid tree (speciffi quadtree for asteroids),
asteroid manager (class that manage asteroid) and
allows to perform a search in Asteroids by quadtree"""
# pylint: disable=import-error
#pylint: disable=(W0201, R0913, R0917, R0902, W0622, R0914, E1101)
import math
from random import randint

from modules.consts import MAX_LEFT_GRID as MLG


class Asteroid:
    """Asteroid class"""
    def __init__(self, radius: float, speed_x: float,
                 speed_y: float, x: float, y: float,
                 color: tuple[int] = (255, 255, 255)):
        """Initialization a class"""
        self.radius: float = radius
        self.speed_x: float = speed_x
        self.speed_y: float = speed_y
        self.x: float = x
        self.y: float = y
        self.color: tuple[int] = color

    def next_step(self, height, width):
        """Performs asteroid advance by one tick"""
        self.x = round(self.x + self.speed_x, MLG)
        self.y = round(self.y + self.speed_y, MLG)

        if self.x - self.radius < 0:
            self.x = self.radius
            self.speed_x = abs(self.speed_x)

        elif self.x + self.radius > width:
            self.x = width - self.radius
            self.speed_x = -abs(self.speed_x)

        if self.y - self.radius < 0:
            self.y = self.radius
            self.speed_y = abs(self.speed_y)
        elif self.y + self.radius > height:
            self.y = height - self.radius
            self.speed_y = -abs(self.speed_y)
        return self

    def __str__(self):
        """str magic method"""
        return f"Asteroid with: R = {self.radius}, x = {self.x}, y = {self.y}"

    def __repr__(self):
        """repr magic method"""
        return f"Asteroid with: R = {self.radius}, x = {self.x}, y = {self.y}"

    def __eq__(self, value):
        """eq magic method"""
        if not isinstance(value, Asteroid):
            raise TypeError()

        return self.__dict__ == value.__dict__

class QuadAsteroidTree:
    """A quadtree that allows you to perform an efficient asteroid search"""
    def __init__(self, min_x: float, max_x: float,
                 min_y: float, max_y: float, capacity = 2, depth = 0,
                 max_depth = 20, asteroids: Asteroid = None):
        """Initialization a class"""
        if asteroids:
            self.nodes = list(asteroids)

        else:
            self.nodes = []

        self.capacity = capacity
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.depth = depth
        self.max_depth = max_depth

        if len(self.nodes) > self.capacity and self.depth < self.max_depth:
            self._subdivide()

    def insert(self, asteroid: Asteroid) -> bool:
        """Construct function, adding one element in tree"""
        if not self._contains_coord(asteroid.x, asteroid.y):
            return False

        if (len(self.nodes) == 0 or
            isinstance(self.nodes[0] if self.nodes else None, Asteroid)):
            if self.depth < self.max_depth:
                self.nodes.append(asteroid)
                if len(self.nodes) > self.capacity:
                    self._subdivide()

        else:
            for child in self.nodes:
                if child.insert(asteroid):
                    return True

        return True

    def _subdivide(self):
        """Split leaves tree to new trees"""
        med_x = round((self.min_x + self.max_x) / 2, MLG)
        med_y = round((self.min_y + self.max_y) / 2, MLG)
        nw_asteroids = []
        ne_asteroids = []
        sw_asteroids = []
        se_asteroids = []

        for ast in self.nodes:
            if ast.x < med_x and ast.y < med_y:
                nw_asteroids.append(ast)
            elif ast.x >= med_x and ast.y < med_y:
                ne_asteroids.append(ast)
            elif ast.x < med_x and ast.y >= med_y:
                sw_asteroids.append(ast)
            else:
                se_asteroids.append(ast)

        self.nodes = [
            QuadAsteroidTree(asteroids=nw_asteroids, min_x=self.min_x, max_x=med_x,
                             min_y=self.min_y, max_y=med_y, capacity=self.capacity,
                             depth=self.depth + 1, max_depth=self.max_depth),
            QuadAsteroidTree(asteroids=ne_asteroids, min_x=med_x, max_x=self.max_x,
                             min_y=self.min_y, max_y=med_y, capacity=self.capacity,
                             depth=self.depth + 1,  max_depth=self.max_depth),
            QuadAsteroidTree(asteroids=sw_asteroids, min_x=self.min_x, max_x=med_x,
                             min_y=med_y, max_y=self.max_y, capacity=self.capacity,
                             depth=self.depth + 1,  max_depth=self.max_depth),
            QuadAsteroidTree(asteroids=se_asteroids, min_x=med_x, max_x=self.max_x,
                             min_y=med_y, max_y=self.max_y, capacity=self.capacity,
                             depth=self.depth + 1,  max_depth=self.max_depth)
        ]

    def remove(self, asteroid: Asteroid) -> bool:
        """Remove leave from tree"""
        if isinstance(self.nodes[0] if self.nodes else None, Asteroid):
            if asteroid in self.nodes:
                self.nodes.remove(asteroid)
                return True

            return False

        for child in self.nodes:
            if child.remove(asteroid):
                return True
        return False

    def _contains_coord(self, x: float, y: float) -> bool:
        """
        Check the coordinates to ensure that they are
        in the range from the specified minimum to the maximum
        """
        return (self.min_x <= x <= self.max_x and
            self.min_y <= y <= self.max_y)

    def querry(
            self, min_x: float, min_y: float, max_x: float,
            max_y: float, out: list = None):
        """Funcs compare that asteroids in rage"""
        if out is None:
            out = []

        if (max_x < self.min_x or min_x > self.max_x or
            max_y < self.min_y or min_y > self.max_y):
            return out

        if not self.nodes:
            return out

        if isinstance(self.nodes[0], Asteroid):
            out.extend(self.nodes)
            return out

        for child in self.nodes:
            child.querry(min_x, min_y, max_x, max_y, out)

        return out

    def __str__(self):
        """str magic method"""
        return "Quadtree with asteroids: " + ",".join(map(str, self.nodes))

    def __repr__(self):
        """repr magic method"""
        return "Quadtree with asteroids: " + ",".join(map(str, self.nodes))


class AsteroidManager:
    """Asteroid manager (class that manage asteroid) and
    allows to perform a search in Asteroids by quadtree"""
    def __init__(self, count: int, min_value: float, max_value: float,
                 height: float, width: float, min_speed: float, max_speed: float,
                 capacity: int, use_color: bool):
        """Initialization a class"""
        self.capacity: int = capacity
        self.restart(count, min_value, max_value, height,
                     width, min_speed, max_speed, use_color)

    @staticmethod
    def _random_generate(min, max):
        """Func that generate random value from range"""
        return randint(int(min * 10 ** MLG), int(max * 10 ** MLG)) / 10 ** MLG

    def _random_speed_generate(self, min, max):
        """
        Func that generate random speed from
        range, based on _random_generate()"""
        return self._random_generate(min, max) * (-1) ** randint(1, 2)

    def restart(self, count: int, min_value: float, max_value: float,
                 height: float, width: float, min_speed: float, max_speed: float,
                 use_color: bool):
        """Func that generate new asteroids"""
        self.asteroids = [Asteroid(
            self._random_generate(min_value, max_value),
            self._random_speed_generate(min_speed, max_speed),
            self._random_speed_generate(min_speed, max_speed),
            self._random_generate(max_value, width - max_value),
            self._random_generate(0 + max_value, height - max_value),
            (self._random_color() if use_color else (255, 255, 255))
        ) for _ in range(count)]
        self.height: float = height
        self.width: float = width
        for _ in range(300):
            self.next_step()

    def next_step(self):
        """Performs asteroids advance by one tick"""
        for asteroid in self.asteroids:
            asteroid.next_step(self.height, self.width)

        self.rebuild_tree()
        self.handle_collision()

    def rebuild_tree(self):
        """Generate new tree"""
        self.tree = QuadAsteroidTree(
            asteroids=self.asteroids, min_x=0, max_x=self.width,
            min_y=0, max_y=self.height, capacity=self.capacity)

    def handle_collision(self):
        """
        Func that handle collisions in the plane, based on QuadAsteroidTree
        and querry() (func in QuadAsteroidTree class)"""
        collisions = self.find_collision()
        for col in collisions:
            a1, a2 = col
            dx = a2.x - a1.x
            dy = a2.y - a1.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                a1.x -= a1.radius
                a2.x += a2.radius
                a1.speed_x, a2.speed_x = a2.speed_x, a1.speed_x
                a1.speed_y, a2.speed_y = a2.speed_y, a1.speed_y
                continue

            norm_x, norm_y = dx / dist, dy / dist
            mass_a1 = a1.radius ** 2
            mass_a2 = a2.radius ** 2
            d_norm_x = a2.speed_x - a1.speed_x
            d_norm_y = a2.speed_y - a1.speed_y
            v_res = d_norm_x * norm_x + d_norm_y * norm_y

            if v_res > 0:
                continue

            p = -2 * v_res / (1 / mass_a1 + 1 / mass_a2)
            a1.speed_x -= (p / mass_a1) * norm_x
            a2.speed_x += (p / mass_a2) * norm_x
            a1.speed_y -= (p / mass_a1) * norm_y
            a2.speed_y += (p / mass_a2) * norm_y

            overlap = a1.radius + a2.radius - dist
            if overlap > 0:
                total = mass_a1 + mass_a2
                a1.x -= norm_x * overlap * (mass_a2 / total)
                a1.y -= norm_y * overlap * (mass_a2 / total)
                a2.x += norm_x * overlap * (mass_a1 / total)
                a2.y += norm_y * overlap * (mass_a1 / total)

    def find_collision(self) -> list[tuple]:
        """Func that find collisions in the plane"""
        handled = set()
        pairs = []
        max_r = max(ast.radius for ast in self.asteroids)
        for ast in self.asteroids:
            rad = ast.radius
            for bound in self.tree.querry(
                ast.x - (rad + max_r), ast.y - (rad + max_r),
                ast.x + (rad + max_r), ast.y + (rad + max_r)):
                if bound is ast:
                    continue

                key = (min(id(ast), id(bound)), max(id(ast), id(bound)))
                if key in handled:
                    continue

                handled.add(key)
                dx, dy = bound.x - ast.x, bound.y - ast.y
                if dx*dx + dy*dy < (ast.radius + bound.radius) ** 2:
                    pairs.append((ast, bound))

        return pairs

    @staticmethod
    def _random_color() -> tuple[int]:
        """Random color generate func"""
        return tuple(randint(0, 255) for _ in range(3))
