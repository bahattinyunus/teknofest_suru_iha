import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Number of drones in the swarm (default 3 for demonstration)
    num_drones = 3
    nodes = []

    # Dynamically generate commander nodes for each drone in the swarm
    for i in range(1, num_drones + 1):
        swarm_node = Node(
            package='swarm_core',
            executable='commander',
            name=f'swarm_commander_{i}',
            # Running them all in the same namespace is optional, 
            # but usually they would be namespaced like /drone1 /drone2 etc
            namespace=f'drone_{i}',
            parameters=[
                {'swarm_id': i},
                {'cohesion_weight': 1.0},
                {'alignment_weight': 1.0},
                {'separation_weight': 1.5},
                {'perception_radius': 20.0},
            ],
            output='screen',
            emulate_tty=True
        )
        nodes.append(swarm_node)

    return LaunchDescription(nodes)
