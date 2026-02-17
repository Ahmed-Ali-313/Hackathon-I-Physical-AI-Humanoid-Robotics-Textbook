/**
 * Root component wrapper
 *
 * Wraps the entire Docusaurus app with PersonalizationProvider
 * to make personalization context available throughout the app.
 */

import React from 'react';
import { PersonalizationProvider } from './contexts/PersonalizationContext';

// This component wraps the entire app
export default function Root({ children }) {
  return (
    <PersonalizationProvider>
      {children}
    </PersonalizationProvider>
  );
}
