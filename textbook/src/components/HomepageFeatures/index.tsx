import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

type ModuleItem = {
  title: string;
  icon: string;
  description: ReactNode;
  link: string;
};

const ModuleList: ModuleItem[] = [
  {
    title: 'Module 1: ROS 2',
    icon: '🤖',
    description: (
      <>
        Master the Robot Operating System 2 - the nervous system of modern robots.
        Learn middleware architecture, nodes, topics, services, and URDF modeling.
      </>
    ),
    link: '/docs/module-1-ros2/middleware',
  },
  {
    title: 'Module 2: Digital Twin',
    icon: '🎮',
    description: (
      <>
        Build photorealistic simulations with Gazebo and Unity.
        Master physics engines, sensor simulation, and virtual testing environments.
      </>
    ),
    link: '/docs/module-2-digital-twin/physics-simulation',
  },
  {
    title: 'Module 3: NVIDIA Isaac',
    icon: '⚡',
    description: (
      <>
        Harness GPU-accelerated robotics with NVIDIA Isaac Sim and Isaac ROS.
        Learn hardware-accelerated perception and navigation planning.
      </>
    ),
    link: '/docs/module-3-isaac/isaac-sim',
  },
  {
    title: 'Module 4: VLA Models',
    icon: '🧠',
    description: (
      <>
        Integrate Vision-Language-Action models for intelligent robot control.
        Build cognitive systems with GPT-4, Whisper, and multi-step planning.
      </>
    ),
    link: '/docs/module-4-vla/llm-robotics',
  },
];

function Module({title, icon, description, link}: ModuleItem) {
  return (
    <div className={clsx('col col--3')}>
      <Link to={link} className={styles.moduleCard}>
        <div className="text--center">
          <div className={styles.moduleIcon}>{icon}</div>
        </div>
        <div className="text--center padding-horiz--md">
          <Heading as="h3">{title}</Heading>
          <p>{description}</p>
        </div>
      </Link>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="text--center margin-bottom--lg">
          <Heading as="h2">Course Modules</Heading>
          <p>Explore our comprehensive curriculum covering the full robotics stack</p>
        </div>
        <div className="row">
          {ModuleList.map((props, idx) => (
            <Module key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
