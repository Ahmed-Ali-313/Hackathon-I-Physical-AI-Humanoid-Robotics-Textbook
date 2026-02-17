---
sidebar_position: 4
title: URDF for Humanoid Robots
description: Modeling humanoid robot kinematics and dynamics using URDF
keywords: [urdf, humanoid, kinematics, robot-model]
---

# URDF for Humanoid Robots

## Introduction

The Unified Robot Description Format (URDF) is the standard way to describe robot geometry, kinematics, and dynamics in ROS 2. For humanoid robots, URDF models capture the complex kinematic chains and joint configurations.

## URDF Basics

A URDF file is an XML document that defines:
- **Links**: Rigid body segments (torso, limbs, head)
- **Joints**: Connections between links (revolute, prismatic, fixed)
- **Visual/Collision geometry**: 3D meshes and collision shapes
- **Inertial properties**: Mass, center of mass, inertia tensors

## Humanoid Robot Structure

```xml
<?xml version="1.0"?>
<robot name="humanoid_g1">

  <!-- Base Link (Torso) -->
  <link name="torso">
    <visual>
      <geometry>
        <mesh filename="package://humanoid_description/meshes/torso.stl"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>

    <inertial>
      <mass value="15.0"/>
      <inertia ixx="0.5" ixy="0.0" ixz="0.0"
               iyy="0.5" iyz="0.0" izz="0.3"/>
    </inertial>
  </link>

  <!-- Hip Joint (Right Leg) -->
  <joint name="right_hip_pitch" type="revolute">
    <parent link="torso"/>
    <child link="right_thigh"/>
    <origin xyz="0.0 -0.1 -0.2" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="2.0"/>
  </joint>

  <!-- Thigh Link -->
  <link name="right_thigh">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.4"/>
      </geometry>
    </visual>
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.04" ixy="0.0" ixz="0.0"
               iyy="0.04" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

</robot>
```

## Kinematic Chains

Humanoid robots have multiple kinematic chains:

1. **Legs**: Torso → Hip → Thigh → Knee → Ankle → Foot
2. **Arms**: Torso → Shoulder → Upper Arm → Elbow → Forearm → Wrist → Hand
3. **Head**: Torso → Neck → Head

```python
# Example: Loading URDF in ROS 2
from ament_index_python.packages import get_package_share_directory
import os

def load_urdf():
    pkg_path = get_package_share_directory('humanoid_description')
    urdf_path = os.path.join(pkg_path, 'urdf', 'humanoid.urdf')

    with open(urdf_path, 'r') as file:
        robot_description = file.read()

    return robot_description
```

## Joint Types for Humanoids

### Revolute Joints (Most Common)

```xml
<joint name="knee_joint" type="revolute">
  <axis xyz="0 1 0"/>  <!-- Rotation around Y-axis -->
  <limit lower="0.0" upper="2.35" effort="150" velocity="3.0"/>
</joint>
```

### Continuous Joints (Rare)

```xml
<joint name="wrist_roll" type="continuous">
  <axis xyz="1 0 0"/>  <!-- Unlimited rotation -->
</joint>
```

## Inertial Properties

Accurate inertial properties are critical for simulation and control:

```xml
<inertial>
  <origin xyz="0 0 0.2" rpy="0 0 0"/>  <!-- Center of mass -->
  <mass value="5.0"/>
  <inertia ixx="0.1" ixy="0.0" ixz="0.0"
           iyy="0.1" iyz="0.0" izz="0.05"/>
</inertial>
```

## Xacro: Parameterized URDF

Xacro extends URDF with macros and parameters for reusable components:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid">

  <!-- Parameters -->
  <xacro:property name="leg_length" value="0.8"/>
  <xacro:property name="leg_mass" value="5.0"/>

  <!-- Macro for leg -->
  <xacro:macro name="leg" params="prefix reflect">
    <link name="${prefix}_thigh">
      <visual>
        <geometry>
          <cylinder radius="0.05" length="${leg_length}"/>
        </geometry>
      </visual>
      <inertial>
        <mass value="${leg_mass}"/>
      </inertial>
    </link>

    <joint name="${prefix}_hip" type="revolute">
      <parent link="torso"/>
      <child link="${prefix}_thigh"/>
      <origin xyz="0 ${reflect*0.1} 0"/>
    </joint>
  </xacro:macro>

  <!-- Instantiate both legs -->
  <xacro:leg prefix="left" reflect="1"/>
  <xacro:leg prefix="right" reflect="-1"/>

</robot>
```

## Visualization and Debugging

```bash
# Check URDF syntax
check_urdf humanoid.urdf

# Visualize in RViz
ros2 launch humanoid_description display.launch.py

# Convert Xacro to URDF
xacro humanoid.urdf.xacro > humanoid.urdf
```

## Integration with Simulation

URDF models are used by:
- **Gazebo**: Physics simulation
- **Isaac Sim**: NVIDIA's simulation platform
- **MoveIt**: Motion planning
- **RViz**: Visualization

## Best Practices

1. **Use realistic inertial properties** - Measure or estimate accurately
2. **Simplify collision geometry** - Use primitive shapes for performance
3. **Organize with Xacro** - Modularize complex robots
4. **Test in simulation first** - Validate before hardware deployment
5. **Version control URDF files** - Track changes carefully

## Common Issues

- Incorrect joint axes causing inverted motion
- Missing collision geometry leading to simulation artifacts
- Unrealistic inertial properties causing instability
- Mesh file paths not resolving correctly

## Next Steps

Now that you understand ROS 2 fundamentals, let's explore digital twin simulation with Gazebo and Unity.
