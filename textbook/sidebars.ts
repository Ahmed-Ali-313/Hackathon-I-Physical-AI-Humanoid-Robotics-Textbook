import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      collapsed: false,
      items: [
        'module-1-ros2/middleware',
        'module-1-ros2/nodes-topics-services',
        'module-1-ros2/python-ros-bridging',
        'module-1-ros2/urdf-humanoids',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      collapsed: false,
      items: [
        'module-2-digital-twin/physics-simulation',
        'module-2-digital-twin/rendering-interaction',
        'module-2-digital-twin/sensor-simulation',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
      collapsed: false,
      items: [
        'module-3-isaac/isaac-sim',
        'module-3-isaac/isaac-ros',
        'module-3-isaac/nav2-planning',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      collapsed: false,
      items: [
        'module-4-vla/llm-robotics',
        'module-4-vla/voice-to-action',
        'module-4-vla/cognitive-planning',
        'module-4-vla/capstone-project',
      ],
    },
    {
      type: 'category',
      label: 'Hardware Requirements',
      collapsed: false,
      items: [
        'hardware/workstations',
        'hardware/edge-kits',
        'hardware/robot-tiers',
      ],
    },
  ],
};

export default sidebars;
