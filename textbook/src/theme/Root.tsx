/**
 * Root component wrapper
 *
 * Wraps the entire app with AuthProvider, PersonalizationProvider, and ChatProvider
 */

import React from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import { PersonalizationProvider } from '../contexts/PersonalizationContext';
import { ChatProvider } from '../contexts/ChatContext';
import ChatButton from '../components/ChatButton';
import ChatPanel from '../components/ChatPanel';

// This component wraps the entire app
export default function Root({ children }) {
  return (
    <AuthProvider>
      <PersonalizationProvider>
        <ChatProvider>
          {children}
          <ChatButton />
          <ChatPanel />
        </ChatProvider>
      </PersonalizationProvider>
    </AuthProvider>
  );
}
