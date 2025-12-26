"""
ComfyUI 客户端 - 与本地 ComfyUI 实例通信

@input:  config (COMFYUI_ENABLED/HOST), workflow_api.json
@output: generate_image(prompt) -> 本地图片路径
@pos:    图像生成的本地 AI 通道，被 v2/image_generator.py 调用

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/_FOLDER.md
"""

import json
import os
import websocket
import uuid
import urllib.request
import urllib.parse
import random
import time
import logging
import config

logger = logging.getLogger(__name__)

def generate_image(prompt_text, seed=None):
    """
    Generate an image using the local ComfyUI instance.
    Returns local file path of the generated image, or None if failed.
    """
    if not config.COMFYUI_ENABLED:
        return None

    address = config.COMFYUI_HOST
    # Check connectivity
    try:
        urllib.request.urlopen(f"http://{address}/system_stats", timeout=2)
    except:
        # Silent fail or log warning
        # logger.debug(f"ComfyUI offline at {address}")
        return None

    client_id = str(uuid.uuid4())
    
    try:
        # 1. Load Workflow
        if not os.path.exists(config.COMFYUI_WORKFLOW_FILE):
             logger.error("Workflow file not found")
             return None
             
        with open(config.COMFYUI_WORKFLOW_FILE, 'r') as f:
            workflow = json.load(f)

        # 2. Modify Workflow
        # Node "45": Positive Prompt (CLIPTextEncode)
        # Node "44": KSampler (Seed)
        # Node "41": EmptySD3LatentImage (Dimensions)
        
        if "45" in workflow and "inputs" in workflow["45"]:
            workflow["45"]["inputs"]["text"] = prompt_text
        
        if seed is None:
            seed = random.randint(1, 1000000000)
            
        if "44" in workflow and "inputs" in workflow["44"]:
            workflow["44"]["inputs"]["seed"] = seed

        # 3. Connect WebSocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{address}/ws?clientId={client_id}")

        # 4. Submit Task
        payload = {
            "prompt": workflow,
            "client_id": client_id
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(f"http://{address}/prompt", data=data)
        response = urllib.request.urlopen(req)
        prompt_id = json.loads(response.read())['prompt_id']
        
        # 5. Wait for completion
        # Timeout after 120 seconds (large images take longer)
        start_time = time.time()
        while True:
            if time.time() - start_time > 120:
                ws.close()
                logger.warning("ComfyUI generation timeout")
                return None
                
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break # Finished
            else:
                continue
        
        ws.close()

        # 6. Get Output Path
        with urllib.request.urlopen(f"http://{address}/history/{prompt_id}") as response:
            history = json.loads(response.read())[prompt_id]
            
        # Assuming Node "9" is SaveImage
        if '9' in history['outputs']:
            outputs = history['outputs']['9']['images']
        else:
            # Fallback: Find first output
            first_key = list(history['outputs'].keys())[0]
            outputs = history['outputs'][first_key]['images']
        
        # Download first image
        if outputs:
            image = outputs[0]
            filename = image['filename']
            subfolder = image['subfolder']
            image_type = image['type']
            
            url_values = urllib.parse.urlencode({
                "filename": filename,
                "subfolder": subfolder,
                "type": image_type
            })
            
            # Save to shared output directory so frontend can serve it if needed, 
            # Or just return local path for python-pptx to use.
            # python-pptx needs absolute path.
            
            # We save to 'output/assets'
            output_dir = os.path.abspath("output/assets")
            os.makedirs(output_dir, exist_ok=True)
            local_filename = f"ai_{uuid.uuid4().hex[:8]}_{filename}"
            local_path = os.path.join(output_dir, local_filename)
            
            urllib.request.urlretrieve(f"http://{address}/view?{url_values}", local_path)
            
            logger.info(f"ComfyUI Image generated: {local_path}")
            return local_path
            
    except Exception as e:
        logger.error(f"ComfyUI Error: {e}")
        return None
    
    return None
