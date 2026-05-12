"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    height_tolerance: float,
    angle_tolerance: float,
    z_speed: float,
    turning_speed: float,
    input_queue: queue_proxy_wrapper.QueueProxyWrapper,
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,
    controller: worker_controller.WorkerController,
) -> None:
    """
    Worker process.

    height_tolerance: altitude tolerance in meters
    angle_tolernace: angle tolerance in degrees
    z_speed: m/s
    turning_speed: deg/s
    input_queue: TelemetryData inputs
    output_queue: string outputs
    controller: pause/stop
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (command.Command)
    result, command_obj = command.Command.create(
        connection,
        target,
        height_tolerance,
        angle_tolerance,
        z_speed,
        turning_speed,
        local_logger,
    )
    if not result:
        local_logger.error("Failed to create Command object", True)
        return
    
    assert command_obj is not None

    # Main loop: do work.
    while not controller.is_exit_requested():
        controller.check_pause()
        try:  # use timeout so worker can notice controller.request_exit() otherwise it'll block forever
            telemetry_data = input_queue.queue.get()
        except input_queue.queue.Empty:
            continue
        output = command_obj.run(telemetry_data)
        if output is not None:
            output_queue.queue.put(output)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
