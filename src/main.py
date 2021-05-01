import krpc

import numpy as np
import math
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
        try:
            self.connection = krpc.connect(name = name)
            print("Connection stablished")
        except Exception as e:
            print("[Err] Could not stablish connection")
            print(f"Errcode was: {e}")

    def get_active_vessel(self):
        """Returns the active vessel"""
        return self.connection.space_center.active_vessel

    def get_space_center(self):
        return self.connection.space_center

    def get_autopilot(self):
        """
        Returns the autopilot
        Autopilot is capable of setting reference frames and pointing to special directions of that
        reference fram
        """
        return self.get_active_vessel().auto_pilot

    def run(self):
        """Runs the actions needed in order to fly"""
        raise NotImplementedError

    def set_sas(self, sas_activated: bool):
        self.get_active_vessel().sas = sas_activated

    def set_throttle(self, throttle: float):
        self.get_active_vessel().control.throttle = throttle

    def get_velocity(self, ref_frame):
        return self.get_active_vessel().velocity(ref_frame)

    def get_vessel_flight(self):
        return self.get_active_vessel().flight(self.get_active_vessel().orbit.body.reference_frame)

    def get_vessel_orbit(self):
        return self.get_active_vessel().orbit


class LegolasVI(BasicSpaceShip):
    """Control LegolasVI spasceship. Working on hitting the moon"""
    def __init__(self):
        # BasicSpaceShip init function
        super(LegolasVI, self).__init__(name = "Main Connection")

        # Displaying some info

    def run(self):
        # Getting some constants
        kerbin = self.get_space_center().bodies.get('Kerbin')
        atmosphere_altitude = kerbin.atmosphere_depth
        print(f"Ascending through {atmosphere_altitude} altitude")

        vessel = self.get_active_vessel()

        # Getting ready for launch
        self.set_sas(True)
        self.set_throttle(1.0)

        # Vertical ascend
        vessel.control.activate_next_stage()
        vessel.auto_pilot.engage()
        vessel.auto_pilot.target_pitch_and_heading(90, 90)

        vel = None
        while vel is None or np.linalg.norm(vel) < 100:
            vel = self.get_velocity(kerbin.reference_frame)
            time.sleep(0.05)

        print("Starting to rotate")
        self.get_autopilot().target_pitch_and_heading(80, 90)
        apoapsis_altitude = None
        while apoapsis_altitude is None or apoapsis_altitude < atmosphere_altitude + 1500:
            apoapsis_altitude = self.get_vessel_orbit().apoapsis
            # TODO -- weird apoapis value
            # TODO -- BUG
            print(f"apoapsis: {apoapsis_altitude}")
            time.sleep(0.05)

        print("Slowing until reaching out of thick air")
        self.set_throttle(0.0)
        altitude = None
        while altitude is None or altitude < atmosphere_altitude:
            altitude = self.get_vessel_flight().mean_altitude
            time.sleep(0.05)

        print("Starting to get in orbit")
        self.set_throttle(1.0)
        self.get_autopilot().target_direction(0, 1, 0)
        periapsis = None
        while periapsis is None or periapsis < atmosphere_altitude:
            periapsis = self.get_vessel_orbit().periapsis
            time.sleep(0.05)

        print("We are done")
        self.set_throttle(0.0)




if __name__== "__main__":
    spaceship = LegolasVI()
    spaceship.run()
    print("==> End of script controller")
