/**
 * Signup Page with Personalization
 *
 * Example signup flow that includes personalization preferences.
 * This will be integrated with Better-Auth in future phases.
 */

import React, { useState } from 'react';
import { useNavigate } from '@docusaurus/router';
import PersonalizationForm from '../components/PersonalizationForm';
import { usePersonalizationContext } from '../contexts/PersonalizationContext';
import { PreferenceInput } from '../services/personalizationApi';

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { setPreferences } = usePersonalizationContext();
  const [step, setStep] = useState<'account' | 'preferences'>('account');
  const [accountData, setAccountData] = useState({ email: '', password: '' });

  const handleAccountSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Integrate with Better-Auth for actual account creation
    // For now, just move to preferences step
    setStep('preferences');
  };

  const handlePreferencesSuccess = () => {
    // Preferences saved successfully
    // TODO: Fetch and set preferences in context after Better-Auth integration
    navigate('/');
  };

  const handlePreferencesError = (error: string) => {
    console.error('Failed to save preferences:', error);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
      <h1>Create Your Account</h1>

      {step === 'account' && (
        <div>
          <h2>Step 1: Account Information</h2>
          <form onSubmit={handleAccountSubmit} style={{ marginBottom: '2rem' }}>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem' }}>
                Email
              </label>
              <input
                type="email"
                id="email"
                value={accountData.email}
                onChange={(e) => setAccountData({ ...accountData, email: e.target.value })}
                required
                style={{ width: '100%', padding: '0.75rem', fontSize: '1rem' }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem' }}>
                Password
              </label>
              <input
                type="password"
                id="password"
                value={accountData.password}
                onChange={(e) => setAccountData({ ...accountData, password: e.target.value })}
                required
                style={{ width: '100%', padding: '0.75rem', fontSize: '1rem' }}
              />
            </div>

            <button
              type="submit"
              style={{
                width: '100%',
                padding: '0.875rem',
                fontSize: '1rem',
                fontWeight: 600,
                backgroundColor: 'var(--ifm-color-primary)',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Continue to Preferences
            </button>
          </form>

          <p style={{ textAlign: 'center', color: 'var(--ifm-color-secondary)' }}>
            Note: Better-Auth integration coming in future phase
          </p>
        </div>
      )}

      {step === 'preferences' && (
        <div>
          <h2>Step 2: Personalization Preferences (Optional)</h2>
          <p style={{ marginBottom: '1.5rem', color: 'var(--ifm-color-secondary)' }}>
            Help us personalize your learning experience by sharing your hardware and software setup.
            You can skip this step and add preferences later from your profile.
          </p>

          <PersonalizationForm
            mode="create"
            onSuccess={handlePreferencesSuccess}
            onError={handlePreferencesError}
          />

          <button
            onClick={() => navigate('/')}
            style={{
              width: '100%',
              padding: '0.875rem',
              marginTop: '1rem',
              fontSize: '1rem',
              backgroundColor: 'transparent',
              color: 'var(--ifm-color-primary)',
              border: '1px solid var(--ifm-color-primary)',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Skip for Now
          </button>
        </div>
      )}
    </div>
  );
};

export default SignupPage;
