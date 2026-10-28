import unittest
from swarm_core.node_commander import SwarmCommander
from swarm_core.algorithms import Vector3
from geometry_msgs.msg import PoseStamped, Twist


class TestSwarmCommander(unittest.TestCase):
    def setUp(self):
        self.node = SwarmCommander()

    def tearDown(self):
        self.node.destroy_node()

    def test_initialization(self):
        """Test node initialization and default parameters."""
        self.assertEqual(self.node.get_name(), 'swarm_commander')
        self.assertEqual(self.node.swarm_id, 1)

    def test_boids_cmd_generation(self):
        """Test that SwarmCommander produces valid velocity vector."""
        cmd = self.node.calculate_boids_cmd()
        self.assertIsInstance(cmd, Vector3)

    def test_neighbor_tracking_and_boids(self):
        """Test that adding a neighbor affects swarm velocity calculation."""
        # Simulate receiving neighbor telemetry
        self.node.neighbors['2'] = {
            'pos': Vector3(4.0, 0.0, 10.0),
            'vel': Vector3(0.0, 0.0, 0.0),
            'time': 1000.0
        }
        cmd = self.node.calculate_boids_cmd()
        self.assertIsInstance(cmd, Vector3)
        # With default cohesion, it should move towards neighbor (+x)
        self.assertGreater(cmd.x, 0.0)

    def test_formation_cmd_generation(self):
        """Test formation command generation in leader and follower roles."""
        # Leader mode (swarm_id == leader_id == 1)
        cmd_leader = self.node.calculate_formation_cmd()
        self.assertIsInstance(cmd_leader, Vector3)

        # Follower mode (set swarm_id to 2)
        self.node.swarm_id = 2
        self.node.neighbors['1'] = {
            'pos': Vector3(0.0, 0.0, 10.0),
            'vel': Vector3(2.0, 0.0, 0.0),
            'time': 1000.0
        }
        cmd_follower = self.node.calculate_formation_cmd()
        self.assertIsInstance(cmd_follower, Vector3)

    def test_heterogeneous_role_assignment(self):
        """Test heterogeneous UAV role configuration."""
        self.assertEqual(self.node.uav_role, 'STANDARD')
        self.assertIsNotNone(self.node.engagement_controller)
        self.assertEqual(self.node.engagement_controller.current_state, 'IDLE')


if __name__ == '__main__':
    unittest.main()
