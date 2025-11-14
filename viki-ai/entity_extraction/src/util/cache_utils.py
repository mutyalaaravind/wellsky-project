"""
Cache utilities for managing aiocache instances.
"""
from aiocache import Cache
from util.custom_logger import getLogger

logger = getLogger(__name__)


async def clear_pipeline_config_cache():
    """
    Clear the pipeline configuration cache.
    This can be used when pipeline configurations are updated and need to be refreshed.
    """
    try:
        cache = Cache.MEMORY
        await cache.clear()
        logger.info("Pipeline configuration cache cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing pipeline configuration cache: {str(e)}")
        raise


async def get_cache_stats():
    """
    Get cache statistics for monitoring purposes.
    
    Returns:
        Dict containing cache statistics
    """
    try:
        cache = Cache.MEMORY
        # Note: aiocache doesn't provide built-in stats, but we can add custom tracking if needed
        logger.info("Cache statistics requested")
        return {"status": "cache_active", "type": "memory"}
    except Exception as e:
        logger.error(f"Error getting cache statistics: {str(e)}")
        return {"status": "error", "error": str(e)}
