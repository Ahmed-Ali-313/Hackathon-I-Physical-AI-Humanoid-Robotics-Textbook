/**
 * Root component wrapper
 *
 * Wraps the entire app with AuthProvider and PersonalizationProvider
 */

import React from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import { PersonalizationProvider } from '../contexts/PersonalizationContext';

// This component wraps the entire app
export default function Root({ children }) {
  return (
    <AuthProvider>
      <PersonalizationProvider>
        {children}
      </PersonalizationProvider>
    </AuthProvider>
  );
}
