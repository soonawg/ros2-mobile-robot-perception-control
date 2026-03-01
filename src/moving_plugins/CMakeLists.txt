cmake_minimum_required(VERSION 3.5)
project(moving_plugins)


find_package(ament_cmake REQUIRED)
find_package(gazebo_dev REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(ignition_math6 QUIET)


include_directories(${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})
add_definitions(${GAZEBO_CXX_FLAGS})


# Linear
add_library(LinearMovePlugin SHARED src/LinearMovePlugin.cpp)
ament_target_dependencies(LinearMovePlugin gazebo_dev gazebo_ros)
target_link_libraries(LinearMovePlugin ${GAZEBO_LIBRARIES})


# Circular
add_library(CircularMovePlugin SHARED src/CircularMovePlugin.cpp)
ament_target_dependencies(CircularMovePlugin gazebo_dev gazebo_ros)
target_link_libraries(CircularMovePlugin ${GAZEBO_LIBRARIES})


# Zigzag
add_library(ZigzagMovePlugin SHARED src/ZigzagMovePlugin.cpp)
ament_target_dependencies(ZigzagMovePlugin gazebo_dev gazebo_ros)
target_link_libraries(ZigzagMovePlugin ${GAZEBO_LIBRARIES})


# Random
add_library(RandomMovePlugin SHARED src/RandomMovePlugin.cpp)
ament_target_dependencies(RandomMovePlugin gazebo_dev gazebo_ros)
target_link_libraries(RandomMovePlugin ${GAZEBO_LIBRARIES})


# Path
add_library(PathMovePlugin SHARED src/PathMovePlugin.cpp)
ament_target_dependencies(PathMovePlugin gazebo_dev gazebo_ros)
target_link_libraries(PathMovePlugin ${GAZEBO_LIBRARIES})


install(TARGETS
LinearMovePlugin
CircularMovePlugin
ZigzagMovePlugin
RandomMovePlugin
PathMovePlugin
DESTINATION lib
)


ament_package()