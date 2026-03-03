/**
 * Personalization API Client
 *
 * Handles all API calls related to user personalization preferences
 */

const API_BASE_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost'
      ? 'http://localhost:8001/api/v1'
      : 'https://ai-native-book-backend.onrender.com/api/v1')
  : 'http://localhost:8001/api/v1';

export interface PersonalizationProfile {
  id: string;
  user_id: string;
  workstation_type?: string;
  edge_kit_available?: string;
  robot_tier_access?: string;
  ros2_level?: string;
  gazebo_level?: string;
  unity_level?: string;
  isaac_level?: string;
  vla_level?: string;
  is_personalized: boolean;
  created_at: string;
  updated_at: string;
}

export interface PreferenceInput {
  workstation_type?: string;
  edge_kit_available?: string;
  robot_tier_access?: string;
  ros2_level?: string;
  gazebo_level?: string;
  unity_level?: string;
  isaac_level?: string;
  vla_level?: string;
}

/**
 * Get authentication token from storage
 */
const getAuthToken = (): string | null => {
  const token = localStorage.getItem('auth_token');
  if (!token) {
    console.warn('No auth token found in localStorage');
  }
  return token;
};

/**
 * Create personalization preferences (signup)
 */
export const createPreferences = async (
  preferences: PreferenceInput
): Promise<PersonalizationProfile> => {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in again.');
  }

  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(preferences),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('[createPreferences] Failed:', response.status, errorText);

    // If preferences already exist, try updating instead
    if (response.status === 409) {
      return updatePreferences(preferences);
    }

    throw new Error(`Failed to create preferences: ${response.statusText}`);
  }

  const data = await response.json();
  return data;
};

/**
 * Get user's personalization preferences
 */
export const getPreferences = async (): Promise<PersonalizationProfile | null> => {
  const token = getAuthToken();

  if (!token) {
    return null;
  }

  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (response.status === 404) {
    // User has no preferences yet
    return null;
  }

  if (!response.ok) {
    const errorText = await response.text();
    console.error('[getPreferences] Failed:', response.status, errorText);
    throw new Error(`Failed to get preferences: ${response.statusText}`);
  }

  const data = await response.json();
  return data;
};

/**
 * Update personalization preferences
 */
export const updatePreferences = async (
  preferences: PreferenceInput
): Promise<PersonalizationProfile> => {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in again.');
  }

  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(preferences),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('[updatePreferences] Failed:', response.status, errorText);
    throw new Error(`Failed to update preferences: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Clear all personalization preferences
 */
export const clearPreferences = async (): Promise<void> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to clear preferences: ${response.statusText}`);
  }
};

/**
 * Get recommended content IDs for user
 */
export const getRecommendations = async (): Promise<{
  recommended_content_ids: string[];
  match_reasons: Record<string, any>;
}> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/content/recommendations`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get recommendations: ${response.statusText}`);
  }

  return response.json();
};
