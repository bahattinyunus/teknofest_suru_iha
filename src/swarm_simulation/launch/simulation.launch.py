import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_swarm_sim = get_package_share_directory('swarm_simulation')
    pkg_swarm_core = get_package_share_directory('swarm_core')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )

    # Swarm Logic Launch
    swarm_logic = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_swarm_core, 'launch', 'swarm.launch.py'),
        )
    )

    return LaunchDescription([
        gazebo,
        swarm_logic
    ])
