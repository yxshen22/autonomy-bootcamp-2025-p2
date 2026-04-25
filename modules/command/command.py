"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        height_tolerance: float,
        angle_tolerance: float,
        z_speed: float,
        turning_speed: float,
        local_logger: logger.Logger,
    ) -> tuple[bool, "Command | None"]:
        """
        Falliable create (instantiation) method to create a Command object.
        """
        if connection is None or local_logger is None:
            return False, None
        return True, cls(
            cls.__private_key,
            connection,
            target,
            height_tolerance,
            angle_tolerance,
            z_speed,
            turning_speed,
            local_logger,
        )

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        height_tolerance: float,
        angle_tolerance: float,
        z_speed: float,
        turning_speed: float,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        self._connection = connection
        self._target = target
        self._height_tolerance = height_tolerance
        self._angle_tolerance = angle_tolerance
        self._z_speed = z_speed
        self._turning_speed = turning_speed
        self._logger = local_logger

        # for avg velocity
        self._count = 0
        self._sum_vx = 0.0
        self._sum_vy = 0.0
        self._sum_vz = 0.0

    def run(self, telemetry_data: telemetry.TelemetryData) -> str | None:
        """
        Make a decision based on received telemetry data.
        """
        if telemetry_data is None:
            return None

        # Log average velocity for this trip so far
        self._count += 1
        self._sum_vx += telemetry_data.x_velocity
        self._sum_vy += telemetry_data.y_velocity
        self._sum_vz += telemetry_data.z_velocity

        avg_vx = self._sum_vx / self._count
        avg_vy = self._sum_vy / self._count
        avg_vz = self._sum_vz / self._count
        self._logger.info(
            f"Average velocity: ({avg_vx:.3f}, {avg_vy:.3f}, {avg_vz:.3f})",
            True,
        )

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"
        dz = self._target.z - telemetry_data.z
        if abs(dz) > self._height_tolerance:
            self._logger.info(f"Sending CHANGE_ALT with target_alt={self._target.z}", True)

            self._connection.mav.command_long_send(
                1,  # target system
                0,  # target_component
                mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                0,  # confirmation
                self._z_speed,  # param1: climb rate
                0,
                0,
                0,
                0,
                0,
                self._target.z,  # param7: absolute target altitude (not delta altitude)
            )
            return f"CHANGE ALTITUDE: {dz}"
        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system
        dx = self._target.x - telemetry_data.x
        dy = self._target.y - telemetry_data.y
        desired_yaw = math.atan2(dy, dx)
        current_yaw = telemetry_data.yaw

        delta = desired_yaw - current_yaw
        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi

        delta_deg = math.degrees(delta)
        if abs(delta_deg) > self._angle_tolerance:
            direction = 1 if delta_deg > 0 else -1
            self._connection.mav.command_long_send(
                1,  # target_system
                0,  # target_component
                mavutil.mavlink.MAV_CMD_CONDITION_YAW,
                0,  # confirmation
                abs(delta_deg),  # param1: angle (deg)
                self._turning_speed,  # param2: turning speed
                direction,  # param3: direction
                1,  # param4: relative
                0,
                0,
                0,
            )
            return f"CHANGE YAW: {delta_deg}"

        return None


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
