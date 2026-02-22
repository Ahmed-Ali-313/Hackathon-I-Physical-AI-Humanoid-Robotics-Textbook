/**
 * useTextSelection hook.
 *
 * Detects text selection via Selection API and extracts metadata.
 */

import { useState, useEffect, useCallback } from 'react';

interface TextSelectionMetadata {
  chapter?: string;
  section?: string;
  module?: string;
  url?: string;
}

interface UseTextSelectionReturn {
  selectedText: string | null;
  metadata: TextSelectionMetadata | null;
  clearSelection: () => void;
}

const MIN_SELECTION_LENGTH = 10;

export function useTextSelection(): UseTextSelectionReturn {
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<TextSelectionMetadata | null>(null);

  const clearSelection = useCallback(() => {
    setSelectedText(null);
    setMetadata(null);
  }, []);

  useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();

      if (!selection || selection.rangeCount === 0) {
        clearSelection();
        return;
      }

      const text = selection.toString().trim();

      // Ignore short selections
      if (!text || text.length < MIN_SELECTION_LENGTH) {
        clearSelection();
        return;
      }

      // Extract metadata from selected element
      const range = selection.getRangeAt(0);
      const container = range.commonAncestorContainer;

      // Find the closest element with metadata
      let element: HTMLElement | null =
        container.nodeType === Node.ELEMENT_NODE
          ? (container as HTMLElement)
          : container.parentElement;

      const extractedMetadata: TextSelectionMetadata = {};

      // Walk up the DOM tree to find metadata attributes
      while (element) {
        if (element.hasAttribute('data-chapter')) {
          extractedMetadata.chapter = element.getAttribute('data-chapter') || undefined;
        }
        if (element.hasAttribute('data-section')) {
          extractedMetadata.section = element.getAttribute('data-section') || undefined;
        }
        if (element.hasAttribute('data-module')) {
          extractedMetadata.module = element.getAttribute('data-module') || undefined;
        }

        // Try to extract URL from article or main element
        if (element.tagName === 'ARTICLE' || element.tagName === 'MAIN') {
          // Use current page URL as fallback
          extractedMetadata.url = window.location.pathname;
          break;
        }

        element = element.parentElement;
      }

      setSelectedText(text);
      setMetadata(Object.keys(extractedMetadata).length > 0 ? extractedMetadata : null);
    };

    // Listen for selection changes
    document.addEventListener('selectionchange', handleSelectionChange);

    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, [clearSelection]);

  return {
    selectedText,
    metadata,
    clearSelection,
  };
}
