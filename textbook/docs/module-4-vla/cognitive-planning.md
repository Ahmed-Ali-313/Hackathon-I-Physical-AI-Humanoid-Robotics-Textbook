---
sidebar_position: 3
title: Cognitive Planning with LLMs
description: Multi-step task planning and reasoning for autonomous robots
keywords: [planning, reasoning, llm, task-decomposition, cognitive]
---

# Cognitive Planning with LLMs

## Introduction

Cognitive planning enables robots to break down complex, high-level goals into executable action sequences. By leveraging LLMs for reasoning and planning, robots can handle novel situations and adapt to changing environments.

## Planning Architecture

```
High-Level Goal → Task Decomposition → Action Sequencing → Execution Monitoring
       ↓                  ↓                    ↓                    ↓
"Clean the room"    [pick_up_items,      [grasp, move,        Execute &
                     vacuum_floor]        release, ...]        Replan
```

## Hierarchical Task Planning

### Task Decomposition with LLMs

```python
import rclpy
from rclpy.node import Node
from openai import OpenAI
import json

class CognitivePlanner(Node):
    def __init__(self):
        super().__init__('cognitive_planner')

        self.client = OpenAI()

        # Task hierarchy
        self.task_hierarchy = []

    def plan_task(self, high_level_goal, context):
        """Decompose high-level goal into subtasks"""

        prompt = f"""You are a humanoid robot planner. Break down this goal into subtasks:

Goal: {high_level_goal}

Context:
- Current location: {context['location']}
- Available objects: {context['objects']}
- Robot capabilities: {context['capabilities']}

Provide a hierarchical plan as JSON:
{{
    "goal": "...",
    "subtasks": [
        {{
            "task": "...",
            "preconditions": [...],
            "actions": [...],
            "expected_outcome": "..."
        }}
    ]
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert robot task planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        plan = json.loads(response.choices[0].message.content)
        return plan

    def execute_plan(self, plan):
        """Execute plan with monitoring and replanning"""

        for subtask in plan['subtasks']:
            self.get_logger().info(f"Executing subtask: {subtask['task']}")

            # Check preconditions
            if not self.check_preconditions(subtask['preconditions']):
                self.get_logger().warn('Preconditions not met, replanning...')
                self.replan(subtask)
                continue

            # Execute actions
            success = self.execute_actions(subtask['actions'])

            if not success:
                self.get_logger().error('Action failed, replanning...')
                self.replan(subtask)
                continue

            # Verify outcome
            if not self.verify_outcome(subtask['expected_outcome']):
                self.get_logger().warn('Outcome not achieved, replanning...')
                self.replan(subtask)

    def check_preconditions(self, preconditions):
        """Verify all preconditions are satisfied"""
        for condition in preconditions:
            if not self.evaluate_condition(condition):
                return False
        return True

    def execute_actions(self, actions):
        """Execute sequence of actions"""
        for action in actions:
            if not self.execute_single_action(action):
                return False
        return True
```

## Reasoning and Common Sense

### LLM-Based Reasoning

```python
class ReasoningEngine(Node):
    def __init__(self):
        super().__init__('reasoning_engine')

        self.client = OpenAI()

    def reason_about_situation(self, situation, question):
        """Use LLM for common sense reasoning"""

        prompt = f"""Situation: {situation}

Question: {question}

Provide reasoning and answer in JSON:
{{
    "reasoning": "step-by-step thought process",
    "answer": "final answer",
    "confidence": 0.0-1.0
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a robot reasoning about physical situations."},
                {"role": "user", "content": prompt}
            ]
        )

        return json.loads(response.choices[0].message.content)

    def handle_unexpected_situation(self, observation):
        """Reason about unexpected observations"""

        reasoning = self.reason_about_situation(
            situation=observation,
            question="What should the robot do in this situation?"
        )

        self.get_logger().info(f"Reasoning: {reasoning['reasoning']}")
        self.get_logger().info(f"Decision: {reasoning['answer']}")

        return reasoning['answer']
```

## Chain-of-Thought Planning

### Step-by-Step Reasoning

```python
class ChainOfThoughtPlanner(Node):
    def __init__(self):
        super().__init__('cot_planner')

        self.client = OpenAI()

    def plan_with_cot(self, goal):
        """Plan using chain-of-thought prompting"""

        prompt = f"""Goal: {goal}

Think step-by-step about how to achieve this goal:

1. What is the current state?
2. What needs to change?
3. What actions are required?
4. What could go wrong?
5. How to handle failures?

Provide detailed reasoning, then a final plan."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Think carefully and reason step-by-step."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        reasoning = response.choices[0].message.content

        # Extract plan from reasoning
        plan = self.extract_plan_from_reasoning(reasoning)

        return plan, reasoning

    def extract_plan_from_reasoning(self, reasoning):
        """Extract structured plan from reasoning text"""

        prompt = f"""Extract a structured plan from this reasoning:

{reasoning}

Return JSON with actions list."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        return json.loads(response.choices[0].message.content)
```

## Reactive Replanning

### Dynamic Plan Adjustment

```python
class ReactivePlanner(Node):
    def __init__(self):
        super().__init__('reactive_planner')

        self.client = OpenAI()
        self.current_plan = None
        self.execution_history = []

    def monitor_and_replan(self):
        """Monitor execution and replan if needed"""

        # Get current state
        current_state = self.get_robot_state()

        # Check if plan is still valid
        if not self.is_plan_valid(self.current_plan, current_state):
            self.get_logger().warn('Plan invalid, replanning...')
            self.replan(current_state)

    def replan(self, current_state):
        """Generate new plan based on current state"""

        prompt = f"""The robot's plan failed. Current state:
{json.dumps(current_state, indent=2)}

Execution history:
{json.dumps(self.execution_history[-5:], indent=2)}

Generate a new plan that:
1. Accounts for the current state
2. Avoids previous failures
3. Achieves the original goal

Return JSON plan."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an adaptive robot planner."},
                {"role": "user", "content": prompt}
            ]
        )

        new_plan = json.loads(response.choices[0].message.content)
        self.current_plan = new_plan

        return new_plan

    def is_plan_valid(self, plan, state):
        """Check if plan is still executable"""

        # Check preconditions
        for action in plan['actions']:
            if not self.can_execute(action, state):
                return False

        return True
```

## Multi-Agent Coordination

### Collaborative Planning

```python
class MultiAgentPlanner(Node):
    def __init__(self):
        super().__init__('multi_agent_planner')

        self.client = OpenAI()
        self.agents = ['robot_1', 'robot_2']

    def plan_collaborative_task(self, task, agents):
        """Plan task requiring multiple robots"""

        prompt = f"""Plan a collaborative task for multiple robots:

Task: {task}
Agents: {agents}

Each agent has capabilities:
- Navigation
- Manipulation
- Perception

Assign subtasks to agents and coordinate timing.

Return JSON:
{{
    "agent_tasks": {{
        "robot_1": [...],
        "robot_2": [...]
    }},
    "synchronization_points": [...]
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        plan = json.loads(response.choices[0].message.content)

        return plan

    def coordinate_execution(self, plan):
        """Execute coordinated plan"""

        # Distribute tasks to agents
        for agent, tasks in plan['agent_tasks'].items():
            self.send_tasks_to_agent(agent, tasks)

        # Monitor synchronization points
        for sync_point in plan['synchronization_points']:
            self.wait_for_synchronization(sync_point)
```

## Learning from Experience

### Experience-Based Planning

```python
class ExperiencePlanner(Node):
    def __init__(self):
        super().__init__('experience_planner')

        self.client = OpenAI()
        self.experience_db = []

    def plan_with_experience(self, goal):
        """Plan using past experiences"""

        # Retrieve similar past experiences
        similar_experiences = self.retrieve_similar_experiences(goal)

        prompt = f"""Goal: {goal}

Past similar experiences:
{json.dumps(similar_experiences, indent=2)}

Learn from these experiences and create an improved plan.
What worked? What failed? How to avoid past mistakes?

Return JSON plan with lessons learned."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        plan = json.loads(response.choices[0].message.content)

        return plan

    def record_experience(self, goal, plan, outcome):
        """Store experience for future learning"""

        experience = {
            'goal': goal,
            'plan': plan,
            'outcome': outcome,
            'success': outcome['success'],
            'timestamp': self.get_clock().now().to_msg()
        }

        self.experience_db.append(experience)

        # Analyze what went wrong/right
        analysis = self.analyze_experience(experience)
        experience['analysis'] = analysis

    def retrieve_similar_experiences(self, goal):
        """Find relevant past experiences"""

        # Use LLM for semantic similarity
        prompt = f"""Find experiences similar to this goal:
{goal}

Experiences:
{json.dumps(self.experience_db, indent=2)}

Return indices of most similar experiences."""

        # ... implementation
```

## Practical Example: Kitchen Cleaning Task

```python
class KitchenCleaningPlanner(Node):
    def __init__(self):
        super().__init__('kitchen_cleaning_planner')

        self.planner = CognitivePlanner()
        self.reasoner = ReasoningEngine()

    def clean_kitchen(self):
        """High-level kitchen cleaning task"""

        # Get current state
        context = {
            'location': 'kitchen_entrance',
            'objects': ['dirty_dishes', 'trash', 'spills'],
            'capabilities': ['grasp', 'navigate', 'wipe']
        }

        # Plan task
        plan = self.planner.plan_task(
            high_level_goal="Clean the kitchen",
            context=context
        )

        self.get_logger().info(f"Generated plan: {json.dumps(plan, indent=2)}")

        # Execute with monitoring
        self.planner.execute_plan(plan)

    def handle_obstacle(self, obstacle):
        """Reason about unexpected obstacles"""

        reasoning = self.reasoner.reason_about_situation(
            situation=f"Encountered {obstacle} while cleaning",
            question="How should I proceed?"
        )

        if reasoning['confidence'] > 0.7:
            return reasoning['answer']
        else:
            # Ask for human help
            self.request_human_assistance(obstacle)
```

## Best Practices

1. **Validate plans** - Check feasibility before execution
2. **Monitor continuously** - Detect failures early
3. **Replan proactively** - Anticipate problems
4. **Learn from failures** - Store and analyze experiences
5. **Use chain-of-thought** - Improve reasoning quality
6. **Handle uncertainty** - Request clarification when needed

## Common Issues

- Plans too abstract for direct execution
- Failure to detect invalid preconditions
- Infinite replanning loops
- High latency affecting real-time performance
- LLM hallucinations generating infeasible plans

## Next Steps

Apply everything you've learned in the capstone project: building an autonomous humanoid assistant.
