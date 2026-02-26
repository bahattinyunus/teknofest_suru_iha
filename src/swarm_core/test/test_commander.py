import unittest
import rclpy
from swarm_core.node_commander import SwarmCommander
from geometry_msgs.msg import PoseStamped, Twist

class TestSwarmCommander(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = SwarmCommander()

    def tearDown(self):
        self.node.destroy_node()

    def test_initialization(self):
        """Test node initialization and default parameters."""
        self.assertEqual(self.node.get_name(), 'swarm_commander')
        self.assertEqual(self.node.swarm_id, 1)

    def test_boids_no_neighbors(self):
        """Test that with no neighbors, velocity is zero."""
        cmd_vel = self.node.calculate_boids_velocity()
        self.assertEqual(cmd_vel.linear.x, 0.0)
        self.assertEqual(cmd_vel.linear.y, 0.0)
        self.assertEqual(cmd_vel.linear.z, 0.0)

    def test_boids_with_neighbor(self):
        """Test basic reaction to a neighbor."""
        # Setup a neighbor pose
        neighbor_pose = PoseStamped()
        neighbor_pose.header.frame_id = "2"
        neighbor_pose.pose.position.x = 5.0
        neighbor_pose.pose.position.y = 0.0
        
        # Add to neighbors directly for testing
        self.node.neighbors["2"] = neighbor_pose
        
        # Node itself is at 0, 0
        cmd_vel = self.node.calculate_boids_velocity()
        
        # distance is 5.0. Perception radius is 15.0 by default.
        # it will be considered.
        # Ensure it doesn't just crash and returns a Twist message
        self.assertIsInstance(cmd_vel, Twist)
        
        # Based on default logic, it should move towards the neighbor (cohesion)
        self.assertNotEqual(cmd_vel.linear.x, 0.0)

if __name__ == '__main__':
    unittest.main()
