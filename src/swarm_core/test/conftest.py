import sys
import os
from unittest.mock import MagicMock

# Ensure src/swarm_core is in sys.path
core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

# Mock ROS 2 packages if not installed in the current environment
try:
    import rclpy
except ImportError:
    mock_rclpy = MagicMock()
    mock_node = MagicMock()

    class MockNodeBase:
        def __init__(self, node_name='mock_node', **kwargs):
            self._node_name = node_name
            self._logger = MagicMock()

        def get_logger(self):
            return self._logger

        def declare_parameter(self, name, default_value):
            class MockParam:
                def __init__(self, val):
                    self.value = val
            if not hasattr(self, '_params'):
                self._params = {}
            self._params[name] = MockParam(default_value)
            return self._params[name]

        def get_parameter(self, name):
            class MockParam:
                def __init__(self, val):
                    self.value = val
            return getattr(self, '_params', {}).get(name, MockParam(None))

        def create_subscription(self, msg_type, topic, callback, qos_profile):
            return MagicMock()

        def create_publisher(self, msg_type, topic, qos_profile):
            pub = MagicMock()
            pub.publish = MagicMock()
            return pub

        def create_timer(self, timer_period_sec, callback):
            return MagicMock()

        def get_clock(self):
            clock = MagicMock()
            now = MagicMock()
            now.nanoseconds = 1000000000
            now_msg = MagicMock()
            now_msg.sec = 1
            now.to_msg.return_value = now_msg
            now.__sub__ = lambda self, other: now
            clock.now.return_value = now
            return clock

        def get_name(self):
            return self._node_name

        def destroy_node(self):
            pass

    mock_rclpy.node.Node = MockNodeBase
    sys.modules['rclpy'] = mock_rclpy
    sys.modules['rclpy.node'] = mock_rclpy.node

    # Mock geometry_msgs
    geom_mock = MagicMock()

    class Point:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x, self.y, self.z = x, y, z

    class Header:
        def __init__(self, frame_id=""):
            self.frame_id = frame_id
            self.stamp = MagicMock()

    class Pose:
        def __init__(self):
            self.position = Point()
            self.orientation = MagicMock()

    class PoseStamped:
        def __init__(self):
            self.header = Header()
            self.pose = Pose()

    class Vector3Msg:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x, self.y, self.z = x, y, z

    class Twist:
        def __init__(self):
            self.linear = Vector3Msg()
            self.angular = Vector3Msg()

    geom_mock.PoseStamped = PoseStamped
    geom_mock.Twist = Twist
    geom_mock.Point = Point
    geom_mock.Vector3 = Vector3Msg
    sys.modules['geometry_msgs'] = MagicMock()
    sys.modules['geometry_msgs.msg'] = geom_mock

    # Mock mavros_msgs
    mavros_mock = MagicMock()

    class State:
        def __init__(self):
            self.connected = True
            self.armed = True
            self.mode = "OFFBOARD"

    mavros_mock.State = State
    sys.modules['mavros_msgs'] = MagicMock()
    sys.modules['mavros_msgs.msg'] = mavros_mock

    # Mock sensor_msgs
    sensor_mock = MagicMock()

    class LaserScan:
        def __init__(self):
            self.ranges = []
            self.angle_min = -3.14
            self.angle_max = 3.14
            self.angle_increment = 0.05
            self.range_min = 0.1
            self.range_max = 30.0

    sensor_mock.LaserScan = LaserScan
    sys.modules['sensor_msgs'] = MagicMock()
    sys.modules['sensor_msgs.msg'] = sensor_mock
