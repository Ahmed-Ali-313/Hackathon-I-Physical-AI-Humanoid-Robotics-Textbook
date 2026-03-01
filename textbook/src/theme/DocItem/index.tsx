/**
 * DocItem Wrapper
 * Feature: 005-urdu-translation
 * Purpose: Integrate TranslationControl and display translated content
 */

import React from 'react';
import DocItem from '@theme-original/DocItem';
import TranslationControl from '../../components/TranslationControl';
import { useTranslation } from '../../hooks/useTranslation';
import type {Props} from '@theme/DocItem';
import ReactMarkdown from 'react-markdown';

export default function DocItemWrapper(props: Props) {
  // Access metadata from props
  const { content } = props;
  const { metadata } = content;

  // Extract chapter ID from the doc path
  const chapterId = metadata.id || metadata.slug || 'unknown';

  // Get original content
  const originalContent = metadata.description || '';

  // Check if user is authenticated
  const isAuthenticated = typeof window !== 'undefined' && localStorage.getItem('auth_token');

  // Use translation hook to manage state
  const {
    isUrdu,
    translatedContent,
    isLoading,
    error,
    toggleLanguage,
    clearError
  } = useTranslation(chapterId, originalContent);

  return (
    <>
      {/* Translation control button */}
      <div style={{ marginBottom: '2rem' }}>
        <TranslationControl
          chapterId={chapterId}
          originalContent={originalContent}
          isUrdu={isUrdu}
          isLoading={isLoading}
          error={error}
          onToggle={toggleLanguage}
          onClearError={clearError}
        />
      </div>

      {/* Display translated content if in Urdu mode and translation is available */}
      {isUrdu && translatedContent ? (
        <div className="markdown" dir="rtl" style={{
          fontFamily: "'Noto Nastaliq Urdu', serif",
          fontSize: '1.1rem',
          lineHeight: '1.8'
        }}>
          <style>{`
            /* Keep code blocks LTR in RTL mode */
            .markdown[dir="rtl"] pre,
            .markdown[dir="rtl"] code,
            .markdown[dir="rtl"] pre code {
              direction: ltr !important;
              text-align: left !important;
              font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace !important;
            }

            /* Keep inline code LTR */
            .markdown[dir="rtl"] p code,
            .markdown[dir="rtl"] li code {
              direction: ltr !important;
              display: inline-block;
              unicode-bidi: embed;
            }
          `}</style>
          <ReactMarkdown>{translatedContent}</ReactMarkdown>
        </div>
      ) : (
        <DocItem {...props} />
      )}
    </>
  );
}
