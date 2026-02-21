/**
 * Signup Page with Authentication
 *
 * Professional signup form with personalization preferences.
 */

import React, { useState } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { useHistory } from '@docusaurus/router';
import Layout from '@theme/Layout';
import PersonalizationForm from '../components/PersonalizationForm';
import { useAuth } from '../contexts/AuthContext';
import { usePersonalizationContext } from '../contexts/PersonalizationContext';
import styles from './auth.module.css';

const SignupPageContent: React.FC = () => {
  const history = useHistory();
  const { signup } = useAuth();
  const { refetchPreferences } = usePersonalizationContext();
  const [step, setStep] = useState<'account' | 'preferences'>('account');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await signup(email, password);
      setStep('preferences');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreferencesSuccess = async () => {
    // Refetch preferences to update context after saving
    await refetchPreferences();
    history.push('/docs/intro');
  };

  const handleSkip = () => {
    history.push('/docs/intro');
  };

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        {step === 'account' && (
          <>
            <h1 className={styles.authTitle}>Create Your Account</h1>
            <p className={styles.authSubtitle}>
              Join to access personalized robotics learning content
            </p>

            {error && (
              <div className={styles.errorMessage}>
                {error}
              </div>
            )}

            <form onSubmit={handleAccountSubmit} className={styles.authForm}>
              <div className={styles.formGroup}>
                <label htmlFor="email" className={styles.formLabel}>
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className={styles.formInput}
                  placeholder="you@example.com"
                  disabled={isLoading}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="password" className={styles.formLabel}>
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className={styles.formInput}
                  placeholder="At least 6 characters"
                  disabled={isLoading}
                />
              </div>

              <button
                type="submit"
                className={styles.submitButton}
                disabled={isLoading}
              >
                {isLoading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>

            <div className={styles.authFooter}>
              <p>
                Already have an account?{' '}
                <a href="/login" className={styles.authLink}>
                  Sign in
                </a>
              </p>
            </div>
          </>
        )}

        {step === 'preferences' && (
          <>
            <h1 className={styles.authTitle}>Personalize Your Experience</h1>
            <p className={styles.authSubtitle}>
              Tell us about your setup to get tailored content recommendations
            </p>

            <PersonalizationForm
              mode="create"
              onSuccess={handlePreferencesSuccess}
              onError={(error) => console.error(error)}
            />

            <button
              onClick={handleSkip}
              className={styles.submitButton}
              style={{ marginTop: '1rem', background: 'transparent', color: 'var(--ifm-color-primary)', border: '1px solid var(--ifm-color-primary)' }}
            >
              Skip for Now
            </button>
          </>
        )}
      </div>
    </div>
  );
};

const SignupPage: React.FC = () => {
  return (
    <Layout title="Sign Up">
      <BrowserOnly fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>}>
        {() => <SignupPageContent />}
      </BrowserOnly>
    </Layout>
  );
};

export default SignupPage;
