import { useState } from 'react';

/**
 * Smart Image component that handles presigned URL expiration
 *
 * Features:
 * - Detects image load failures
 * - Triggers refresh callback on error
 * - Shows loading state during refresh
 * - Falls back to placeholder on persistent errors
 *
 * @param {string} src - The presigned image URL
 * @param {string} alt - Alt text for the image
 * @param {Function} onError - Callback when image fails to load
 * @param {boolean} isRefreshing - Whether parent is currently refreshing
 * @param {string} className - CSS classes
 * @param {Object} props - Additional img props
 */
export default function PresignedImage({
    src,
    alt,
    onError,
    isRefreshing = false,
    className = '',
    ...props
}) {
    const [imageError, setImageError] = useState(false);
    const [hasTriedRefresh, setHasTriedRefresh] = useState(false);

    const handleError = () => {
        console.log('🖼️ Image load failed:', alt);

        // Only trigger refresh once per image
        if (!hasTriedRefresh && onError) {
            setHasTriedRefresh(true);
            setImageError(true);
            onError();
        } else {
            // Already tried refresh, show error state
            setImageError(true);
        }
    };

    const handleLoad = () => {
        // Image loaded successfully, reset error states
        setImageError(false);
        setHasTriedRefresh(false);
    };

    // Show loading spinner during refresh
    if (isRefreshing) {
        return (
            <div className={`flex items-center justify-center bg-gray-800 ${className}`}>
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-2"></div>
                    <p className="text-white text-sm">Refreshing...</p>
                </div>
            </div>
        );
    }

    // Show error placeholder if image failed even after refresh
    if (imageError && hasTriedRefresh) {
        return (
            <div className={`flex items-center justify-center bg-gray-800 ${className}`}>
                <div className="text-center p-4">
                    <div className="text-4xl mb-2">🖼️</div>
                    <p className="text-white text-sm">Image unavailable</p>
                    <p className="text-gray-400 text-xs mt-1">{alt}</p>
                </div>
            </div>
        );
    }

    return (
        <img
            src={src}
            alt={alt}
            className={className}
            onError={handleError}
            onLoad={handleLoad}
            {...props}
        />
    );
}
