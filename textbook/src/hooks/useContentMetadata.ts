/**
 * useContentMetadata Hook
 *
 * Fetches content recommendations for the current user.
 * Provides helper function to check if content is recommended.
 */

import { useState, useEffect } from 'react';
import { usePersonalizationContext } from '../contexts/PersonalizationContext';
import { getRecommendations } from '../services/personalizationApi';

interface UseContentMetadataReturn {
  recommendedContentIds: string[];
  isLoading: boolean;
  error: string | null;
  isRecommended: (contentId: string) => boolean;
}

export const useContentMetadata = (): UseContentMetadataReturn => {
  const { preferences } = usePersonalizationContext();
  const [recommendedContentIds, setRecommendedContentIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      // Don't fetch if user has no preferences or is not personalized
      if (!preferences || !preferences.is_personalized) {
        setRecommendedContentIds([]);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const result = await getRecommendations();
        setRecommendedContentIds(result.recommended_content_ids);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch recommendations';
        setError(errorMessage);
        console.error('Error fetching recommendations:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [preferences]);

  const isRecommended = (contentId: string): boolean => {
    return recommendedContentIds.includes(contentId);
  };

  return {
    recommendedContentIds,
    isLoading,
    error,
    isRecommended,
  };
};
