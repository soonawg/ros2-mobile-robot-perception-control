from setuptools import find_packages, setup

package_name = 'stt_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/stt_control.launch.py']),
    ],
    install_requires=[
        'setuptools',
        'torch',
        'openai-whisper',
        'transformers',
        'rclpy',
        'geometry_msgs',
    ],
    zip_safe=True,
    maintainer='soonawg',
    maintainer_email='hansangu093@gmail.com',
    description='음성(STT) 자연어 명령으로 Turtlebot3를 제어하는 ROS2 패키지',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'stt_node = stt_control.stt_node:main',
        ],
    },
)
