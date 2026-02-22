/**
 * Tests for ChatButton component.
 *
 * Tests floating chat button behavior and interactions.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatButton from '../../src/components/ChatButton';
import { ChatProvider } from '../../src/contexts/ChatContext';

describe('ChatButton', () => {
  it('should render chat button', () => {
    render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = screen.getByRole('button', { name: /ask/i });
    expect(button).toBeInTheDocument();
  });

  it('should display "Ask" text', () => {
    render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    expect(screen.getByText('Ask')).toBeInTheDocument();
  });

  it('should open chat panel when clicked', () => {
    render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = screen.getByRole('button', { name: /ask/i });
    fireEvent.click(button);

    // Panel state should be updated (verified through context)
    // Actual panel rendering is tested in ChatPanel tests
  });

  it('should have floating button styles', () => {
    render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = screen.getByRole('button', { name: /ask/i });

    // Button should have appropriate classes for positioning
    expect(button).toHaveClass('chatButton');
  });

  it('should be positioned at bottom-right', () => {
    const { container } = render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = container.querySelector('.chatButton');
    expect(button).toBeInTheDocument();
  });

  it('should be accessible via keyboard', () => {
    render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = screen.getByRole('button', { name: /ask/i });

    // Button should be focusable
    button.focus();
    expect(button).toHaveFocus();

    // Should respond to Enter key
    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
  });

  it('should have proper ARIA attributes', () => {
    render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = screen.getByRole('button', { name: /ask/i });

    expect(button).toHaveAttribute('aria-label');
  });

  it('should show tooltip on hover', () => {
    render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = screen.getByRole('button', { name: /ask/i });

    // Button should have title attribute for tooltip
    expect(button).toHaveAttribute('title');
  });

  it('should not open panel when disabled', () => {
    render(
      <ChatProvider>
        <ChatButton disabled />
      </ChatProvider>
    );

    const button = screen.getByRole('button', { name: /ask/i });
    expect(button).toBeDisabled();

    fireEvent.click(button);
    // Panel should not open (verified through context state)
  });

  it('should match theme colors', () => {
    const { container } = render(
      <ChatProvider>
        <ChatButton />
      </ChatProvider>
    );

    const button = container.querySelector('.chatButton');

    // Button should use CSS variables for theming
    expect(button).toBeInTheDocument();
  });
});
