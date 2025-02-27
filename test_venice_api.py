import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get API key from environment variables
VENICE_API_KEY = os.getenv('VENICE_API_KEY')
API_BASE_URL = "https://api.venice.ai/api/v1"

def test_simple_text_to_image():
    """
    Test a simple text-to-image generation without inpainting
    to see if our basic API integration works
    """
    # Set up the headers with authentication
    headers = {
        'Authorization': f'Bearer {VENICE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Prepare a minimal payload
    payload = {
        "model": "fluently-xl",
        "prompt": "A beautiful sunset over a mountain range",
        "height": 512,
        "width": 512,
        "steps": 30,
        "cfg_scale": 7.5,
        "safe_mode": False,
        "return_binary": False
    }
    
    print("Testing basic Venice API integration...")
    print(f"Using API key: {VENICE_API_KEY[:4]}...{VENICE_API_KEY[-4:]}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make the API request
        response = requests.post(
            f"{API_BASE_URL}/image/generate",
            headers=headers,
            json=payload
        )
        
        # Print response information
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check if response includes any content
        if response.text:
            if response.status_code == 200:
                result = response.json()
                print("Success! Image generated.")
                print(f"Response includes {len(result.get('images', []))} images")
                print(f"Complete metadata: {json.dumps({k:v for k,v in result.items() if k != 'images'}, indent=2)}")
            else:
                # For error responses, print the full content
                print(f"Error response: {response.text}")
        else:
            print("Empty response received")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

def test_child_drawing_transformation():
    """
    Test transforming a child's drawing using the Venice API
    """
    # Set up the headers with authentication
    headers = {
        'Authorization': f'Bearer {VENICE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Create the prompt for a child's drawing
    prompt = "A high-resolution detailed photorealistic image of a cat, inspired by a child's drawing. " \
             "The cat should be in a natural environment, with lifelike features, " \
             "realistic fur texture, and proper anatomical proportions."
    
    # Prepare a minimal payload
    payload = {
        "model": "fluently-xl",
        "prompt": prompt,
        "style_preset": "Photographic",
        "height": 512,
        "width": 512,
        "steps": 30,
        "cfg_scale": 7.5,
        "safe_mode": False,
        "return_binary": False
    }
    
    print("\nTesting child drawing transformation...")
    print(f"Using API key: {VENICE_API_KEY[:4]}...{VENICE_API_KEY[-4:]}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make the API request
        response = requests.post(
            f"{API_BASE_URL}/image/generate",
            headers=headers,
            json=payload
        )
        
        # Print response information
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check if response includes any content
        if response.text:
            if response.status_code == 200:
                result = response.json()
                print("Success! Image generated.")
                print(f"Response includes {len(result.get('images', []))} images")
                print(f"Complete metadata: {json.dumps({k:v for k,v in result.items() if k != 'images'}, indent=2)}")
            else:
                # For error responses, print the full content
                print(f"Error response: {response.text}")
        else:
            print("Empty response received")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    print("Venice API Test")
    test_simple_text_to_image()
    test_child_drawing_transformation()
