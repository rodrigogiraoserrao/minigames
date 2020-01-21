from math import sqrt

class Follower(object):
    def __init__(self, pos, follow, delay):
        """Creates a new Follower that starts at the given position, follows
        the given object with the specified delay in number of frames"""
        self.pos = pos
        self.follow = follow
        self.point_to = self.follow.pos[::]
        self.delay = delay
        self.positions = []

    def move(self, speed):
        self.positions.append(self.follow.pos[::])
        if len(self.positions) <= self.delay:
            p = self.point_to
        else:
            p = self.positions.pop(0)
        direction = [p[0]-self.pos[0], p[1]-self.pos[1]]
        distance = sqrt(direction[0]**2 + direction[1]**2)
        if distance <= speed:
            self.pos = p
        else:
            dx = direction[0]/distance*speed
            dy = direction[1]/distance*speed
            self.pos[0] += dx
            self.pos[1] += dy

def FollowerFactory(delay, speed):
    class Creeper(Follower):
        def __init__(self, pos, follow):
            Follower.__init__(self, pos, follow, delay)

        def move(self):
            Follower.move(self, speed)

    return Creeper