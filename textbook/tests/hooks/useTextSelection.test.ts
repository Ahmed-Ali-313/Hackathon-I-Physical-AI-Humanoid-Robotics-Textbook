/**
 * Tests for useTextSelection hook.
 *
 * Tests text selection detection using Selection API.
 */

import { renderHook, act } from '@testing-library/react';
import { useTextSelection } from '../../src/hooks/useTextSelection';

describe('useTextSelection', () => {
  beforeEach(() => {
    // Clear any existing selection
    window.getSelection()?.removeAllRanges();
  });

  it('should return null when no text is selected', () => {
    const { result } = renderHook(() => useTextSelection());

    expect(result.current.selectedText).toBeNull();
    expect(result.current.metadata).toBeNull();
  });

  it('should detect selected text', () => {
    // Create a text node and select it
    const div = document.createElement('div');
    div.textContent = 'VSLAM is a technique for robotics.';
    document.body.appendChild(div);

    const range = document.createRange();
    range.selectNodeContents(div);

    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);

    const { result } = renderHook(() => useTextSelection());

    act(() => {
      // Trigger selection change
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.selectedText).toBe('VSLAM is a technique for robotics.');

    document.body.removeChild(div);
  });

  it('should extract metadata from selected element', () => {
    const article = document.createElement('article');
    article.setAttribute('data-chapter', 'isaac-sim');
    article.setAttribute('data-section', 'intro');
    article.textContent = 'Test content';
    document.body.appendChild(article);

    const range = document.createRange();
    range.selectNodeContents(article);

    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);

    const { result } = renderHook(() => useTextSelection());

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.metadata).toEqual({
      chapter: 'isaac-sim',
      section: 'intro',
    });

    document.body.removeChild(article);
  });

  it('should clear selection when text is deselected', () => {
    const div = document.createElement('div');
    div.textContent = 'Test content';
    document.body.appendChild(div);

    const range = document.createRange();
    range.selectNodeContents(div);

    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);

    const { result } = renderHook(() => useTextSelection());

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.selectedText).toBe('Test content');

    // Clear selection
    selection?.removeAllRanges();

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.selectedText).toBeNull();

    document.body.removeChild(div);
  });

  it('should ignore selections shorter than 10 characters', () => {
    const div = document.createElement('div');
    div.textContent = 'Short';
    document.body.appendChild(div);

    const range = document.createRange();
    range.selectNodeContents(div);

    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);

    const { result } = renderHook(() => useTextSelection());

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.selectedText).toBeNull();

    document.body.removeChild(div);
  });

  it('should trim whitespace from selected text', () => {
    const div = document.createElement('div');
    div.textContent = '  VSLAM is a technique  ';
    document.body.appendChild(div);

    const range = document.createRange();
    range.selectNodeContents(div);

    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);

    const { result } = renderHook(() => useTextSelection());

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.selectedText).toBe('VSLAM is a technique');

    document.body.removeChild(div);
  });

  it('should provide clearSelection function', () => {
    const div = document.createElement('div');
    div.textContent = 'Test content for selection';
    document.body.appendChild(div);

    const range = document.createRange();
    range.selectNodeContents(div);

    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);

    const { result } = renderHook(() => useTextSelection());

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.selectedText).toBe('Test content for selection');

    act(() => {
      result.current.clearSelection();
    });

    expect(result.current.selectedText).toBeNull();

    document.body.removeChild(div);
  });
});
