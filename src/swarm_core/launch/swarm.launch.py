import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch arguments
    num_drones_arg = DeclareLaunchArgument(
        'num_drones',
        default_value='5',
        description='Total number of UAVs in the swarm fleet'
    )
    mission_mode_arg = DeclareLaunchArgument(
        'mission_mode',
        default_value='BOIDS',
        description='Mission mode: BOIDS, FORMATION, SEARCH, APF, RTL'
    )
    formation_type_arg = DeclareLaunchArgument(
        'formation_type',
        default_value='V_SHAPE',
        description='Formation type: V_SHAPE, LINE, COLUMN, CIRCLE, GRID'
    )

    num_drones = 5  # default static count for node expansion
    nodes = []

    for i in range(1, num_drones + 1):
        swarm_node = Node(
            package='swarm_core',
            executable='commander',
            name=f'swarm_commander_{i}',
            namespace=f'drone_{i}',
            parameters=[
                {'swarm_id': i},
                {'total_drones': num_drones},
                {'leader_id': 1},
                {'mission_mode': LaunchConfiguration('mission_mode')},
                {'formation_type': LaunchConfiguration('formation_type')},
                {'formation_spacing': 3.5},
                {'cohesion_weight': 1.0},
                {'alignment_weight': 1.0},
                {'separation_weight': 1.8},
                {'perception_radius': 20.0},
                {'safe_distance': 3.0},
                {'obstacle_weight': 2.5},
                {'max_speed': 5.0},
                {'enable_logging': True},
                {'enable_security_ids': True},
                {'failsafe_enabled': True},
            ],
            output='screen',
            emulate_tty=True
        )
        nodes.append(swarm_node)

    return LaunchDescription([
        num_drones_arg,
        mission_mode_arg,
        formation_type_arg,
        *nodes
    ])
