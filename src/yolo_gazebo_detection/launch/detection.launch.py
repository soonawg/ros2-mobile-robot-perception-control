from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition

def generate_launch_description():
    # 패키지 경로
    pkg_share = FindPackageShare('yolo_gazebo_detection')
    
    # 런치 인수
    use_gazebo = LaunchConfiguration('use_gazebo')
    world_file = LaunchConfiguration('world_file')
    use_rviz = LaunchConfiguration('use_rviz')
    
    return LaunchDescription([
        # 런치 인수 선언
        DeclareLaunchArgument(
            'use_gazebo',
            default_value='true',
            description='Gazebo 시뮬레이터 사용 여부'
        ),
        
        DeclareLaunchArgument(
            'world_file',
            default_value=PathJoinSubstitution([pkg_share, 'worlds', 'detection_world.world']),
            description='Gazebo 월드 파일 경로'
        ),
        
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='RViz 사용 여부'
        ),
        
        # Gazebo 실행
        ExecuteProcess(
            condition=IfCondition(use_gazebo),
            cmd=['gazebo', '--verbose', world_file, '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),
        
        # TurtleBot3 스폰
        TimerAction(
            period=3.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'run', 'gazebo_ros', 'spawn_entity.py', 
                         '-entity', 'turtlebot3_waffle_pi', 
                         '-file', '/opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf',
                         '-x', '0.0', '-y', '0.0', '-z', '0.0'],
                    output='screen'
                )
            ]
        ),
        
        # 노드들 실행 (Gazebo 로드 후)
        TimerAction(
            period=8.0,
            actions=[
                # YOLO 감지 노드
                Node(
                    package='yolo_gazebo_detection',
                    executable='yolo_detector',
                    name='yolo_detector',
                    output='screen',
                    parameters=[{
                        'confidence_threshold': 0.5,
                        'model_path': 'yolov8n.pt'
                    }]
                ),
                
                # 카메라 노드
                Node(
                    package='yolo_gazebo_detection',
                    executable='gazebo_camera',
                    name='gazebo_camera',
                    output='screen'
                ),
                
                # 시각화 노드
                Node(
                    package='yolo_gazebo_detection',
                    executable='visualization',
                    name='visualization',
                    output='screen'
                ),
                
                # RViz 실행
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    arguments=['-d', PathJoinSubstitution([pkg_share, 'config', 'detection.rviz'])],
                    output='screen',
                    condition=IfCondition(use_rviz)
                )
            ]
        )
    ])