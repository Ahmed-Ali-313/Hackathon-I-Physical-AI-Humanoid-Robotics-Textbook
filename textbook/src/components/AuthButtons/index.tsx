/**
 * Auth Buttons Component
 *
 * Shows login/signup buttons or user menu in navbar.
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

export default function AuthButtons() {
  const { user, isAuthenticated, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);

  if (!isAuthenticated) {
    return (
      <div className={styles.authButtons}>
        <a href="/login" className={styles.loginButton}>
          Login
        </a>
        <a href="/signup" className={styles.signupButton}>
          Sign Up
        </a>
      </div>
    );
  }

  return (
    <div className={styles.userMenu}>
      <button
        className={styles.userButton}
        onClick={() => setShowMenu(!showMenu)}
      >
        {user?.email.charAt(0).toUpperCase()}
      </button>
      {showMenu && (
        <div className={styles.dropdown}>
          <div className={styles.userEmail}>{user?.email}</div>
          <a href="/profile" className={styles.dropdownItem}>
            Profile & Preferences
          </a>
          <button onClick={logout} className={styles.dropdownItem}>
            Logout
          </button>
        </div>
      )}
    </div>
  );
}
