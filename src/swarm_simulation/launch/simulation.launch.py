import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_swarm_sim = get_package_share_directory('swarm_simulation')
    pkg_swarm_core = get_package_share_directory('swarm_core')

    # Arguments
    use_mock_arg = DeclareLaunchArgument(
        'use_mock',
        default_value='false',
        description='Launch fast physics SITL simulator instead of Gazebo'
    )

    arena_world_path = os.path.join(pkg_swarm_sim, 'worlds', 'teknofest_arena.world')
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=arena_world_path,
        description='Full path to Gazebo world file'
    )

    # Gazebo simulation
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        ),
        launch_arguments={'world': LaunchConfiguration('world')}.items(),
        condition=UnlessCondition(LaunchConfiguration('use_mock'))
    )

    # Fast Mock SITL node
    mock_sitl_node = Node(
        package='swarm_simulation',
        executable='mock_sitl',
        name='mock_sitl_bridge',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_mock'))
    )

    # Swarm Core Logic
    swarm_logic = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_swarm_core, 'launch', 'swarm.launch.py'),
        )
    )

    return LaunchDescription([
        use_mock_arg,
        world_arg,
        gazebo,
        mock_sitl_node,
        swarm_logic
    ])
