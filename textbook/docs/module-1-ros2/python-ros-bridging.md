---
sidebar_position: 3
title: Python-ROS 2 Bridging
description: Integrating AI models and Python applications with ROS 2 systems
keywords: [ros2, python, ai, integration, rclpy]
---

# Python-ROS 2 Bridging

## Overview

Modern robotics requires seamless integration between ROS 2 control systems and Python-based AI frameworks (PyTorch, TensorFlow, OpenAI). This chapter covers best practices for bridging these ecosystems.

## Why Python for Robotics AI?

Python dominates the AI/ML landscape with:
- Rich ecosystem (NumPy, PyTorch, TensorFlow, OpenCV)
- Rapid prototyping capabilities
- Extensive pre-trained models
- Active research community

## Basic ROS 2 Python Node

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import torch
import numpy as np

class VisionProcessor(Node):
    def __init__(self):
        super().__init__('vision_processor')

        # Initialize CV Bridge for image conversion
        self.bridge = CvBridge()

        # Load AI model
        self.model = torch.load('humanoid_vision_model.pth')
        self.model.eval()

        # Subscribe to camera feed
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.get_logger().info('Vision processor initialized')

    def image_callback(self, msg):
        # Convert ROS Image to OpenCV format
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # Preprocess for model
        tensor_image = self.preprocess(cv_image)

        # Run inference
        with torch.no_grad():
            prediction = self.model(tensor_image)

        # Process results
        self.handle_prediction(prediction)
```

## Integrating OpenAI APIs

```python
from openai import OpenAI
from std_msgs.msg import String

class LanguageCommandNode(Node):
    def __init__(self):
        super().__init__('language_command')

        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Subscribe to voice commands
        self.voice_sub = self.create_subscription(
            String,
            'voice_input',
            self.voice_callback,
            10
        )

        # Publish robot actions
        self.action_pub = self.create_publisher(
            String,
            'robot_actions',
            10
        )

    def voice_callback(self, msg):
        # Convert natural language to robot action
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Convert human commands to robot actions"},
                {"role": "user", "content": msg.data}
            ]
        )

        action = response.choices[0].message.content
        self.action_pub.publish(String(data=action))
```

## Performance Considerations

### 1. Threading and Async Operations

```python
import threading
from rclpy.executors import MultiThreadedExecutor

class AsyncAINode(Node):
    def __init__(self):
        super().__init__('async_ai_node')

        # Use threading for heavy AI computations
        self.inference_thread = threading.Thread(
            target=self.inference_loop,
            daemon=True
        )
        self.inference_thread.start()

    def inference_loop(self):
        while rclpy.ok():
            # Run AI inference without blocking ROS callbacks
            self.process_ai_task()
```

### 2. Message Conversion Efficiency

```python
# Efficient image conversion
def convert_image_efficiently(self, ros_image):
    # Use zero-copy when possible
    np_array = np.frombuffer(ros_image.data, dtype=np.uint8)
    np_array = np_array.reshape((ros_image.height, ros_image.width, 3))
    return np_array
```

## Real-World Example: Vision-Language-Action Pipeline

```python
class VLAController(Node):
    def __init__(self):
        super().__init__('vla_controller')

        # Vision: Process camera input
        self.vision_model = load_vision_model()

        # Language: Understand commands
        self.language_model = OpenAI()

        # Action: Control robot
        self.action_pub = self.create_publisher(
            JointTrajectory,
            'joint_commands',
            10
        )

        # Subscribe to camera and voice
        self.setup_subscriptions()

    def process_vla_pipeline(self, image, command):
        # 1. Vision: Extract scene features
        scene_features = self.vision_model(image)

        # 2. Language: Parse command with context
        action_plan = self.language_model.parse(
            command,
            context=scene_features
        )

        # 3. Action: Execute robot motion
        trajectory = self.plan_trajectory(action_plan)
        self.action_pub.publish(trajectory)
```

## Best Practices

1. **Separate AI inference from ROS callbacks** - Use threading or async
2. **Handle model loading efficiently** - Load once at initialization
3. **Manage dependencies carefully** - Use virtual environments
4. **Monitor performance** - Track inference latency and throughput
5. **Implement fallbacks** - Handle API failures gracefully

## Common Pitfalls

- Blocking ROS callbacks with slow AI inference
- Memory leaks from improper tensor management
- Network timeouts with external APIs
- Version conflicts between ROS and Python packages

## Next Steps

Learn how to model humanoid robots using URDF for simulation and control.
