/**
 * Profile Page
 *
 * Allows users to view and update their personalization preferences.
 * Includes clear all preferences functionality with confirmation.
 */

import React, { useState, useEffect } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import Layout from '@theme/Layout';
import PersonalizationForm from '../components/PersonalizationForm';
import { usePersonalizationContext } from '../contexts/PersonalizationContext';
import { clearPreferences } from '../services/personalizationApi';
import { useAuth } from '../contexts/AuthContext';

const ProfilePageContent: React.FC = () => {
  const { user } = useAuth();
  const { preferences, refetchPreferences, isLoading } = usePersonalizationContext();
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [isRefetching, setIsRefetching] = useState(true);

  // Refetch preferences when component mounts to ensure fresh data
  useEffect(() => {
    const fetchPrefs = async () => {
      if (user) {
        setIsRefetching(true);
        await refetchPreferences();
        setIsRefetching(false);
      }
    };
    fetchPrefs();
  }, [user, refetchPreferences]);

  // Check if user has preferences - must have id and at least one preference field set
  const hasPreferences = !!(
    preferences &&
    preferences.id &&
    preferences.is_personalized
  );

  const handleUpdateSuccess = async () => {
    // Refetch preferences to update context
    await refetchPreferences();
  };

  const handleClearClick = () => {
    setShowClearConfirm(true);
  };

  const handleClearConfirm = async () => {
    setIsClearing(true);
    try {
      await clearPreferences();
      await refetchPreferences();
      setShowClearConfirm(false);
      alert('Preferences cleared successfully!');
    } catch (err) {
      alert('Failed to clear preferences');
    } finally {
      setIsClearing(false);
    }
  };

  const handleClearCancel = () => {
    setShowClearConfirm(false);
  };

  if (!user) {
    return (
      <Layout title="Profile">
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Please log in to view your profile.</p>
        </div>
      </Layout>
    );
  }

  if (isLoading || isRefetching) {
    return (
      <Layout title="Profile">
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Loading preferences...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Profile">
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
        <h1>Your Profile</h1>
        {user?.email && (
          <p style={{ marginBottom: '0.5rem', color: 'var(--ifm-color-secondary)' }}>
            Email: <strong>{user.email}</strong>
          </p>
        )}
        <p style={{ marginBottom: '2rem', color: 'var(--ifm-color-secondary)' }}>
          {hasPreferences
            ? 'Update your personalization preferences to customize your learning experience.'
            : 'Set up your preferences to get personalized content recommendations.'}
        </p>

        {hasPreferences && preferences ? (
          <>
            <PersonalizationForm
              key={preferences.id} // Force remount when preferences change
              mode="edit"
              initialValues={{
                workstation_type: preferences.workstation_type,
                edge_kit_available: preferences.edge_kit_available,
                robot_tier_access: preferences.robot_tier_access,
                ros2_level: preferences.ros2_level,
                gazebo_level: preferences.gazebo_level,
                unity_level: preferences.unity_level,
                isaac_level: preferences.isaac_level,
                vla_level: preferences.vla_level,
              }}
              onSuccess={handleUpdateSuccess}
            />

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <button
                onClick={handleClearClick}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'transparent',
                  color: 'var(--ifm-color-danger)',
                  border: '1px solid var(--ifm-color-danger)',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                }}
              >
                Clear All Preferences
              </button>
            </div>

            {showClearConfirm && (
              <div
                style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 1000,
                }}
              >
                <div
                  style={{
                    backgroundColor: 'var(--ifm-background-color)',
                    padding: '2rem',
                    borderRadius: '8px',
                    maxWidth: '400px',
                    textAlign: 'center',
                  }}
                >
                  <h3>Are you sure?</h3>
                  <p>This will clear all your personalization preferences.</p>
                  <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1.5rem' }}>
                    <button
                      onClick={handleClearConfirm}
                      disabled={isClearing}
                      style={{
                        padding: '0.75rem 1.5rem',
                        backgroundColor: 'var(--ifm-color-danger)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: isClearing ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {isClearing ? 'Clearing...' : 'Confirm'}
                    </button>
                    <button
                      onClick={handleClearCancel}
                      disabled={isClearing}
                      style={{
                        padding: '0.75rem 1.5rem',
                        backgroundColor: 'transparent',
                        color: 'var(--ifm-color-primary)',
                        border: '1px solid var(--ifm-color-primary)',
                        borderRadius: '4px',
                        cursor: isClearing ? 'not-allowed' : 'pointer',
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <PersonalizationForm
            mode="create"
            onSuccess={handleUpdateSuccess}
          />
        )}
      </div>
    </Layout>
  );
};

const ProfilePage: React.FC = () => {
  return (
    <BrowserOnly fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>}>
      {() => <ProfilePageContent />}
    </BrowserOnly>
  );
};

export default ProfilePage;
