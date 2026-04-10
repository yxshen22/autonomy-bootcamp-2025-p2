"""
Heartbeat sending logic.
"""

from pymavlink import mavutil


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatSender:
    """
    HeartbeatSender class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        heartbeat_period,  # Put your own arguments here
    ) -> "tuple[True, HeartbeatSender] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatSender object.
        """
        if connection is None:
            return (False, None)
        return (True, cls(cls.__private_key, connection, heartbeat_period))

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        heartbeat_period
    ):
        assert key is HeartbeatSender.__private_key, "Use create() method"

        # Do any intializiation here
        self._connection = connection
        self._heartbeat_period = heartbeat_period

    def run(
        self,
        heartbeat_period=None
    ):
        """
        Attempt to send a heartbeat message.
        """
        period = heartbeat_period if heartbeat_period is not None else self._heartbeat_period
        # Send a heartbeat message
        self._connection.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS, 
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, # base_mode
            0, # custom_mode
            mavutil.mavlink.MAV_STATE_ACTIVE
        )


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
