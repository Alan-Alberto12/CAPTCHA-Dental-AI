import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook to manage presigned S3 URLs with automatic refresh
 *
 * Features:
 * - Detects when images fail to load (expired presigned URLs)
 * - Automatically refreshes the session to get new presigned URLs
 * - Prevents infinite refresh loops
 * - Handles errors gracefully
 *
 * @param {Object} initialSession - The initial session object with images
 * @param {Function} onRefresh - Callback to fetch fresh session data
 * @returns {Object} { session, isRefreshing, refreshError, handleImageError }
 */
export function usePresignedImages(initialSession, onRefresh) {
    const [session, setSession] = useState(initialSession);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [refreshError, setRefreshError] = useState(null);

    // Track which images have failed to prevent infinite loops
    const failedImages = useRef(new Set());
    const refreshInProgress = useRef(false);

    // Update session when initialSession changes
    useEffect(() => {
        setSession(initialSession);
        // Reset failed images when we get a new session
        failedImages.current.clear();
    }, [initialSession]);

    /**
     * Handle image load errors (likely due to expired presigned URLs)
     */
    const handleImageError = useCallback(async (imageId) => {
        // Prevent multiple simultaneous refreshes
        if (refreshInProgress.current) {
            console.log('🔄 Refresh already in progress, skipping...');
            return;
        }

        // Check if we've already tried to refresh this image
        if (failedImages.current.has(imageId)) {
            console.error('❌ Image failed even after refresh:', imageId);
            setRefreshError('Unable to load images. Please refresh the page.');
            return;
        }

        console.log('⚠️ Image failed to load (likely expired URL), refreshing session...', imageId);

        refreshInProgress.current = true;
        setIsRefreshing(true);
        setRefreshError(null);
        failedImages.current.add(imageId);

        try {
            // Call the refresh callback to get new presigned URLs
            const freshSession = await onRefresh();

            if (freshSession) {
                console.log('✅ Session refreshed with new presigned URLs');
                setSession(freshSession);
                // Clear failed images after successful refresh
                setTimeout(() => {
                    failedImages.current.clear();
                }, 1000);
            }
        } catch (error) {
            console.error('❌ Failed to refresh session:', error);
            setRefreshError('Failed to refresh images. Please try again.');
        } finally {
            setIsRefreshing(false);
            refreshInProgress.current = false;
        }
    }, [onRefresh]);

    /**
     * Manually trigger a refresh (useful for "retry" buttons)
     */
    const manualRefresh = useCallback(async () => {
        setIsRefreshing(true);
        setRefreshError(null);
        failedImages.current.clear();

        try {
            const freshSession = await onRefresh();
            if (freshSession) {
                setSession(freshSession);
            }
        } catch (error) {
            console.error('❌ Manual refresh failed:', error);
            setRefreshError('Failed to refresh images.');
        } finally {
            setIsRefreshing(false);
        }
    }, [onRefresh]);

    return {
        session,
        isRefreshing,
        refreshError,
        handleImageError,
        manualRefresh
    };
}
