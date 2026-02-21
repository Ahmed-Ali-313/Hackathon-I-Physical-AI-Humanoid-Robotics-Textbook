/**
 * Doc Root Wrapper
 *
 * Wraps all documentation pages with authentication protection.
 */

import React from 'react';
import DocRoot from '@theme-original/DocRoot';
import ProtectedRoute from '../../components/ProtectedRoute';

export default function DocRootWrapper(props) {
  return (
    <ProtectedRoute>
      <DocRoot {...props} />
    </ProtectedRoute>
  );
}
