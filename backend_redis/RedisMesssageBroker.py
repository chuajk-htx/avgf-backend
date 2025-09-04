import redis
import aioredis
import json

class RedisMessageBroker:
    def __init__(self, host='localhost', port=6379):
        self.redis_host = host
        self.redis_port = port
        self.channel = 'grpc_to_websocket'
        self.redis_grpc = redis.Redis(host=self.redis_host, port=self.redis_port)   
        self.redis_ws = aioredis.Redis(host=self.redis_host, port=self.redis_port)
        
    def publish_from_grpc(self, payload: dict):
        try:
            message = json.dumps(payload)
            message['type'] = 'grpc_payload'
            self.redis_grpc.publish(self.channel, message)
        except Exception as e:
            print(f"Error publishing message to Redis: {str(e)}")
    
    async def subscribe_from_ws(self):
        try:
            pubsub = self.redis_ws.pubsub()
            await pubsub.subscribe(self.channel)
            async for message in pubsub.listen():
                if message['type'] == 'grpc_payload':
                    yield json.loads(message['data'])
        except Exception as e:
            print(f"Error subscribing to Redis channel: {str(e)}")