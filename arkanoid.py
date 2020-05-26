import random
import time
import pygame
import pyglet
import pymunk
from pyglet.window import key
from pymunk.pyglet_util import DrawOptions
from pymunk.vec2d import Vec2d

collision_types = {
    "ball": 1,
    "brick": 2,
    "ordinaryBalls": 3,
    "cullBalls": 4,
    "bottom": 5,
    "platform": 6,
    "rectangle": 7,
    "bonus": 8
}


class Bonus:
    def __init__(self, space, x, y):
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        body.position = x + 35, y
        shape = pymunk.Circle(body, 12)
        shape.color = pygame.color.THECOLORS["gold"]
        shape.elasticity = 0.98
        shape.collision_type = collision_types["bonus"]
        body.velocity = 0, -100
        body.on_platform = False
        space.add(body, shape)

        handler = space.add_collision_handler(collision_types["platform"], collision_types["bonus"])
        handler.separate = self.remove_bonus

    def remove_bonus(self, arbiter, space, data):
        bonus = arbiter.shapes[1]
        space.remove(bonus, bonus.body)
        flag = random.choice[1, 2, 3, 4]
        if flag == 1:
            window.slow()


class Rectangle:
    def __init__(self, space):
        for x in range(2):
            for y in range(2):
                body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
                body.position = x * 850 + 165, y * 280 + 400
                body.x = x * 850 + 165
                body.y = y * 280 + 400
                shape = pymunk.Segment(body, (0, 0), (70, 0), 12)
                shape.color = pygame.color.THECOLORS["red"]
                shape.elasticity = 0.98
                shape.collision_type = collision_types["rectangle"]
                space.add(body, shape)

        handler = space.add_collision_handler(collision_types["rectangle"], collision_types["ball"])
        handler.separate = self.remove_rectangle

    def remove_rectangle(self, arbiter, space, data):
        rectangle = arbiter.shapes[0]
        space.bonus = Bonus(space, rectangle.body.x, rectangle.body.y)
        space.remove(rectangle, rectangle.body)
        flag = 1
        if flag == 1:
            window.slow()


# обычные шары, разбивающиеся с первого удара
class OrdinaryBalls:
    def __init__(self, space):
        for x in range(8):
            for y in range(6):
                if (x == 0 and (y == 0 or y == 4)) or (x == 6 and (y == 0 or y == 4)):
                    continue
                else:
                    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
                    body.position = (2 * x + 1) * 70 + 100, y * 70 + 400
                    shape = pymunk.Circle(body, 20)
                    shape.color = pygame.color.THECOLORS["pink"]
                    shape.elasticity = 0.98
                    shape.collision_type = collision_types["ordinaryBalls"]
                    space.add(body, shape)

        handler = space.add_collision_handler(collision_types["ordinaryBalls"], collision_types["ball"])
        handler.separate = self.remove_ordinary_balls

    def remove_ordinary_balls(self, arbiter, space, data):
        ordinary_balls_shape = arbiter.shapes[0]
        ball = arbiter.shapes[1]
        ball.count = 1
        space.remove(ordinary_balls_shape, ordinary_balls_shape.body)


# клевые шары, их необходимо ударить два раза, чтобы разбить
class CullBalls:
    def __init__(self, space):
        for x in range(8):
            for y in range(6):
                if (x == 1 and (y == 0 or y == 4)) or (x == 7 and (y == 0 or y == 4)):
                    continue
                else:
                    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
                    body.position = (2 * x) * 70 + 100, y * 70 + 400
                    body.flag = False
                    shape = pymunk.Circle(body, 20)
                    shape.color = pygame.color.THECOLORS["orange"]
                    shape.elasticity = 0.98
                    shape.collision_type = collision_types["cullBalls"]
                    space.add(body, shape)

        handler = space.add_collision_handler(collision_types["cullBalls"], collision_types["ball"])
        handler.separate = self.remove_cull_balls

    def remove_cull_balls(self, arbiter, space, data):
        cull_ball_shape = arbiter.shapes[0]
        ball = arbiter.shapes[1]
        ball.count = 1
        if not cull_ball_shape.body.flag:
            cull_ball_shape.body.flag = True
        else:
            space.remove(cull_ball_shape, cull_ball_shape.body)


class Walls:
    def __init__(self, space):
        left = pymunk.Segment(space.static_body, (50, 50), (50, 800), 2)
        up = pymunk.Segment(space.static_body, (50, 800), (1200, 800), 2)
        right = pymunk.Segment(space.static_body, (1200, 800), (1200, 50), 2)

        left.elasticity = 0.98
        up.elasticity = 0.98
        right.elasticity = 0.98

        down = pymunk.Segment(space.static_body, (50, 50), (1200, 50), 2)
        down.sensor = True
        down.collision_type = collision_types["bottom"]

        left.color = pygame.color.THECOLORS["khaki"]
        up.color = pygame.color.THECOLORS["khaki"]
        right.color = pygame.color.THECOLORS["khaki"]
        down.color = pygame.color.THECOLORS["khaki"]

        handler = space.add_collision_handler(collision_types["ball"], collision_types["bottom"])
        handler.begin = self.reset_game

        space.add(left, up, right, down)

    def reset_game(self, arbiter, space, data):
        window.reset_game()
        return True


class Ball(pymunk.Body):
    def __init__(self, space, position):
        super().__init__(1, pymunk.inf)
        self.position = position.x, position.y + 18
        shape = pymunk.Circle(self, 10)
        shape.color = pygame.color.THECOLORS["hotpink"]
        shape.elasticity = 0.98
        shape.collision_type = collision_types["ball"]
        self.spc = space
        self.count = 500
        self.flag = False
        self.flag_fast = False
        self.flag2 = True
        self.on_paddle = True
        self.velocity_func = self.constant_velocity

        space.add(self, shape)

    # рандомно выбираем, куда полетит шарик после "выстрела"
    def shoot(self):
        self.on_paddle = False
        direction = Vec2d(random.choice([(50, 250), (-50, 250)]))
        self.apply_impulse_at_local_point(direction)

    # необходимо, чтобы после соударений шарик не терял скорость,
    # поэтому после каждого удара нормализуем вектор его скорости и делаем его длину равно 500
    def constant_velocity(self, body, gravity, damping, dt):
        self.velocity = self.velocity.normalized()
        self.velocity *= self.count

    def update(self, platform):
        if self.flag:
            if self.flag2:
                self.count /= 2
                self.flag2 = False
        if self.on_paddle:
            self.velocity = platform.velocity
            self.position.x = platform.position.x
            self.position.y = platform.position.y + 18


class Platform(pymunk.Body):
    def __init__(self, space):
        super().__init__(10, pymunk.inf)
        self.position = 640, 100
        shape = pymunk.Segment(self, (-50, 0), (50, 0), 8)
        shape.color = pygame.color.THECOLORS["cyan"]
        shape.elasticity = 0.98
        shape.collision_type = collision_types["platform"]

        joint = pymunk.GrooveJoint(space.static_body, self, (150, 100), (1100, 100), (0, 0))

        space.add(self, shape, joint)


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_location(300, 50)

        self.space = pymunk.Space()
        self.options = DrawOptions()

        self.platform = Platform(self.space)
        self.ball = Ball(self.space, self.platform.position)
        self.walls = Walls(self.space)
        self.ordinary_balls = OrdinaryBalls(self.space)
        self.cull_balls = CullBalls(self.space)
        self.rectangle = Rectangle(self.space)

    def on_draw(self):
        self.clear()
        self.space.debug_draw(self.options)

    def slow(self):
        self.ball.flag = True
    def fast(self):
        self.ball.flag_fast= True
    def on_key_press(self, symbol, modifiers):
        if symbol == key.RIGHT:
            self.platform.velocity = 600, 0
            if self.ball.on_paddle:
                self.ball.velocity = 600, 0
                self.ball.position = self.platform.position.x, self.platform.position.y + 18
        if symbol == key.LEFT:
            self.platform.velocity = -600, 0
            if self.ball.on_paddle:
                self.ball.velocity = -600, 0
                self.ball.position = self.platform.position.x, self.platform.position.y + 18
        if symbol == key.SPACE:
            if self.ball.on_paddle:
                self.ball.shoot()
        if symbol == key.R:
            self.reset_game()
            self.ordinary_balls = OrdinaryBalls(self.space)
            self.cull_balls = CullBalls(self.space)
            self.rectangle = Rectangle(self.space)

    def on_key_release(self, symbol, modifiers):
        if symbol in (key.LEFT, key.RIGHT):
            self.platform.velocity = 0, 0
            if self.ball.on_paddle:
                self.ball.velocity = 0, 0

    def reset_game(self):
        for shape in self.space.shapes:
            if shape.body != self.space.static_body and shape.body.body_type != pymunk.Body.KINEMATIC:
                self.space.remove(shape.body, shape)
        for constraint in self.space.constraints:
            self.space.remove(constraint)
        self.platform = Platform(self.space)
        self.ball = Ball(self.space, self.platform.position)

    def update(self, dt):
        self.space.step(dt)
        self.ball.update(self.platform)
    def time(self):
        time.sleep(1800)

if __name__ == "__main__":
    window = GameWindow(1250, 850, "Arkanoid", resizable=False)
    pyglet.clock.schedule_interval(window.update, 1 / 120.0)
    pyglet.app.run()
