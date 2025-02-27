#!/usr/bin/env python3
"""
Script to generate a repeatable test payload for the Venice API inpainting feature.
This creates a simple, consistent payload that can be shared with the Venice API support team.
"""
import os
import json
import base64
from PIL import Image
from io import BytesIO

def create_simple_test_image():
    """Create a very simple test image - a white background with a black circle"""
    # Create a white background
    img = Image.new('RGB', (512, 512), color='white')
    
    # Create a simple shape - a black circle
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse((156, 156, 356, 356), fill='black')
    
    # Save to BytesIO
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_byte_data = buffered.getvalue()
    
    # Encode to base64
    base64_encoded = base64.b64encode(img_byte_data).decode('utf-8')
    return f"data:image/png;base64,{base64_encoded}"

def create_test_payload():
    """Create a test payload for the Venice API inpainting feature"""
    # Generate or load a test image
    use_generated = input("Generate a simple test image? (y/n, default: y): ").lower() != 'n'
    
    if use_generated:
        print("Generating a simple test image (white background with black circle)...")
        image_base64 = create_simple_test_image()
    else:
        # Load from file
        image_path = input("Enter path to test image: ")
        if not os.path.exists(image_path):
            print(f"Error: File not found: {image_path}")
            return
        
        # Load and convert the image
        with Image.open(image_path) as img:
            # Resize if needed
            if img.width > 512 or img.height > 512:
                img = img.resize((512, 512), Image.LANCZOS)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to BytesIO
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_byte_data = buffered.getvalue()
            
            # Encode to base64
            base64_encoded = base64.b64encode(img_byte_data).decode('utf-8')
            image_base64 = f"data:image/png;base64,{base64_encoded}"
    
    # Create the payload
    payload = {
        "model": "fluently-xl",
        "prompt": "A detailed photograph of a circle transformed into a smiling face",
        "height": 512,
        "width": 512,
        "steps": 30,
        "cfg_scale": 7.5,
        "safe_mode": False,
        "return_binary": False,
        "inpaint": {
            "strength": 80,
            "source_image_base64": image_base64,
            "mask": {
                "image_prompt": "A detailed photograph of a circle transformed into a smiling face",
                "object_target": "circle", 
                "inferred_object": "smiling face"
            }
        }
    }
    
    # Save to file
    output_file = "venice_test_payload.json"
    with open(output_file, 'w') as f:
        # Save without the actual base64 data to keep file small
        display_payload = payload.copy()
        display_payload["inpaint"]["source_image_base64"] = "BASE64_STRING_REMOVED_FOR_BREVITY"
        json.dump(display_payload, f, indent=2)
    
    # Also save full payload
    with open("venice_test_payload_full.json", 'w') as f:
        json.dump(payload, f, indent=2)
    
    print(f"\nTest payload saved to {output_file}")
    print(f"Full payload (including base64 image) saved to venice_test_payload_full.json")
    
    # Print curl command for easy testing
    api_key = os.getenv('VENICE_API_KEY', 'YOUR_API_KEY')
    print("\nCURL command for testing:")
    print(f"""
curl -X POST \\
  https://api.venice.ai/api/v1/image/generate \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d @venice_test_payload_full.json
""")
    
    return payload

if __name__ == "__main__":
    create_test_payload()
