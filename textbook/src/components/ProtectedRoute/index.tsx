/**
 * Protected Route Component
 *
 * Redirects to login if user is not authenticated.
 */

import React, { useEffect } from 'react';
import { useHistory, useLocation } from '@docusaurus/router';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const history = useHistory();
  const location = useLocation();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect to login with return URL
      history.push(`/login?redirect=${encodeURIComponent(location.pathname)}`);
    }
  }, [isAuthenticated, isLoading, history, location]);

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
