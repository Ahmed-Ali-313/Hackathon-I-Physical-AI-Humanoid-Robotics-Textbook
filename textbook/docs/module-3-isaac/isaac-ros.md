---
sidebar_position: 2
title: Isaac ROS - Hardware-Accelerated Perception
description: Deploy GPU-accelerated perception pipelines with Isaac ROS
keywords: [isaac-ros, perception, gpu, jetson, real-time]
---

# Isaac ROS - Hardware-Accelerated Perception

## Introduction

Isaac ROS provides GPU-accelerated ROS 2 packages for perception, enabling real-time performance on NVIDIA Jetson and desktop GPUs. These packages leverage CUDA, TensorRT, and hardware encoders for maximum efficiency.

## Architecture Overview

Isaac ROS packages run perception algorithms on GPU while maintaining ROS 2 compatibility:

```
Camera → Isaac ROS DNN → Isaac ROS Segmentation → ROS 2 Topics
  ↓           ↓                    ↓
 GPU        GPU                  GPU
```

## Installation

### On NVIDIA Jetson

```bash
# Install Isaac ROS on Jetson Orin
sudo apt-get update
sudo apt-get install -y ros-humble-isaac-ros-base

# Install specific packages
sudo apt-get install -y \
    ros-humble-isaac-ros-dnn-inference \
    ros-humble-isaac-ros-image-segmentation \
    ros-humble-isaac-ros-object-detection \
    ros-humble-isaac-ros-pose-estimation
```

### Docker Setup (Recommended)

```bash
# Clone Isaac ROS common
cd ~/workspaces
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# Build Docker image
cd isaac_ros_common
./scripts/run_dev.sh

# Inside container, build workspace
cd /workspaces/isaac_ros-dev
colcon build --symlink-install
source install/setup.bash
```

## DNN Inference

### Object Detection with DOPE

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection3DArray

class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection')

        # Subscribe to camera
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Subscribe to detections from Isaac ROS DOPE
        self.detection_sub = self.create_subscription(
            Detection3DArray,
            '/dope/detections',
            self.detection_callback,
            10
        )

    def detection_callback(self, msg):
        for detection in msg.detections:
            # Extract 6D pose
            pose = detection.results[0].pose.pose
            position = pose.position
            orientation = pose.orientation

            self.get_logger().info(
                f'Detected object at ({position.x:.2f}, '
                f'{position.y:.2f}, {position.z:.2f})'
            )
```

### Launch File Configuration

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Camera driver
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            parameters=[{
                'depth_module.profile': '640x480x30',
                'rgb_camera.profile': '640x480x30'
            }]
        ),

        # Isaac ROS DNN Image Encoder
        Node(
            package='isaac_ros_dnn_image_encoder',
            executable='dnn_image_encoder',
            parameters=[{
                'network_image_width': 640,
                'network_image_height': 480,
                'image_mean': [0.485, 0.456, 0.406],
                'image_stddev': [0.229, 0.224, 0.225]
            }],
            remappings=[
                ('image', '/camera/color/image_raw'),
                ('camera_info', '/camera/color/camera_info')
            ]
        ),

        # Isaac ROS TensorRT
        Node(
            package='isaac_ros_tensor_rt',
            executable='isaac_ros_tensor_rt',
            parameters=[{
                'model_file_path': '/models/dope_model.onnx',
                'engine_file_path': '/models/dope_model.plan',
                'input_tensor_names': ['input'],
                'output_tensor_names': ['output'],
                'input_binding_names': ['input'],
                'output_binding_names': ['output']
            }]
        ),

        # DOPE Decoder
        Node(
            package='isaac_ros_dope',
            executable='dope_decoder',
            parameters=[{
                'object_name': 'soup_can'
            }]
        )
    ])
```

## Semantic Segmentation

### U-Net Segmentation Pipeline

```python
from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    container = ComposableNodeContainer(
        name='segmentation_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            # Image rectification
            ComposableNode(
                package='isaac_ros_image_proc',
                plugin='nvidia::isaac_ros::image_proc::RectifyNode',
                name='rectify_node',
                remappings=[
                    ('image_raw', '/camera/image_raw'),
                    ('camera_info', '/camera/camera_info')
                ]
            ),

            # DNN encoder
            ComposableNode(
                package='isaac_ros_dnn_image_encoder',
                plugin='nvidia::isaac_ros::dnn_inference::DnnImageEncoderNode',
                name='encoder_node',
                parameters=[{
                    'network_image_width': 960,
                    'network_image_height': 544
                }]
            ),

            # TensorRT inference
            ComposableNode(
                package='isaac_ros_tensor_rt',
                plugin='nvidia::isaac_ros::dnn_inference::TensorRTNode',
                name='tensorrt_node',
                parameters=[{
                    'model_file_path': '/models/unet_model.onnx',
                    'engine_file_path': '/models/unet_model.plan'
                }]
            ),

            # U-Net decoder
            ComposableNode(
                package='isaac_ros_unet',
                plugin='nvidia::isaac_ros::unet::UNetDecoderNode',
                name='unet_decoder',
                parameters=[{
                    'network_output_type': 'softmax'
                }]
            )
        ],
        output='screen'
    )

    return LaunchDescription([container])
```

## Visual SLAM

### Isaac ROS Visual SLAM

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
                'enable_infra1': True,
                'enable_infra2': True,
                'depth_module.profile': '640x480x30',
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
                'denoise_input_images': True,
                'rectified_images': False,
                'enable_imu_fusion': True,
                'gyro_noise_density': 0.000244,
                'gyro_random_walk': 0.000019393,
                'accel_noise_density': 0.001862,
                'accel_random_walk': 0.003,
                'calibration_frequency': 200.0,
                'img_jitter_threshold_ms': 22.00
            }],
            remappings=[
                ('stereo_camera/left/image', '/camera/infra1/image_rect_raw'),
                ('stereo_camera/left/camera_info', '/camera/infra1/camera_info'),
                ('stereo_camera/right/image', '/camera/infra2/image_rect_raw'),
                ('stereo_camera/right/camera_info', '/camera/infra2/camera_info'),
                ('visual_slam/imu', '/camera/imu')
            ]
        )
    ])
```

## AprilTag Detection

### Hardware-Accelerated Fiducial Detection

```python
class AprilTagTracker(Node):
    def __init__(self):
        super().__init__('apriltag_tracker')

        # Subscribe to AprilTag detections
        self.tag_sub = self.create_subscription(
            AprilTagDetectionArray,
            '/tag_detections',
            self.tag_callback,
            10
        )

        # Publish robot commands based on tags
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

    def tag_callback(self, msg):
        if len(msg.detections) == 0:
            return

        # Track first detected tag
        tag = msg.detections[0]
        tag_id = tag.id[0]
        pose = tag.pose.pose.pose

        # Calculate control command
        cmd = self.compute_tracking_command(pose)
        self.cmd_pub.publish(cmd)

    def compute_tracking_command(self, pose):
        cmd = Twist()

        # Simple proportional controller
        Kp_linear = 0.5
        Kp_angular = 1.0

        # Move toward tag
        cmd.linear.x = Kp_linear * pose.position.z
        cmd.angular.z = Kp_angular * (-pose.position.x)

        return cmd
```

## Performance Monitoring

### Measuring Inference Latency

```python
import time
from rclpy.qos import QoSProfile, ReliabilityPolicy

class PerformanceMonitor(Node):
    def __init__(self):
        super().__init__('performance_monitor')

        self.latencies = []

        # Subscribe with timestamp tracking
        qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            qos
        )

        self.detection_sub = self.create_subscription(
            Detection3DArray,
            '/detections',
            self.detection_callback,
            qos
        )

        self.image_timestamps = {}

    def image_callback(self, msg):
        # Store timestamp
        self.image_timestamps[msg.header.stamp] = time.time()

    def detection_callback(self, msg):
        # Calculate latency
        if msg.header.stamp in self.image_timestamps:
            latency = time.time() - self.image_timestamps[msg.header.stamp]
            self.latencies.append(latency * 1000)  # Convert to ms

            if len(self.latencies) >= 100:
                avg_latency = sum(self.latencies) / len(self.latencies)
                self.get_logger().info(
                    f'Average latency: {avg_latency:.2f}ms'
                )
                self.latencies = []
```

## Model Optimization with TensorRT

### Converting ONNX to TensorRT

```python
import tensorrt as trt

def convert_onnx_to_tensorrt(onnx_path, engine_path):
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    # Parse ONNX model
    with open(onnx_path, 'rb') as model:
        if not parser.parse(model.read()):
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            return False

    # Configure builder
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB

    # Enable FP16 precision
    if builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)

    # Build engine
    engine = builder.build_serialized_network(network, config)

    # Save engine
    with open(engine_path, 'wb') as f:
        f.write(engine)

    return True
```

## Best Practices

1. **Use composable nodes** - Reduce overhead with intra-process communication
2. **Enable zero-copy** - Use shared memory for large messages
3. **Optimize models** - Convert to TensorRT with FP16 precision
4. **Monitor GPU utilization** - Use `tegrastats` on Jetson
5. **Batch processing** - Process multiple images together when possible

## Common Issues

- TensorRT engine build failures due to unsupported operations
- Memory exhaustion on Jetson with large models
- Camera synchronization issues with IMU
- QoS mismatch between publishers and subscribers

## Next Steps

Learn how to implement navigation and path planning with Nav2 and Isaac ROS.
