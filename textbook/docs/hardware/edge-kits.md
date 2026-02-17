---
sidebar_position: 2
title: Edge Kits
description: Edge computing hardware for on-robot AI processing
keywords: [jetson, edge-computing, embedded, real-time]
---

# Edge Kits

## Overview

Edge computing kits enable real-time AI processing directly on the robot, reducing latency and enabling autonomous operation without cloud connectivity. This chapter covers NVIDIA Jetson platforms and complementary sensors.

## NVIDIA Jetson Orin Nano

### Specifications

**NVIDIA Jetson Orin Nano Developer Kit**

- **GPU**: 1024-core NVIDIA Ampere GPU with 32 Tensor Cores
- **CPU**: 6-core Arm Cortex-A78AE v8.2 64-bit
- **Memory**: 8GB 128-bit LPDDR5 (102.4 GB/s)
- **Storage**: microSD card slot (64GB+ recommended)
- **AI Performance**: 40 TOPS (INT8)
- **Power**: 7W - 15W configurable
- **Price**: ~$499

**Use Cases**:
- Real-time perception (object detection, segmentation)
- Visual SLAM and navigation
- Voice processing and NLU
- Motor control and sensor fusion

### Setup and Installation

```bash
# Flash JetPack 6.0 (includes Ubuntu 22.04, CUDA, cuDNN, TensorRT)
# Download from: https://developer.nvidia.com/embedded/jetpack

# Use NVIDIA SDK Manager or balenaEtcher
# 1. Download JetPack image
# 2. Flash to microSD card (64GB+ recommended)
# 3. Insert card and power on Jetson

# First boot setup
sudo apt update && sudo apt upgrade -y

# Install jtop for monitoring
sudo pip3 install jetson-stats
sudo reboot

# Monitor system
jtop
```

### Power Modes

```bash
# View available power modes
sudo nvpmodel -q

# Set to maximum performance (15W)
sudo nvpmodel -m 0

# Set to power-efficient mode (7W)
sudo nvpmodel -m 1

# Check current power consumption
sudo tegrastats
```

### ROS 2 on Jetson

```bash
# Install ROS 2 Humble
sudo apt install -y ros-humble-desktop

# Install Isaac ROS packages
sudo apt install -y \
    ros-humble-isaac-ros-base \
    ros-humble-isaac-ros-dnn-inference \
    ros-humble-isaac-ros-image-segmentation

# Build workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## Intel RealSense Cameras

### RealSense D435i

**Specifications**:
- **Depth Technology**: Active IR stereo
- **Depth Range**: 0.3m - 3m
- **RGB Resolution**: 1920x1080 @ 30fps
- **Depth Resolution**: 1280x720 @ 90fps
- **IMU**: 6-DOF (accelerometer + gyroscope)
- **Field of View**: 87° × 58° (depth), 69° × 42° (RGB)
- **Interface**: USB 3.1 Gen 1
- **Price**: ~$179

**Use Cases**:
- Visual odometry and SLAM
- Obstacle detection and avoidance
- Object recognition and grasping
- Human tracking and interaction

### Installation

```bash
# Install RealSense SDK
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main"
sudo apt update
sudo apt install -y librealsense2-dkms librealsense2-utils librealsense2-dev

# Test camera
realsense-viewer

# Install ROS 2 wrapper
sudo apt install -y ros-humble-realsense2-camera

# Launch camera
ros2 launch realsense2_camera rs_launch.py
```

### RealSense with Isaac ROS

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # RealSense camera
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            parameters=[{
                'enable_depth': True,
                'enable_color': True,
                'enable_infra1': True,
                'enable_infra2': True,
                'depth_module.profile': '640x480x30',
                'rgb_camera.profile': '640x480x30',
                'enable_gyro': True,
                'enable_accel': True,
                'unite_imu_method': 2
            }]
        ),

        # Isaac ROS Visual SLAM
        Node(
            package='isaac_ros_visual_slam',
            executable='isaac_ros_visual_slam',
            parameters=[{
                'enable_imu_fusion': True
            }],
            remappings=[
                ('stereo_camera/left/image', '/camera/infra1/image_rect_raw'),
                ('stereo_camera/right/image', '/camera/infra2/image_rect_raw'),
                ('visual_slam/imu', '/camera/imu')
            ]
        )
    ])
```

## Jetson + RealSense Integration

### Complete Edge System

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import torch

class EdgePerceptionSystem(Node):
    def __init__(self):
        super().__init__('edge_perception')

        self.bridge = CvBridge()

        # Load AI model (optimized for Jetson)
        self.model = torch.jit.load('model_jetson.pt')
        self.model.eval()

        # Subscribe to camera
        self.image_sub = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.image_callback,
            10
        )

        # Subscribe to IMU
        self.imu_sub = self.create_subscription(
            Imu,
            '/camera/imu',
            self.imu_callback,
            10
        )

        # Publish control commands
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.get_logger().info('Edge perception system initialized')

    def image_callback(self, msg):
        # Convert image
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # Run inference on Jetson GPU
        with torch.no_grad():
            prediction = self.model(self.preprocess(cv_image))

        # Process prediction and generate control
        cmd = self.generate_control(prediction)
        self.cmd_pub.publish(cmd)

    def imu_callback(self, msg):
        # Process IMU data for state estimation
        pass
```

## Performance Optimization

### TensorRT Optimization

```python
import tensorrt as trt

def optimize_for_jetson(onnx_path, engine_path):
    """Convert ONNX model to TensorRT for Jetson"""

    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    # Parse ONNX
    with open(onnx_path, 'rb') as model:
        parser.parse(model.read())

    # Configure for Jetson
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)

    # Enable FP16 for Jetson
    config.set_flag(trt.BuilderFlag.FP16)

    # Build engine
    engine = builder.build_serialized_network(network, config)

    # Save
    with open(engine_path, 'wb') as f:
        f.write(engine)

    print(f'TensorRT engine saved to {engine_path}')
```

### Memory Management

```python
import gc
import torch

class MemoryOptimizedNode(Node):
    def __init__(self):
        super().__init__('memory_optimized')

        # Use mixed precision
        self.scaler = torch.cuda.amp.GradScaler()

        # Clear cache periodically
        self.timer = self.create_timer(10.0, self.clear_cache)

    def clear_cache(self):
        gc.collect()
        torch.cuda.empty_cache()

        # Log memory usage
        allocated = torch.cuda.memory_allocated() / 1e9
        self.get_logger().info(f'GPU Memory: {allocated:.2f}GB')
```

## Networking and Connectivity

### WiFi Configuration

```bash
# Connect to WiFi
nmcli device wifi connect "SSID" password "PASSWORD"

# Set static IP
sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.1.100/24
sudo nmcli con mod "Wired connection 1" ipv4.gateway 192.168.1.1
sudo nmcli con mod "Wired connection 1" ipv4.dns "8.8.8.8"
sudo nmcli con mod "Wired connection 1" ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

### ROS 2 Multi-Machine Setup

```bash
# On Jetson (robot)
export ROS_DOMAIN_ID=42
export ROS_LOCALHOST_ONLY=0

# On workstation
export ROS_DOMAIN_ID=42
export ROS_LOCALHOST_ONLY=0

# Test communication
# On Jetson:
ros2 topic pub /test std_msgs/String "data: Hello from Jetson"

# On workstation:
ros2 topic echo /test
```

## Power Management

### Battery Monitoring

```python
class BatteryMonitor(Node):
    def __init__(self):
        super().__init__('battery_monitor')

        # Read battery status
        self.timer = self.create_timer(5.0, self.check_battery)

    def check_battery(self):
        # Read from battery management system
        voltage = self.read_battery_voltage()
        percentage = self.calculate_percentage(voltage)

        if percentage < 20:
            self.get_logger().warn(f'Low battery: {percentage}%')
            self.initiate_return_to_base()

    def read_battery_voltage(self):
        # Read from I2C battery monitor
        # Implementation depends on battery hardware
        pass
```

## Recommended Edge Kit Configurations

### Basic Edge Kit ($700-$900)

- NVIDIA Jetson Orin Nano Developer Kit ($499)
- Intel RealSense D435i ($179)
- 64GB microSD card ($20)
- USB WiFi adapter ($30)
- Power supply and cables ($50)

### Advanced Edge Kit ($1,200-$1,500)

- NVIDIA Jetson AGX Orin Developer Kit ($999)
- Intel RealSense D455 ($329)
- 2D LiDAR (RPLidar A1) ($99)
- 128GB NVMe SSD ($80)
- Industrial WiFi module ($100)

### Professional Edge Kit ($2,000-$3,000)

- NVIDIA Jetson AGX Orin 64GB ($1,999)
- Intel RealSense L515 ($949)
- 3D LiDAR (Ouster OS0) ($3,500)
- Industrial-grade storage ($200)
- Redundant power system ($300)

## Troubleshooting

### Jetson Won't Boot

```bash
# Check power supply (5V 4A minimum)
# Reflash JetPack using SDK Manager
# Check microSD card (use high-quality card)
```

### RealSense Not Detected

```bash
# Check USB connection
lsusb | grep Intel

# Reinstall drivers
sudo apt install --reinstall librealsense2-dkms

# Check permissions
sudo usermod -aG video $USER
```

### Performance Issues

```bash
# Enable maximum performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Monitor with jtop
jtop
```

## Next Steps

Learn about different robot hardware tiers and their capabilities.
