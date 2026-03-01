from setuptools import find_packages, setup

package_name = 'control_ws'

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
            'pid_control = control_ws.pid_control:main',
            'mpc_control = control_ws.mpc_control:main',
            'impedance_control = control_ws.impedance_control:main'
        ],
    },
)
