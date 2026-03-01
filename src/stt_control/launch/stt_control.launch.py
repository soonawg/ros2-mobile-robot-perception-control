from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='stt_control',
            executable='stt_node',
            name='stt_control_node',
            output='screen'
        )
    ])