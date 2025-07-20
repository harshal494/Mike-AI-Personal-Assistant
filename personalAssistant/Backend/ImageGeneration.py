import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os 
from time import sleep

# Debug setup
DEBUG = True  # Set to False in production

def log(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ","_")
    Files = [f"{prompt}{i}.jpg" for i in range(1,5)]
    
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                log(f"Opening image: {image_path}")
                img.show()
                sleep(1)
            else:
                log(f"Image not found: {image_path}")
        except Exception as e:
            log(f"Error opening {image_path}: {str(e)}")

# Verify API Key
API_KEY = get_key('.env', 'HuggingFaceAPIKey')
if not API_KEY:
    print("Error: Missing HuggingFace API key in .env file")
    exit()

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_KEY}"}

async def query(payload):
    try:
        response = await asyncio.to_thread(
            requests.post, 
            API_URL, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 429:
            log("Rate limited - waiting 10 seconds")
            await asyncio.sleep(10)
            return await query(payload)
        else:
            log(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        log(f"Request failed: {str(e)}")
        return None

async def generate_images(prompt: str):
    # Ensure output directory exists
    os.makedirs("Data", exist_ok=True)
    
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        
    image_bytes_list = await asyncio.gather(*tasks)
    
    success_count = 0
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            filename = fr"Data\{prompt.replace(' ','_')}{i + 1}.jpg"
            try:
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                success_count += 1
            except Exception as e:
                log(f"Error saving {filename}: {str(e)}")
    
    log(f"Successfully generated {success_count}/4 images")
    return success_count > 0

def GenerateImages(prompt: str):
    log(f"Starting generation for: {prompt}")
    result = asyncio.run(generate_images(prompt))
    if result:
        open_images(prompt)
    return result

# Main loop with better error handling
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data = f.read().strip()
            
        if data:
            try:
                Prompt, Status = data.split(",")
                if Status.strip() == "True":
                    log("Generation triggered")
                    GenerateImages(prompt=Prompt.strip())
                    
                    with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                        f.write("False,False")
                    break
            except ValueError:
                log("Invalid data format in ImageGeneration.data")
        
        sleep(1)
            
    except FileNotFoundError:
        log("ImageGeneration.data not found - waiting...")
        sleep(5)
    except Exception as e:
        log(f"Unexpected error: {str(e)}")
        sleep(5)