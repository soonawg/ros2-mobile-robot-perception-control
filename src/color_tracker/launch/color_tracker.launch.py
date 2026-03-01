from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='color_tracker',
            executable='color_tracker',
            name='color_follower',
            output='screen'
        )
    ])