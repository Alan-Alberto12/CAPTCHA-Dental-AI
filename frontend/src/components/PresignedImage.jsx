import { useState, useEffect } from 'react';

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

    useEffect(() => {
        setImageError(false);
        setHasTriedRefresh(false);
    }, [src]);

    const handleError = () => {
        if (!hasTriedRefresh && onError) {
            setHasTriedRefresh(true);
            setImageError(true);
            onError();
        } else {
            setImageError(true);
        }
    };

    const handleLoad = () => {
        setImageError(false);
        setHasTriedRefresh(false);
    };

    if (isRefreshing) {
        return (
            <div className={`flex items-center justify-center bg-gray-800 ${className}`}>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            </div>
        );
    }

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
