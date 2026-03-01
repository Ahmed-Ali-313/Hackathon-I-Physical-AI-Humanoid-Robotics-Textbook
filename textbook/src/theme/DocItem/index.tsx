/**
 * DocItem Wrapper
 * Feature: 005-urdu-translation
 * Purpose: Integrate TranslationControl into chapter pages
 */

import React from 'react';
import DocItem from '@theme-original/DocItem';
import TranslationControl from '../../components/TranslationControl';
import type {Props} from '@theme/DocItem';

export default function DocItemWrapper(props: Props) {
  // Access metadata from props instead of useDoc hook
  const { content } = props;
  const { metadata, frontMatter } = content;

  // Extract chapter ID from the doc path
  // Example: docs/01-introduction-to-ros2.md -> 01-introduction-to-ros2
  const chapterId = metadata.id || metadata.slug || 'unknown';

  // Get original content
  const originalContent = metadata.description || '';

  // Check if user is authenticated (check for auth token)
  const isAuthenticated = typeof window !== 'undefined' && localStorage.getItem('auth_token');

  // Only show translation control for authenticated users and on doc pages
  const showTranslationControl = isAuthenticated;

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
