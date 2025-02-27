import requests
import json
import base64
import os

# API endpoint
BASE_URL = 'http://localhost:5001'

def test_submit_drawing_valid():
    """Test submitting a valid drawing"""
    payload = {
        "imageUrl": "https://www.publicdomainpictures.net/pictures/490000/velka/kids-drawing.jpg",
        "name": "Fluffy the Cat",
        "holdjarID": "0xabc123def456",
        "animal": "cat"
    }
    
    response = requests.post(f"{BASE_URL}/api/drawing", json=payload)
    print("\n=== Valid Drawing Submission ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_submit_drawing_invalid():
    """Test submitting an invalid drawing (missing fields)"""
    payload = {
        "imageUrl": "https://www.publicdomainpictures.net/pictures/490000/velka/kids-drawing.jpg",
        # Missing name field
        "holdjarID": "0xabc123def456",
        "animal": "cat"
    }
    
    response = requests.post(f"{BASE_URL}/api/drawing", json=payload)
    print("\n=== Invalid Drawing Submission (Missing Field) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_submit_drawing_invalid_url():
    """Test submitting an invalid URL"""
    payload = {
        "imageUrl": "not-a-valid-url",
        "name": "Fluffy the Cat",
        "holdjarID": "0xabc123def456",
        "animal": "cat"
    }
    
    response = requests.post(f"{BASE_URL}/api/drawing", json=payload)
    print("\n=== Invalid Drawing Submission (Invalid URL) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_transform_drawing_photorealistic():
    """Test transforming a drawing to photorealistic style using base64 image"""
    # Create a simple base64 image (a 1x1 transparent pixel)
    simple_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    
    payload = {
        "base64Image": f"data:image/png;base64,{simple_base64}",
        "name": "Emma",
        "holdjarID": "0xdef456abc789",
        "animal": "cat",
        "style": "photorealistic" 
    }
    
    response = requests.post(f"{BASE_URL}/api/transform-drawing", json=payload)
    print("\n=== Transform Drawing (Photorealistic) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_transform_drawing_cartoon():
    """Test transforming a drawing to cartoon style using base64 image"""
    # Create a simple base64 image (a 1x1 transparent pixel)
    simple_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    
    payload = {
        "base64Image": f"data:image/png;base64,{simple_base64}",
        "name": "Jack",
        "holdjarID": "0xabc789def123",
        "animal": "cat",
        "style": "cartoon" 
    }
    
    response = requests.post(f"{BASE_URL}/api/transform-drawing", json=payload)
    print("\n=== Transform Drawing (Cartoon) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("KryptoKids API Test")
    print("Make sure the API server is running before executing these tests.")
    
    # Test the API endpoints
    try:
        # Original endpoints
        test_submit_drawing_valid()
        test_submit_drawing_invalid()
        test_submit_drawing_invalid_url()
        
        # New transform-drawing endpoint
        test_transform_drawing_photorealistic()
        test_transform_drawing_cartoon()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Make sure the server is running with: python app.py")
