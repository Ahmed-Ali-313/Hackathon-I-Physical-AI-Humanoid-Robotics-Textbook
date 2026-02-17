import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import LandingHero from '@site/src/components/LandingHero';

import styles from './index.module.css';

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Master the fundamentals of humanoid robotics from ROS 2 to Vision-Language-Action models">
      <LandingHero />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}

