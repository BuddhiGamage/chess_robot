import sys
import os
import threading
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2

# Maximum allowed waiting time during actions (in seconds)
TIMEOUT_DURATION = 30

# Create closure to set an event after an END or an ABORT
def check_for_end_or_abort(e):
    """Return a closure checking for END or ABORT notifications"""
    def check(notification, e=e):
        print("EVENT: " + Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check

def move_to_cartesian_position(base, x, y,z=0.15):
    """
    Move the arm to a given Cartesian position with fixed values for other pose parameters.
    
    Parameters:
        base (BaseClient): The base client object for controlling the robot.
        x (float): The desired x-coordinate.
        y (float): The desired y-coordinate.
    """
    # Fixed values for the Cartesian position
    # z = 0.01  # Fixed z-coordinate
    theta_x = 2.385  # Fixed rotation about x-axis
    theta_y = -176.618   # Fixed rotation about y-axis
    theta_z = 81.918  # Fixed rotation about z-axis
    blending_radius = 0.0  # No blending

    # Set the arm to Single Level Servoing mode
    base_servo_mode = Base_pb2.ServoingModeInformation()
    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    base.SetServoingMode(base_servo_mode)

    # Define the target Cartesian waypoint
    waypoint = Base_pb2.CartesianWaypoint()
    waypoint.pose.x = x
    waypoint.pose.y = y
    waypoint.pose.z = z
    waypoint.pose.theta_x = theta_x
    waypoint.pose.theta_y = theta_y
    waypoint.pose.theta_z = theta_z
    waypoint.blending_radius = blending_radius
    waypoint.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_BASE

    # Create a WaypointList with the defined waypoint
    waypoints = Base_pb2.WaypointList()
    waypoints.waypoints.add().cartesian_waypoint.CopyFrom(waypoint)

    # Verify validity of the waypoint
    result = base.ValidateWaypointList(waypoints)
    if len(result.trajectory_error_report.trajectory_error_elements) == 0:
        e = threading.Event()
        notification_handle = base.OnNotificationActionTopic(
            check_for_end_or_abort(e),
            Base_pb2.NotificationOptions()
        )

        print("Executing Cartesian move...")
        base.ExecuteWaypointTrajectory(waypoints)

        # Wait for the action to finish
        finished = e.wait(TIMEOUT_DURATION)
        base.Unsubscribe(notification_handle)

        if finished:
            print("Move to Cartesian position completed successfully.")
        else:
            print("Timeout on action notification wait.")
    else:
        print("Error found in the trajectory:")
        result.trajectory_error_report.PrintDebugString()

# def main():
#     # Import the utilities helper module
#     sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
#     import utilities

#     # Parse arguments
#     args = utilities.parseConnectionArguments()
    
#     # Create connection to the device and get the router
#     with utilities.DeviceConnection.createTcpConnection(args) as router:
#         # Create required services
#         base = BaseClient(router)

#         # Example core
#         x = 0.147  # Replace with desired x-coordinate
#         y = 0.182  # Replace with desired y-coordinate
#         move_to_cartesian_position(base, x, y)

# if __name__ == "__main__":
#     exit(main())
