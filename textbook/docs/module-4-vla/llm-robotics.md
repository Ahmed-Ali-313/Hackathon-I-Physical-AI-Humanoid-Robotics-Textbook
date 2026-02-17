---
sidebar_position: 1
title: LLMs for Robotics
description: Integrating large language models with robotic systems
keywords: [llm, gpt, robotics, natural-language, ai]
---

# LLMs for Robotics

## Introduction

Large Language Models (LLMs) like GPT-4 enable robots to understand natural language commands, reason about tasks, and generate executable plans. This chapter explores how to integrate LLMs into robotic control systems.

## Why LLMs for Robotics?

**Key Benefits**:
- **Natural interaction**: Communicate with robots using everyday language
- **Task understanding**: Parse complex, ambiguous instructions
- **Common sense reasoning**: Leverage world knowledge for decision-making
- **Code generation**: Generate robot control code from descriptions
- **Adaptability**: Handle novel situations without retraining

## Architecture Overview

```
User Command → LLM → Task Plan → Motion Primitives → Robot Actions
     ↓          ↓         ↓              ↓              ↓
  "Pick up"  Parse   [grasp,      Joint         Execute
  "the cup"  Intent   move]      Trajectories   Motion
```

## OpenAI Integration

### Basic Setup

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from openai import OpenAI
import os

class LLMRobotController(Node):
    def __init__(self):
        super().__init__('llm_robot_controller')

        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Subscribe to voice/text commands
        self.command_sub = self.create_subscription(
            String,
            '/user_command',
            self.command_callback,
            10
        )

        # Publish robot actions
        self.action_pub = self.create_publisher(
            String,
            '/robot_actions',
            10
        )

        # System prompt for robot control
        self.system_prompt = """You are a humanoid robot controller.
        Convert natural language commands into structured robot actions.
        Available actions: grasp, release, move_to, rotate, walk, stop.
        Respond with JSON format: {"action": "...", "parameters": {...}}"""

    def command_callback(self, msg):
        user_command = msg.data
        self.get_logger().info(f'Received command: {user_command}')

        # Query LLM
        robot_action = self.query_llm(user_command)

        # Execute action
        self.execute_action(robot_action)

    def query_llm(self, command):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": command}
            ],
            temperature=0.3,
            max_tokens=200
        )

        return response.choices[0].message.content

    def execute_action(self, action_json):
        # Parse JSON and execute
        import json
        try:
            action = json.loads(action_json)
            self.get_logger().info(f'Executing: {action}')
            self.action_pub.publish(String(data=action_json))
        except json.JSONDecodeError:
            self.get_logger().error('Failed to parse LLM response')
```

## Prompt Engineering for Robotics

### Structured Prompts

```python
class RobotPromptBuilder:
    def __init__(self):
        self.base_prompt = """You are controlling a humanoid robot with the following capabilities:

**Available Actions:**
- grasp(object_name): Close gripper around object
- release(): Open gripper
- move_arm(x, y, z): Move end-effector to position
- walk_to(x, y): Navigate to location
- rotate(angle): Rotate base by angle
- look_at(object_name): Orient head toward object

**Current State:**
{state}

**Scene Description:**
{scene}

**Task:** {task}

Provide a step-by-step plan as a JSON array of actions."""

    def build_prompt(self, task, state, scene):
        return self.base_prompt.format(
            task=task,
            state=state,
            scene=scene
        )

# Usage
builder = RobotPromptBuilder()
prompt = builder.build_prompt(
    task="Pick up the red cup and place it on the table",
    state="Robot is standing, gripper is empty",
    scene="Red cup on floor, table 2m ahead"
)
```

### Few-Shot Learning

```python
def create_few_shot_prompt(task):
    examples = [
        {
            "command": "Pick up the ball",
            "plan": [
                {"action": "look_at", "params": {"object": "ball"}},
                {"action": "walk_to", "params": {"object": "ball"}},
                {"action": "grasp", "params": {"object": "ball"}}
            ]
        },
        {
            "command": "Go to the kitchen",
            "plan": [
                {"action": "walk_to", "params": {"location": "kitchen"}}
            ]
        }
    ]

    prompt = "Convert commands to robot action plans:\n\n"
    for ex in examples:
        prompt += f"Command: {ex['command']}\n"
        prompt += f"Plan: {json.dumps(ex['plan'])}\n\n"

    prompt += f"Command: {task}\nPlan:"
    return prompt
```

## Vision-Language Integration

### Combining Vision and Language

```python
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import base64

class VisionLanguageController(Node):
    def __init__(self):
        super().__init__('vision_language_controller')

        self.bridge = CvBridge()
        self.client = OpenAI()

        # Subscribe to camera
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.latest_image = None

    def image_callback(self, msg):
        self.latest_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

    def query_with_vision(self, command):
        if self.latest_image is None:
            return "No image available"

        # Encode image to base64
        _, buffer = cv2.imencode('.jpg', self.latest_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Query GPT-4 Vision
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You are a robot. {command}. What objects do you see and what should you do?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )

        return response.choices[0].message.content
```

## Code Generation

### LLM-Generated Robot Code

```python
class CodeGenerationController(Node):
    def __init__(self):
        super().__init__('code_generation_controller')

        self.client = OpenAI()

    def generate_robot_code(self, task_description):
        prompt = f"""Generate Python code for a ROS 2 robot to perform this task:
{task_description}

Use these imports:
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose
from std_msgs.msg import String

Create a complete ROS 2 node class."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert ROS 2 programmer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )

        code = response.choices[0].message.content

        # Extract code from markdown
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]

        return code

    def execute_generated_code(self, code):
        # CAUTION: Executing generated code is dangerous
        # In production, use sandboxing and validation
        try:
            exec(code, globals())
            self.get_logger().info('Code executed successfully')
        except Exception as e:
            self.get_logger().error(f'Code execution failed: {e}')
```

## Safety and Validation

### Action Validation

```python
class SafetyValidator:
    def __init__(self):
        self.safe_workspace = {
            'x_min': -1.0, 'x_max': 1.0,
            'y_min': -1.0, 'y_max': 1.0,
            'z_min': 0.0, 'z_max': 2.0
        }

        self.max_velocity = 0.5  # m/s
        self.max_force = 50.0    # N

    def validate_action(self, action):
        action_type = action.get('action')

        if action_type == 'move_arm':
            return self.validate_arm_motion(action['params'])
        elif action_type == 'walk_to':
            return self.validate_navigation(action['params'])
        elif action_type == 'grasp':
            return self.validate_grasp(action['params'])

        return True

    def validate_arm_motion(self, params):
        x, y, z = params['x'], params['y'], params['z']

        # Check workspace bounds
        if not (self.safe_workspace['x_min'] <= x <= self.safe_workspace['x_max']):
            return False
        if not (self.safe_workspace['y_min'] <= y <= self.safe_workspace['y_max']):
            return False
        if not (self.safe_workspace['z_min'] <= z <= self.safe_workspace['z_max']):
            return False

        return True

    def validate_navigation(self, params):
        # Check for obstacles, collision-free path
        # ...
        return True

    def validate_grasp(self, params):
        # Check if object is graspable
        # ...
        return True
```

## Practical Example: Kitchen Assistant Robot

```python
class KitchenAssistant(Node):
    def __init__(self):
        super().__init__('kitchen_assistant')

        self.client = OpenAI()
        self.validator = SafetyValidator()

        # Knowledge base
        self.object_locations = {
            'cup': 'cabinet_1',
            'plate': 'cabinet_2',
            'fork': 'drawer_1'
        }

    def handle_request(self, request):
        # Example: "Can you get me a cup?"

        # 1. Parse intent with LLM
        intent = self.parse_intent(request)

        # 2. Query knowledge base
        object_name = intent['object']
        location = self.object_locations.get(object_name)

        # 3. Generate plan
        plan = self.generate_plan(object_name, location)

        # 4. Validate plan
        if not self.validate_plan(plan):
            return "Cannot safely execute this task"

        # 5. Execute plan
        self.execute_plan(plan)

        return f"Retrieved {object_name} from {location}"

    def parse_intent(self, request):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract intent from user request. Return JSON with 'action' and 'object' fields."},
                {"role": "user", "content": request}
            ]
        )

        return json.loads(response.choices[0].message.content)
```

## Best Practices

1. **Validate all LLM outputs** - Never execute without safety checks
2. **Use structured outputs** - Request JSON for easier parsing
3. **Implement timeouts** - Handle API failures gracefully
4. **Cache common queries** - Reduce API costs and latency
5. **Monitor token usage** - Track costs and optimize prompts
6. **Test edge cases** - Handle ambiguous or impossible commands

## Common Issues

- LLM hallucinations generating invalid actions
- API rate limits during high-frequency control
- Latency affecting real-time responsiveness
- Cost accumulation with frequent queries
- Inconsistent outputs requiring retry logic

## Next Steps

Learn how to implement voice-to-action pipelines for hands-free robot control.
