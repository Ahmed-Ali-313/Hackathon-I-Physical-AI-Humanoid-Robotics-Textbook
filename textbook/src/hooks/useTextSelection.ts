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
  const [isSelectionLocked, setIsSelectionLocked] = useState(false);

  const clearSelection = useCallback(() => {
    setSelectedText(null);
    setMetadata(null);
    setIsSelectionLocked(false);
  }, []);

  useEffect(() => {
    const handleSelectionChange = () => {
      // If selection is locked (user already captured it), don't update
      if (isSelectionLocked) {
        return;
      }

      const selection = window.getSelection();

      if (!selection || selection.rangeCount === 0) {
        // Don't clear if we already have a selection stored
        // This prevents clearing when user clicks elsewhere
        return;
      }

      const text = selection.toString().trim();

      // Ignore short selections
      if (!text || text.length < MIN_SELECTION_LENGTH) {
        // Only clear if we don't have a previous selection
        if (!selectedText) {
          clearSelection();
        }
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
      setIsSelectionLocked(true); // Lock the selection once captured
    };

    // Listen for selection changes
    document.addEventListener('selectionchange', handleSelectionChange);

    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, [clearSelection, selectedText, isSelectionLocked]);

  return {
    selectedText,
    metadata,
    clearSelection,
  };
}
