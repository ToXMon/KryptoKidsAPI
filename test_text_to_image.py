import requests
import json
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
BASE_URL = 'http://localhost:5001'

def test_text_to_image_cartoon():
    """Test text-to-image generation with cartoon style"""
    payload = {
        "name": "Emma",
        "holdjarID": "0xabc123def456",
        "description": "a friendly blue dragon playing with butterflies in a magical forest",
        "style": "cartoon"
    }
    
    response = requests.post(f"{BASE_URL}/api/text-to-image", json=payload)
    print("\n=== Text-to-Image Generation (Cartoon) ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        # Check if images were generated
        if result.get('data') and result.get('data').get('images'):
            print(f"Generated {len(result['data']['images'])} image(s)")
            
            # Save the first image for demonstration purposes
            if len(result['data']['images']) > 0:
                save_generated_image(result['data']['images'][0], "cartoon_dragon.png")
        else:
            print("No images were generated")
    else:
        print(f"Error: {response.text}")

def test_text_to_image_watercolor():
    """Test text-to-image generation with watercolor style"""
    payload = {
        "name": "Jack",
        "holdjarID": "0xdef456abc789",
        "description": "a magical unicorn with rainbow mane running through a meadow of flowers",
        "style": "watercolor"
    }
    
    response = requests.post(f"{BASE_URL}/api/text-to-image", json=payload)
    print("\n=== Text-to-Image Generation (Watercolor) ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        # Check if images were generated
        if result.get('data') and result.get('data').get('images'):
            print(f"Generated {len(result['data']['images'])} image(s)")
            
            # Save the first image for demonstration purposes
            if len(result['data']['images']) > 0:
                save_generated_image(result['data']['images'][0], "watercolor_unicorn.png")
        else:
            print("No images were generated")
    else:
        print(f"Error: {response.text}")

def test_text_to_image_sketch():
    """Test text-to-image generation with sketch style"""
    payload = {
        "name": "Alex",
        "holdjarID": "0xfed789abc123",
        "description": "a space rocket flying to the moon with stars all around",
        "style": "sketch"
    }
    
    response = requests.post(f"{BASE_URL}/api/text-to-image", json=payload)
    print("\n=== Text-to-Image Generation (Sketch) ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        # Check if images were generated
        if result.get('data') and result.get('data').get('images'):
            print(f"Generated {len(result['data']['images'])} image(s)")
            
            # Save the first image for demonstration purposes
            if len(result['data']['images']) > 0:
                save_generated_image(result['data']['images'][0], "sketch_rocket.png")
        else:
            print("No images were generated")
    else:
        print(f"Error: {response.text}")

def test_inappropriate_content_filtering():
    """Test that inappropriate content is filtered and replaced with kid-friendly alternatives"""
    payload = {
        "name": "Test",
        "holdjarID": "0x123test456",
        "description": "a scary monster with a gun fighting in a battle",  # Contains words that should be filtered
        "style": "cartoon"
    }
    
    response = requests.post(f"{BASE_URL}/api/text-to-image", json=payload)
    print("\n=== Text-to-Image with Content Filtering ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        # Check if images were generated
        if result.get('data') and result.get('data').get('images'):
            print(f"Generated {len(result['data']['images'])} image(s)")
            
            # Save the first image for demonstration purposes
            if len(result['data']['images']) > 0:
                save_generated_image(result['data']['images'][0], "filtered_content.png")
        else:
            print("No images were generated")
    else:
        print(f"Error: {response.text}")

def save_generated_image(base64_image, filename):
    """Save a base64 encoded image to file"""
    # Create output directory if it doesn't exist
    output_dir = "generated_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the image
    img_data = base64.b64decode(base64_image)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(img_data)
    
    print(f"Image saved to {filepath}")

if __name__ == "__main__":
    print("KryptoKids Text-to-Image API Test")
    print("Make sure the API server is running before executing these tests.")
    
    try:
        # Test different styles
        test_text_to_image_cartoon()
        test_text_to_image_watercolor()
        test_text_to_image_sketch()
        
        # Test content filtering
        test_inappropriate_content_filtering()
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Make sure the server is running with: python app.py")
