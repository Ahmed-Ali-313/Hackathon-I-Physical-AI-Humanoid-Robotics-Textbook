/**
 * Personalization API Client
 *
 * Handles all API calls related to user personalization preferences
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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
  // TODO: Implement Better-Auth token retrieval
  return localStorage.getItem('auth_token');
};

/**
 * Create personalization preferences (signup)
 */
export const createPreferences = async (
  preferences: PreferenceInput
): Promise<PersonalizationProfile> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(preferences),
  });

  if (!response.ok) {
    throw new Error(`Failed to create preferences: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get user's personalization preferences
 */
export const getPreferences = async (): Promise<PersonalizationProfile> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get preferences: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Update personalization preferences
 */
export const updatePreferences = async (
  preferences: PreferenceInput
): Promise<PersonalizationProfile> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(preferences),
  });

  if (!response.ok) {
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
