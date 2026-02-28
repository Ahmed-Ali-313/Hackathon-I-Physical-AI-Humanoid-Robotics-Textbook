/**
 * DocItem Wrapper
 * Feature: 005-urdu-translation
 * Purpose: Integrate TranslationControl into chapter pages
 */

import React from 'react';
import DocItem from '@theme-original/DocItem';
import { useDoc } from '@docusaurus/theme-common/internal';
import TranslationControl from '../../components/TranslationControl';
import styles from '../../components/TranslationControl/styles.module.css';

export default function DocItemWrapper(props) {
  const { metadata, frontMatter } = useDoc();

  // Extract chapter ID from the doc path
  // Example: docs/01-introduction-to-ros2.md -> 01-introduction-to-ros2
  const chapterId = metadata.id;

  // Get original content (we'll need to pass this to TranslationControl)
  // For now, we'll use the rendered content
  const originalContent = metadata.description || '';

  // Check if user is authenticated (check for auth token)
  const isAuthenticated = typeof window !== 'undefined' && localStorage.getItem('auth_token');

  // Only show translation control for authenticated users and on doc pages
  const showTranslationControl = isAuthenticated && metadata.type === 'doc';

  return (
    <>
      {showTranslationControl && (
        <div style={{ marginBottom: '2rem' }}>
          <TranslationControl
            chapterId={chapterId}
            originalContent={originalContent}
          />
        </div>
      )}
      <DocItem {...props} />
    </>
  );
}
