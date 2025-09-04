import asyncio
import json
import base64
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from connectionmanager import ConnectionManager
from backend_redis.RedisClient import RedisPubSub
from dotenv import load_dotenv
import uvicorn
import logging
import uuid
from contact_lens_detection import AnalyzeImageAsync


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

UPLOAD_DIR = "./received_images"

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

#instantiate FastAPI app
app = FastAPI()

#instantiate ConnectionManager
connection_manager = ConnectionManager()

#instantiate RedisClient
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = RedisPubSub(redis_host, redis_port)

@app.websocket("/analyze")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())[:8]  # Generate a short unique client ID
    
    #ping_task = asyncio.create_task(ping_client(websocket, client_id))
    await connection_manager.connect(websocket, client_id)  
    try:
        sub_messages = redis_client.subscribe_async('upload_image')
        async for sub_message in sub_messages:
            try:
                sub_message['type'] = "show_image"
                await connection_manager.send_message(sub_message, client_id)
                outcome = await AnalyzeImageAsync(sub_message['image_base64'])
                sub_message['type'] = "show_result"
                sub_message['result'] = outcome
                logger.info(f"{json.dumps(sub_message)}")
                await connection_manager.send_message(sub_message, client_id)
            except json.JSONDecodeError:
                await send_error("Invalid JSON format", client_id)
            except Exception as e:
                await send_error(f"Error processing message: {str(e)}", client_id)
                
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Unexpected error for client {client_id}: {str(e)}")
        connection_manager.disconnect(client_id)
        #ping_task.cancel()
    
async def send_error(error_message: str, client_id: str):
    logger.error(f"Error for client {client_id}: {error_message}")
    message= {
        "origin": "error",
        "data": error_message,
    }
    await connection_manager.send_message(message, client_id)
    

async def ping_client(websocket: WebSocket, client_id: str):
    try:
        while True:
            await asyncio.sleep(30)  # Ping every 30 seconds
            await connection_manager.send_message(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
        #ping_task.cancel()
    except Exception as e:
        print(f"Error in pinging client {client_id}: {e}")
        connection_manager.disconnect(client_id)


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )