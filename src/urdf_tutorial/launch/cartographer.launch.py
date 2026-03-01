# cartographer.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    
    # 패키지 경로
    pkg_share = FindPackageShare('urdf_tutorial').find('urdf_tutorial')
    
    # cartographer 설정 파일 경로
    cartographer_config_dir = PathJoinSubstitution([pkg_share, 'config'])
    configuration_basename = 'carto.lua'
    
    return LaunchDescription([
        # cartographer node
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{
                'use_sim_time': True
            }],
            arguments=[
                '-configuration_directory', cartographer_config_dir,
                '-configuration_basename', configuration_basename
            ]
        ),
        
        # occupancy grid node (ROS2 Humble에서는 이 이름 사용)
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{
                'use_sim_time': True
            }],
            arguments=['-resolution', '0.05']
        ),
        
        # rviz (선택사항)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', PathJoinSubstitution([pkg_share, 'rviz', 'cartographer.rviz'])],
            parameters=[{
                'use_sim_time': True
            }]
        )
    ])