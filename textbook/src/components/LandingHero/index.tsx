import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Heading from '@theme/Heading';

import styles from './styles.module.css';

export default function LandingHero(): ReactNode {
  const {siteConfig} = useDocusaurusContext();

  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Begin Your Journey 🚀
          </Link>
        </div>
        <div className={styles.heroDescription}>
          <p>
            Learn to build intelligent humanoid robots from the ground up.
            This comprehensive course covers ROS 2, digital twin simulation,
            NVIDIA Isaac, and cutting-edge Vision-Language-Action models.
          </p>
        </div>
      </div>
    </header>
  );
}
