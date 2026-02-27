/**
 * Root component wrapper
 *
 * Wraps the entire app with AuthProvider, PersonalizationProvider, and ChatProvider
 */

import React, { lazy, Suspense } from 'react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { PersonalizationProvider } from '../contexts/PersonalizationContext';
import { ChatProvider } from '../contexts/ChatContext';
import ChatButton from '../components/ChatButton';

// T089: Lazy load ChatPanel for better performance (code splitting)
const ChatPanel = lazy(() => import('../components/ChatPanel'));

// Inner component that has access to auth context
function RootContent({ children }) {
  const { isAuthenticated } = useAuth();

  return (
    <>
      {children}
      {/* Only show chat button after user is logged in */}
      {isAuthenticated && <ChatButton />}
      {isAuthenticated && (
        <Suspense fallback={<div />}>
          <ChatPanel />
        </Suspense>
      )}
    </>
  );
}

// This component wraps the entire app
export default function Root({ children }) {
  return (
    <AuthProvider>
      <PersonalizationProvider>
        <ChatProvider>
          <RootContent>{children}</RootContent>
        </ChatProvider>
      </PersonalizationProvider>
    </AuthProvider>
  );
}
