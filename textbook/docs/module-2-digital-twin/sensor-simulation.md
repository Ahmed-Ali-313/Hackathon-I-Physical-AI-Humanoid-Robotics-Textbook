---
sidebar_position: 3
title: Sensor Simulation
description: Simulating cameras, LiDAR, IMU, and other sensors for perception development
keywords: [sensors, camera, lidar, imu, simulation, perception]
---

# Sensor Simulation

## Overview

Accurate sensor simulation is critical for developing and testing perception systems before hardware deployment. This chapter covers simulation of cameras, LiDAR, IMU, force/torque sensors, and other sensors used in humanoid robotics.

## Camera Simulation

### RGB Camera

```xml
<!-- Gazebo RGB camera sensor -->
<sensor name="rgb_camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>1920</width>
      <height>1080</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.007</stddev>
    </noise>
  </camera>
  <update_rate>30</update_rate>
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>image_raw:=camera/rgb/image_raw</remapping>
      <remapping>camera_info:=camera/rgb/camera_info</remapping>
    </ros>
  </plugin>
</sensor>
```

### Depth Camera (Intel RealSense)

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2
from cv_bridge import CvBridge
import numpy as np

class DepthCameraProcessor(Node):
    def __init__(self):
        super().__init__('depth_camera_processor')

        self.bridge = CvBridge()

        # Subscribe to depth image
        self.depth_sub = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            10
        )

        # Publish point cloud
        self.pc_pub = self.create_publisher(
            PointCloud2,
            '/camera/depth/points',
            10
        )

    def depth_callback(self, msg):
        # Convert depth image to point cloud
        depth_image = self.bridge.imgmsg_to_cv2(msg, '32FC1')
        point_cloud = self.depth_to_pointcloud(depth_image)
        self.pc_pub.publish(point_cloud)

    def depth_to_pointcloud(self, depth_image):
        # Camera intrinsics
        fx, fy = 525.0, 525.0
        cx, cy = 319.5, 239.5

        # Generate point cloud
        points = []
        h, w = depth_image.shape
        for v in range(h):
            for u in range(w):
                z = depth_image[v, u]
                if z > 0:
                    x = (u - cx) * z / fx
                    y = (v - cy) * z / fy
                    points.append([x, y, z])

        return self.create_pointcloud2(points)
```

## LiDAR Simulation

### 3D LiDAR (Velodyne/Ouster)

```xml
<!-- Gazebo 3D LiDAR sensor -->
<sensor name="lidar_3d" type="gpu_ray">
  <pose>0 0 0.5 0 0 0</pose>
  <ray>
    <scan>
      <horizontal>
        <samples>1024</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>
      <vertical>
        <samples>128</samples>
        <resolution>1</resolution>
        <min_angle>-0.436</min_angle>
        <max_angle>0.436</max_angle>
      </vertical>
    </scan>
    <range>
      <min>0.1</min>
      <max>100.0</max>
      <resolution>0.01</resolution>
    </range>
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.01</stddev>
    </noise>
  </ray>
  <update_rate>10</update_rate>
  <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
    <ros>
      <remapping>~/out:=lidar/points</remapping>
    </ros>
    <output_type>sensor_msgs/PointCloud2</output_type>
    <frame_name>lidar_link</frame_name>
  </plugin>
</sensor>
```

## IMU Simulation

### 6-DOF IMU (Accelerometer + Gyroscope)

```xml
<!-- Gazebo IMU sensor -->
<sensor name="imu_sensor" type="imu">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0002</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0002</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0002</stddev>
        </noise>
      </z>
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </z>
    </linear_acceleration>
  </imu>
  <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
    <ros>
      <remapping>~/out:=imu/data</remapping>
    </ros>
  </plugin>
</sensor>
```

### IMU Data Processing

```python
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion
import numpy as np

class IMUProcessor(Node):
    def __init__(self):
        super().__init__('imu_processor')

        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        # Complementary filter for orientation
        self.alpha = 0.98
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0])

    def imu_callback(self, msg):
        # Extract data
        accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])

        gyro = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # Complementary filter
        self.orientation = self.complementary_filter(
            accel, gyro, self.orientation
        )

        # Detect falls
        if self.detect_fall(accel):
            self.get_logger().warn('Fall detected!')

    def detect_fall(self, accel):
        # Simple fall detection based on acceleration magnitude
        magnitude = np.linalg.norm(accel)
        return magnitude > 20.0  # m/s^2
```

## Force/Torque Sensors

### Contact Force Sensors

```xml
<!-- Gazebo contact sensor for foot -->
<sensor name="foot_contact" type="contact">
  <contact>
    <collision>foot_collision</collision>
  </contact>
  <update_rate>100</update_rate>
  <plugin name="contact_plugin" filename="libgazebo_ros_bumper.so">
    <ros>
      <remapping>bumper_states:=foot/contact</remapping>
    </ros>
  </plugin>
</sensor>
```

### Force/Torque Processing

```python
from geometry_msgs.msg import WrenchStamped

class ForceController(Node):
    def __init__(self):
        super().__init__('force_controller')

        self.force_sub = self.create_subscription(
            WrenchStamped,
            '/foot/force_torque',
            self.force_callback,
            10
        )

        self.cop_pub = self.create_publisher(
            PointStamped,
            '/center_of_pressure',
            10
        )

    def force_callback(self, msg):
        # Calculate center of pressure
        force_z = msg.wrench.force.z
        torque_x = msg.wrench.torque.x
        torque_y = msg.wrench.torque.y

        if force_z > 10.0:  # Minimum force threshold
            cop_x = -torque_y / force_z
            cop_y = torque_x / force_z

            self.publish_cop(cop_x, cop_y)
```

## Sensor Fusion

### Multi-Sensor Integration

```python
from sensor_fusion_py import ExtendedKalmanFilter

class SensorFusion(Node):
    def __init__(self):
        super().__init__('sensor_fusion')

        # Initialize EKF
        self.ekf = ExtendedKalmanFilter(state_dim=6)

        # Subscribe to multiple sensors
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )
        self.vision_sub = self.create_subscription(
            PoseStamped, '/vision/pose', self.vision_callback, 10
        )

        # Publish fused state
        self.state_pub = self.create_publisher(
            Odometry, '/fused_state', 10
        )

    def imu_callback(self, msg):
        # Update EKF with IMU measurement
        measurement = self.extract_imu_measurement(msg)
        self.ekf.update(measurement, sensor_type='imu')
        self.publish_fused_state()

    def odom_callback(self, msg):
        # Update EKF with odometry
        measurement = self.extract_odom_measurement(msg)
        self.ekf.update(measurement, sensor_type='odom')
        self.publish_fused_state()
```

## Sensor Noise Models

### Realistic Noise Simulation

```python
import numpy as np

class SensorNoiseModel:
    @staticmethod
    def add_gaussian_noise(data, mean=0.0, stddev=0.01):
        noise = np.random.normal(mean, stddev, data.shape)
        return data + noise

    @staticmethod
    def add_salt_pepper_noise(image, prob=0.01):
        noisy = image.copy()
        # Salt noise
        salt = np.random.random(image.shape) < prob/2
        noisy[salt] = 255
        # Pepper noise
        pepper = np.random.random(image.shape) < prob/2
        noisy[pepper] = 0
        return noisy

    @staticmethod
    def add_motion_blur(image, kernel_size=15):
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size-1)/2), :] = np.ones(kernel_size)
        kernel = kernel / kernel_size
        return cv2.filter2D(image, -1, kernel)
```

## Best Practices

1. **Match real sensor specifications** - Use accurate noise models
2. **Calibrate sensors** - Implement calibration procedures
3. **Handle sensor failures** - Test degraded sensor scenarios
4. **Synchronize timestamps** - Ensure proper time alignment
5. **Validate in simulation** - Compare with real sensor data

## Common Issues

- Sensor data latency causing control instability
- Incorrect noise models leading to unrealistic behavior
- Missing sensor calibration causing drift
- Synchronization issues between multiple sensors

## Next Steps

Explore NVIDIA Isaac Sim and Isaac ROS for advanced GPU-accelerated simulation and perception.
