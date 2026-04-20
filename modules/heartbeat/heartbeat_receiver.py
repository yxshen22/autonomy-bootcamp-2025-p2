"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        heartbeat_period: float,
        disconnect_threshold: int,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        if connection is None or local_logger is None:
            return False, None
        return True, cls(
            cls.__private_key, connection, heartbeat_period, disconnect_threshold, local_logger
        )

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        heartbeat_period: float,
        disconnect_threshold: int,
        local_logger: logger.Logger,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        self._connection = connection
        self._heartbeat_period = heartbeat_period
        self._disconnect_threshold = disconnect_threshold
        self._logger = local_logger
        self._missed_count = 0

    def run(
        self,
        heartbeat_period: float | None = None,
    ) -> str:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        period = heartbeat_period if heartbeat_period is not None else self._heartbeat_period
        msg = self._connection.recv_match(type="HEARTBEAT", blocking=True, timeout=period)

        if msg and msg.get_type() == "HEARTBEAT":
            self._missed_count = 0
            return "Connected"

        self._missed_count += 1
        self._logger.warning(
            f"Missed heartbeat {self._missed_count}/{self._disconnect_threshold}", True
        )
        if self._missed_count >= self._disconnect_threshold:
            return "Disconnected"
        return "Connected"


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
