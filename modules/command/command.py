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
        command_queue,
        output_queue,
        command_period: float, # seconds between decisions
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a Command object.
        """
        pass  #  Create a Command object

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        command_queue,
        output_queue,
        command_period: float,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        self._connection = connection
        self._target = target
        self._command_queue = command_queue
        self._output_queue = output_queue
        self._command_period = command_period
        self._logger = local_logger

    def run(
        self,
        telemetry_data: telemetry.TelemetryData
    ):
        """
        Make a decision based on received telemetry data.
        """
        # Log average velocity for this trip so far

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"

        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
