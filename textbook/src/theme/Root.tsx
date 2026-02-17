/**
 * Root component wrapper
 *
 * Phase 1: Basic textbook without personalization
 * PersonalizationProvider will be added in Phase 2
 */

import React from 'react';

// This component wraps the entire app
export default function Root({ children }) {
  return <>{children}</>;
}
