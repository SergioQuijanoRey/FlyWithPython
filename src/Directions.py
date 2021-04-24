"""
Manage directions in different frames
All directions need a reference frame. This reference frame is given by an autopilot object.
Therefore all kind of directions are constructed from an autopilot object
"""

# TODO -- not sure about what I am doing here
class OrbitalDirections:
    """Orbital directios, given by the autopilot"""
    def __init__(self, autopilot):
        self.autopilot = autopilot

    def prograde(self):
        return (0, 1, 0)

    def retrograde(self):
        return (0, -1, 0)

    def normal(self):
        return (0, 0, 1)

    def antinormal(self):
        return (0, 0, -1)

    def radialin(self):
        return (1, 0, 0)

    def radialout(self):
        return (-1, 0, 0)
