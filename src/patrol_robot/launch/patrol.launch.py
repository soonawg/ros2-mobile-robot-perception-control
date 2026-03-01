from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='patrol_robot',
            executable='yolo_detector',
            name='yolo_detector',
            output='screen'
        ),
        Node(
            package='patrol_robot',
            executable='object_tracker',
            name='object_tracker',
            output='screen'
        ),
        Node(
            package='patrol_robot',
            executable='navigator_node',
            name='navigator_node',
            output='screen'
        ),
    ])
