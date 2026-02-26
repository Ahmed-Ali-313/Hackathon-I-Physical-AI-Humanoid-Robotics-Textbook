/**
 * Root component wrapper
 *
 * Wraps the entire app with AuthProvider, PersonalizationProvider, and ChatProvider
 */

import React, { lazy, Suspense } from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import { PersonalizationProvider } from '../contexts/PersonalizationContext';
import { ChatProvider } from '../contexts/ChatContext';
import ChatButton from '../components/ChatButton';

// T089: Lazy load ChatPanel for better performance (code splitting)
const ChatPanel = lazy(() => import('../components/ChatPanel'));

// This component wraps the entire app
export default function Root({ children }) {
  return (
    <AuthProvider>
      <PersonalizationProvider>
        <ChatProvider>
          {children}
          <ChatButton />
          <Suspense fallback={<div />}>
            <ChatPanel />
          </Suspense>
        </ChatProvider>
      </PersonalizationProvider>
    </AuthProvider>
  );
}
