import redis
import redis.asyncio as aioredis
import json

class RedisPubSub:
    def __init__(self, host='localhost', port=6379):
        self.redis_host = host
        self.redis_port = port
        self._sync_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)   
        self._async_client = aioredis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        
    ################################################
    #              Synchronous Methods            #
    ################################################    
        
    def publish(self, channel: str, payload: dict):
        try:
            message = json.dumps(payload)           
            self._sync_client.publish(channel, message)
        except Exception as e:
            print(f"Error publishing message to Redis: {str(e)}")
    
    def subscribe(self, channel: str):
        try:
            pubsub = self._sync_client.pubsub()
            pubsub.subscribe(channel)
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        yield json.loads(message['data'].decode('utf-8'))
                    except json.JSONDecodeError:
                        print("Received invalid JSON message")
                    except UnicodeDecodeError:
                        print("Received message with invalid encoding")
        except Exception as e:
            print(f"Error subscribing to Redis channel: {str(e)}")
        finally:
            pubsub.close()
            self._sync_client.close()
    
    ################################################
    #              Asynchronous Methods            # 
    ################################################
    async def publish_async(self, channel: str, payload: dict):
        try:
            message = json.dumps(payload)           
            await self._async_client.publish(channel, message)
        except Exception as e:
            print(f"Error publishing message to Redis: {str(e)}")
       
    async def subscribe_async(self, channel: str):
        try:
            pubsub = self.redis_async.pubsub()
            await pubsub.subscribe(channel)
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        yield json.loads(message['data'].decode('utf-8'))
                    except json.JSONDecodeError:
                        print("Received invalid JSON message")
                    except UnicodeDecodeError:
                        print("Received message with invalid encoding")
        except Exception as e:
            print(f"Error subscribing to Redis channel: {str(e)}")
        finally:
            await pubsub.close()