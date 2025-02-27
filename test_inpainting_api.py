#!/usr/bin/env python3
"""
Test script for the inpainting API endpoint
"""
import requests
import json
import base64
import os
from PIL import Image
from io import BytesIO

# API endpoint
BASE_URL = 'http://localhost:5001'

def load_image_as_base64(file_path):
    """
    Load an image from disk and convert to base64 with proper format prefix
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
    
    # Determine the MIME type based on file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    mime_type = 'image/jpeg' if file_ext in ['.jpg', '.jpeg'] else 'image/png'
    
    # Open and read the image file
    with Image.open(file_path) as img:
        # For more reliable compatibility, convert to RGB and to PNG format
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize the image if it's too large
        max_size = 1024
        if img.width > max_size or img.height > max_size:
            # Maintain aspect ratio
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Save to BytesIO instead of file
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_byte_data = buffered.getvalue()
    
    # Encode to base64
    base64_encoded = base64.b64encode(img_byte_data).decode('utf-8')
    
    # Return with proper data URI format
    return f"data:{mime_type};base64,{base64_encoded}"

def save_base64_image(base64_image, output_dir="output_images", prefix="inpainted"):
    """
    Save a base64 encoded image to a file
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    output_path = os.path.join(output_dir, filename)
    
    # Remove data URI prefix if present
    if ";" in base64_image and "," in base64_image:
        # Format is like "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
        base64_data = base64_image.split(",")[1]
    else:
        base64_data = base64_image
    
    # Decode base64 data
    image_data = base64.b64decode(base64_data)
    
    # Write to file
    with open(output_path, "wb") as f:
        f.write(image_data)
    
    print(f"Image saved to: {output_path}")
    return output_path

def test_inpaint_api_with_base64(image_path):
    """Test the inpainting API endpoint with a base64 encoded image"""
    # Load image as base64
    image_base64 = load_image_as_base64(image_path)
    print(f"Image loaded, base64 length: {len(image_base64)}")
    
    # Prepare the request payload
    payload = {
        "base64Image": image_base64,
        "prompt": "A cute cartoon cat with blue eyes and a pink nose",
        "objectTarget": "cat's face",
        "inferredObject": "cat's face with blue eyes and a pink nose",
        "strength": 75
    }
    
    # Send the request to the API
    print("Sending request to inpainting API endpoint...")
    response = requests.post(f"{BASE_URL}/api/inpaint", json=payload)
    
    # Print the response status and headers
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    # Process the response
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Success! Response: {result['message']}")
            
            # Save the inpainted images if any
            if 'data' in result and 'images' in result['data'] and result['data']['images']:
                images = result['data']['images']
                print(f"Received {len(images)} inpainted images")
                
                # Save each image
                for i, img_base64 in enumerate(images):
                    output_path = save_base64_image(
                        img_base64,
                        prefix=f"api_inpainted_{i+1}"
                    )
                
                # Save the original image for comparison
                save_base64_image(
                    image_base64,
                    prefix="api_original"
                )
                
                print("All images saved to the output_images directory")
            else:
                print("No images found in the response")
                print(f"Response data keys: {result.get('data', {}).keys()}")
        except Exception as e:
            print(f"Error processing response: {e}")
            print(f"Raw response: {response.text[:500]}...")
    else:
        print(f"Error: {response.status_code}")
        try:
            print(f"Error details: {response.json()}")
        except:
            print(f"Raw error response: {response.text}")

def test_inpaint_api_with_url():
    """Test the inpainting API endpoint with an image URL"""
    # Image URL - you can use any publicly accessible image
    image_url = "https://example.com/path/to/cat_image.jpg"
    
    # Prepare the request payload
    payload = {
        "imageUrl": image_url,
        "prompt": "A cute cartoon cat with blue eyes and a pink nose",
        "objectTarget": "cat's face",
        "inferredObject": "cat's face with blue eyes and a pink nose",
        "strength": 75
    }
    
    # Send the request to the API
    print("Sending request to inpainting API endpoint with URL...")
    response = requests.post(f"{BASE_URL}/api/inpaint", json=payload)
    
    # Print the response status and headers
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    # Process the response (similar to the base64 version)
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Success! Response: {result['message']}")
            
            # Save the inpainted images if any
            if 'data' in result and 'images' in result['data'] and result['data']['images']:
                images = result['data']['images']
                print(f"Received {len(images)} inpainted images")
                
                # Save each image
                for i, img_base64 in enumerate(images):
                    output_path = save_base64_image(
                        img_base64,
                        prefix=f"api_url_inpainted_{i+1}"
                    )
                
                print("All images saved to the output_images directory")
            else:
                print("No images found in the response")
                print(f"Response data keys: {result.get('data', {}).keys()}")
        except Exception as e:
            print(f"Error processing response: {e}")
            print(f"Raw response: {response.text[:500]}...")
    else:
        print(f"Error: {response.status_code}")
        try:
            print(f"Error details: {response.json()}")
        except:
            print(f"Raw error response: {response.text}")

if __name__ == "__main__":
    # Check if the API server is running
    try:
        # Simple check if the server is up
        health_check = requests.get(f"{BASE_URL}/api/status")
        if health_check.status_code == 200:
            print("API server is running")
        else:
            print(f"API server returned unexpected status: {health_check.status_code}")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running with: python app.py")
        exit(1)
    
    # Ask for image path
    default_image = "test_images/sample.jpg"
    image_path = input(f"Enter the path to the image file (press enter for default: {default_image}): ") or default_image
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        exit(1)
    
    # Run the tests
    print("\n=== Testing inpainting API with base64 image ===")
    test_inpaint_api_with_base64(image_path)
    
    # Ask if user wants to test with URL
    test_url = input("\nDo you want to test with image URL? (This requires a valid public image URL) (y/n): ")
    if test_url.lower() == "y":
        print("\n=== Testing inpainting API with image URL ===")
        test_inpaint_api_with_url()
