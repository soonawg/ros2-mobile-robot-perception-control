from setuptools import find_packages, setup

package_name = 'sensor_subscriber'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hpmcsg1wl7',
    maintainer_email='hansangu093@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'scan_listener = sensor_subscriber.scan_listener:main',
            'odom_listener = sensor_subscriber.odom_listener:main',
            'image_subscriber = sensor_subscriber.image_subscriber:main',
        ],
    },
)
