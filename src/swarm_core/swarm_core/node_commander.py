#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State

class SwarmCommander(Node):
    def __init__(self):
        super().__init__('swarm_commander')
        self.get_logger().info('Sürü Komutanı Başlatıldı, emirler bekleniyor...')
        
        # Parametreleri yükle
        self.declare_parameter('swarm_id', 1)
        self.swarm_id = self.get_parameter('swarm_id').value
        
        # Abonelikler (Subscribers)
        self.state_sub = self.create_subscription(
            State,
            f'mavros/state',
            self.state_cb,
            10
        )
        
        self.current_state = State()

    def state_cb(self, msg):
        self.current_state = msg

def main(args=None):
    rclpy.init(args=args)
    node = SwarmCommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
