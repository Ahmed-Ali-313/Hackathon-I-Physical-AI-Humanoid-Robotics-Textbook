# 📚 Hackathon Project Specifications

## 1. What to Build (Deliverables)

To fulfill the project requirements, you must create and deploy the following:

- **AI-Native Technical Textbook**: A digital book created using Docusaurus that teaches the "Physical AI & Humanoid Robotics" course.
  +1

- **Integrated RAG Chatbot**: A chatbot embedded within the book that uses Retrieval-Augmented Generation to answer questions based on the book's content.

- **Authentication System (Bonus)**: A sign-up/sign-in system that collects user hardware and software backgrounds to enable content personalization.

- **Personalization & Translation Features (Bonus)**: Interactive buttons at the start of each chapter to personalize content or translate it into Urdu.

- **Demo Video**: A walkthrough of your project no longer than 90 seconds.

## 2. Tech Stack

You are required to use specific tools and platforms for development:

### Book Authoring & Deployment

- **Claude Code**: Used for writing and coding the project.
  +1

- **Spec-Kit Plus**: The framework for AI-driven book creation.
  +1

- **Docusaurus**: The documentation platform for the book.
  +1

- **GitHub Pages / Vercel**: For public deployment of the book and chatbot.
  +1

### AI & Backend (The RAG Chatbot)

- **OpenAI Agents / ChatKit SDKs**: For building the core agentic capabilities.

- **FastAPI**: To handle the backend API services.

- **Neon Serverless Postgres**: To store structured data.

- **Qdrant Cloud (Free Tier)**: As the vector database for content retrieval.

- **Claude Code Subagents & Agent Skills**: For advanced reusable intelligence (bonus).

### User Management

- **Better-Auth**: For implementing the secure login and user profiling system.

## 3. Book Content & Topics

The textbook must cover the following specific modules and weekly breakdown for the "Physical AI & Humanoid Robotics" course:

### Module 1: The Robotic Nervous System (ROS 2)

- Middleware for robot control.
- ROS 2 Nodes, Topics, and Services.
- Bridging Python Agents to ROS controllers using rclpy.
- Understanding URDF (Unified Robot Description Format) for humanoids.

### Module 2: The Digital Twin (Gazebo & Unity)

- Physics simulation, gravity, and collisions in Gazebo.
- High-fidelity rendering and human-robot interaction in Unity.
- Simulating sensors: LiDAR, Depth Cameras, and IMUs.

### Module 3: The AI-Robot Brain (NVIDIA Isaac™)

- NVIDIA Isaac Sim: Photorealistic simulation and synthetic data generation.
- Isaac ROS: Hardware-accelerated VSLAM (Visual SLAM) and navigation.
- Nav2: Path planning for bipedal humanoid movement.

### Module 4: Vision-Language-Action (VLA)

- The convergence of LLMs and Robotics.
- Voice-to-Action: Using OpenAI Whisper for voice commands.
- Cognitive Planning: Translating natural language into ROS 2 action sequences.
- Capstone Project: Building an autonomous humanoid that navigates and manipulates objects.

## Hardware Specifics (Required Knowledge Chapters)

You should also include chapters or sections explaining the necessary hardware infrastructure:

- **Workstations**: Requirements for NVIDIA RTX GPUs (minimum 12GB VRAM) and Ubuntu 22.04 LTS.
  +1

- **Edge Kits**: Usage of NVIDIA Jetson Orin Nano and Intel RealSense cameras.
  +1

- **Robot Tiers**: Comparing quadruped proxies (Unitree Go2) vs. full humanoids (Unitree G1).
  +2
