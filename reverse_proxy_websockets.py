import asyncio

from typing import Optional

import urllib

from fastapi import FastAPI, Request

from fastapi import WebSocket

import websockets

from starlette.websockets import WebSocketDisconnect

import json

from typing import Dict

import os


app = FastAPI()

ws_b_uri = "wss://origin-websocket-server/?c="


async def forward(ws_a: WebSocket, ws_b: websockets.WebSocketClientProtocol):
    
    stop_task = False

    while not stop_task:

        try:
            
            data = await ws_a.receive_text()
            
            print("websocket A received:", data)
            
            await ws_b.send(data)
        
        except WebSocketDisconnect as e:
            
            print('Client Disconnected from Reverse Proxy')
            
            stop_task = True
            
        except websockets.exceptions.ConnectionClosedOK as e:
            
            print('Client Disconnected from Origin WebSocket Server')
            
            stop_task = True
            

async def reverse(ws_a: WebSocket, ws_b: websockets.WebSocketClientProtocol):
    
    stop_task = False

    while not stop_task:
        
        try:
            
            data = await ws_b.recv()
            
            await ws_a.send_text(data)
            
            print("websocket A sent:", data)

        except WebSocketDisconnect as e:
            
            print('Client Disconnected from Reverse Proxy')
            
            stop_task = True
            
        
        except websockets.exceptions.ConnectionClosedOK as e:
            
            print('Client Disconnected from Origin WebSocket Server')
            
            stop_task = True
            

async def socket_connection(ws_a: WebSocket, ws_b_client: websockets.WebSocketClientProtocol):
    
    loop = asyncio.get_event_loop()
    
    fwd_task = loop.create_task(forward(ws_a, ws_b_client))
    
    rev_task = loop.create_task(reverse(ws_a, ws_b_client))
    
    await asyncio.gather(fwd_task, rev_task)



@app.websocket("/")
async def websocket_a(ws_a: WebSocket, c:str):
    
    await ws_a.accept()

    socket_url = ws_b_uri + urllib.parse.quote(c)
    
    try:
       
       async with websockets.connect(socket_url) as ws_b_client:
       
          await socket_connection(ws_a, ws_b_client)
    
    except:
       
       pass

