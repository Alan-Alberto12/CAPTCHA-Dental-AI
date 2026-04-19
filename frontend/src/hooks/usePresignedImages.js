import { useState, useEffect, useCallback, useRef } from 'react';

export function usePresignedImages(initialSession, onRefresh) {
    const [session, setSession] = useState(initialSession);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [refreshError, setRefreshError] = useState(null);

    const hasRefreshed = useRef(false);
    const refreshInProgress = useRef(false);

    useEffect(() => {
        setSession(initialSession);
        hasRefreshed.current = false;
    }, [initialSession]);

    const doRefresh = useCallback(async () => {
        if (refreshInProgress.current) return;
        refreshInProgress.current = true;
        setIsRefreshing(true);
        setRefreshError(null);

        try {
            const freshSession = await onRefresh();
            if (freshSession) setSession(freshSession);
        } catch (error) {
            console.error('❌ Failed to refresh session:', error);
            setRefreshError('Failed to refresh images. Please try again.');
        } finally {
            setIsRefreshing(false);
            refreshInProgress.current = false;
        }
    }, [onRefresh]);

    const handleImageError = useCallback((imageId) => {
        if (hasRefreshed.current) {
            console.error('❌ Image failed even after refresh:', imageId);
            setRefreshError('Unable to load images. Please refresh the page.');
            return;
        }
        hasRefreshed.current = true;
        doRefresh();
    }, [doRefresh]);

    const manualRefresh = useCallback(() => {
        hasRefreshed.current = false;
        doRefresh();
    }, [doRefresh]);

    return { session, isRefreshing, refreshError, handleImageError, manualRefresh };
}
