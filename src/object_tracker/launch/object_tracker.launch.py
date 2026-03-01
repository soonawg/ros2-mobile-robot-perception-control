from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Gazebo, Turtlebot3 노드 등은 별도 launch에서 포함
        Node(
            package='object_tracker',
            executable='perception_node',
            name='perception_node',
            output='screen'
        ),
        Node(
            package='object_tracker',
            executable='tracker_node',
            name='tracker_node',
            output='screen'
        ),
    ])