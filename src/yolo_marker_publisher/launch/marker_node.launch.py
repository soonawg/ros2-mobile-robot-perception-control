from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """
    YOLO 객체 탐지 + RViz Marker 퍼블리시 노드 실행 launch 파일

    - 카메라 이미지 토픽: /camera/image_raw
    - 마커 퍼블리시 토픽: /detected_objects/markers
    """
    return LaunchDescription([
        Node(
            package='yolo_marker_publisher',
            executable='marker_node',
            name='yolo_marker_node',
            output='screen'
        )
    ])