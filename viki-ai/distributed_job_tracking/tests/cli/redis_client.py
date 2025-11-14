import asyncio
import redis.asyncio as redis
from datetime import datetime


async def redis_test_function():
    """
    Async function that connects to Redis, saves a key, and returns a key value.
    """
    # Connect to Redis
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
    
    try:
        # Test connection
        await redis_client.ping()
        print("✅ Connected to Redis successfully")
        
        # Save a test key with current timestamp
        test_key = "test_key"
        test_value = f"test_value_{datetime.now().isoformat()}"
        
        await redis_client.set(test_key, test_value)
        print(f"✅ Saved key '{test_key}' with value '{test_value}'")
        
        # Retrieve the key value
        retrieved_value = await redis_client.get(test_key)
        print(f"✅ Retrieved key '{test_key}' with value '{retrieved_value}'")
        
        # Clean up - delete the test key
        await redis_client.delete(test_key)
        print(f"✅ Cleaned up test key '{test_key}'")
        
        return retrieved_value
        
    except redis.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return None
    except Exception as e:
        print(f"❌ Error during Redis operation: {e}")
        return None
    finally:
        # Close the connection
        await redis_client.aclose()
        print("✅ Redis connection closed")


async def main():
    """Main function to run the Redis test."""
    print("Starting Redis test...")
    result = await redis_test_function()
    if result:
        print(f"Test completed successfully. Retrieved value: {result}")
    else:
        print("Test failed.")


if __name__ == "__main__":
    asyncio.run(main())
