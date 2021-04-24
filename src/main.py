import krpc
import time

class BasicSpaceShip:
    """
    Basic Spaceship. Designed to be used by other spaceships classes with concrete behaviour.
    Gives basic operations for other spaceships to use
    """

    def __init__(self, name: str = "Main Connection"):
        # Atributes
        self.connection = None

        # Connect to krpc server
        self.stablish_connection(name)

    def stablish_connection(self, name):
        """
        Stablish connection to the krcp server

        Parameters:
        ===========
        name: name of the connection
        """
        self.connection = krpc.connect(name = name)

    def get_active_vessel(self):
        """Returns the active vessel"""
        return self.connection.space_center.active_vessel

    def get_autopilot(self):
        """
        Returns the autopilot
        Autopilot is capable of setting reference frames and pointing to special directions of that
        reference fram
        """
        return self.get_active_vessel().auto_pilot

    def run(self):
        """Runs the actions needed in order to fly"""
        raise Exception("Not implemented")

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

class OrbitalSpaceship(BasicSpaceShip):
    def __init__(self):
        # BasicSpaceShip init function
        super(OrbitalSpaceship, self).__init__(name = "Main Connection")

    def run(self):
        vessel = self.get_active_vessel()

        # TODO -- dirty code
        conn = self.connection

        # Point vertically and stabilize direction
        vessel.auto_pilot.target_pitch_and_heading(90, 90)
        vessel.auto_pilot.engage()
        vessel.control.throttle = 1
        time.sleep(1)

        print('Liftoff!')
        vessel.control.activate_next_stage()

        # Wait until fuel is consumed
        fuel_amount = conn.get_call(vessel.resources.amount, 'SolidFuel')
        expr = conn.krpc.Expression.less_than(
            conn.krpc.Expression.call(fuel_amount),
            conn.krpc.Expression.constant_float(0.1))
        event = conn.krpc.add_event(expr)
        with event.condition:
            event.wait()
        print('Booster separation')
        vessel.control.activate_next_stage()

        # Wait until fuel is consumed -- second time
        fuel_amount = conn.get_call(vessel.resources.amount, 'SolidFuel')
        expr = conn.krpc.Expression.less_than(
            conn.krpc.Expression.call(fuel_amount),
            conn.krpc.Expression.constant_float(0.1))
        event = conn.krpc.add_event(expr)
        with event.condition:
            event.wait()
        print('Booster separation')
        vessel.control.activate_next_stage()

        # Reaching apoapsis
        mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
        expr = conn.krpc.Expression.greater_than(
            conn.krpc.Expression.call(mean_altitude),
            conn.krpc.Expression.constant_double(10000))
        event = conn.krpc.add_event(expr)
        with event.condition:
            event.wait()

        print('Gravity turn')
        vessel.auto_pilot.target_pitch_and_heading(60, 90)

        apoapsis_altitude = conn.get_call(getattr, vessel.orbit, 'apoapsis_altitude')
        expr = conn.krpc.Expression.greater_than(
            conn.krpc.Expression.call(apoapsis_altitude),
            conn.krpc.Expression.constant_double(100000))
        event = conn.krpc.add_event(expr)
        with event.condition:
            event.wait()

        print('Launch stage separation')
        vessel.control.throttle = 0
        time.sleep(1)
        vessel.control.activate_next_stage()
        vessel.auto_pilot.disengage()

        # Returning to kerbing
        srf_altitude = conn.get_call(getattr, vessel.flight(), 'surface_altitude')
        expr = conn.krpc.Expression.less_than(
            conn.krpc.Expression.call(srf_altitude),
            conn.krpc.Expression.constant_double(1000))
        event = conn.krpc.add_event(expr)
        with event.condition:
            event.wait()

        vessel.control.activate_next_stage()

        # Ending
        while vessel.flight(vessel.orbit.body.reference_frame).vertical_speed < -0.1:
            print('Altitude = %.1f meters' % vessel.flight().surface_altitude)
            time.sleep(1)
        print('Landed!')

if __name__== "__main__":
    spaceship = OrbitalSpaceship()
    spaceship.run()
    print("==> End of script controller")
