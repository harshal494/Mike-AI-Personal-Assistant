import pygame
import random 
import asyncio
import edge_tts
import os
import time
from dotenv import dotenv_values

# Initialize pygame mixer with proper settings
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-AriaNeural")

async def TextToAudioFile(text) -> None:
    """Generate speech audio file from text with retry logic"""
    file_path = r"Data\speech.mp3"
    
    # Ensure Data directory exists
    os.makedirs("Data", exist_ok=True)
    
    # Retry mechanism for file access
    for attempt in range(3):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            communicate = edge_tts.Communicate(
                text=text,
                voice=AssistantVoice,
                pitch='+5Hz', 
                rate='+13%'
            )
            await communicate.save(file_path)
            return
        except PermissionError:
            if attempt == 2:
                raise
            time.sleep(0.2)  # Short delay before retry

def TTS(Text, func=lambda r=None: True):
    """Play generated speech audio with proper resource management"""
    try:
        # Generate audio file
        asyncio.run(TextToAudioFile(Text))
        
        # Ensure mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        
        # Load and play with error handling
        for attempt in range(3):
            try:
                pygame.mixer.music.load(r"Data\speech.mp3")
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    if func() == False:
                        pygame.mixer.music.stop()
                        break
                    pygame.time.Clock().tick(10)
                
                # Ensure music system is properly stopped
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                return True
                
            except pygame.error as e:
                if attempt == 2:
                    raise
                time.sleep(0.2)
                pygame.mixer.quit()
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
                
    except Exception as e:
        print(f"TTS Error: {e}")
        return False
    finally:
        try:
            func(False)
        except Exception as e:
            print(f"Callback Error: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    """Handle text processing and TTS playback"""
    if not Text or not isinstance(Text, str):
        return
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    
    sentences = Text.split(".")
    if len(sentences) > 4 and len(Text) >= 250:
        short_version = ". ".join(sentences[:2]) + "."
        TTS(f"{short_version} {random.choice(responses)}", func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    try:
        print("Text-to-Speech System Ready")
        print(f"Using voice: {AssistantVoice}")
        
        while True:
            user_input = input("\nEnter text (or 'quit'): ").strip()
            if user_input.lower() in ('quit', 'exit'):
                break
                
            if user_input:
                TextToSpeech(user_input)
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        pygame.mixer.quit()