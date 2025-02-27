import os
import base64
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from venice_api import VeniceAPI

# Load environment variables
load_dotenv()

# Get API key from environment variables
VENICE_API_KEY = os.getenv('VENICE_API_KEY')
API_BASE_URL = "https://api.venice.ai/api/v1"

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
        
        # Resize the image if it's too large (Venice may have size limits)
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

def save_base64_image(base64_image, output_dir="output_images", prefix="transformed"):
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

def test_inpainting_with_file(image_path, prompt, style="Photographic"):
    """
    Test inpainting with a source image file
    """
    try:
        # Convert image to base64
        source_image_base64 = load_image_as_base64(image_path)
        
        # Print info about the base64 string (length, prefix)
        print(f"Base64 image string length: {len(source_image_base64)}")
        print(f"Base64 image string prefix: {source_image_base64[:50]}...")
        
        # Set up the headers with authentication
        headers = {
            'Authorization': f'Bearer {VENICE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Prepare the payload with inpainting
        payload = {
            "model": "fluently-xl",
            "prompt": prompt,
            "style_preset": style,
            "height": 512,
            "width": 512,
            "steps": 30,
            "cfg_scale": 7.5,
            "safe_mode": False,
            "return_binary": False,
            "inpaint": {
                "strength": 80,  # Higher strength for more transformation
                "source_image_base64": source_image_base64
            }
        }
        
        print(f"Making request to Venice API with inpainting...")
        print(f"Prompt: {prompt}")
        print(f"Style: {style}")
        
        # Make the API request
        response = requests.post(
            f"{API_BASE_URL}/image/generate",
            headers=headers,
            json=payload
        )
        
        # Print response info
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check if response includes any content
        if response.text:
            try:
                result = response.json()
                if response.status_code == 200:
                    print("Success! Image transformed.")
                    if "images" in result and result["images"]:
                        print(f"Response includes {len(result['images'])} images")
                        
                        # Create a folder for output
                        output_dir = "output_images"
                        
                        # Save all generated images
                        for i, img_base64 in enumerate(result["images"]):
                            # Get original filename without extension
                            original_name = os.path.splitext(os.path.basename(image_path))[0]
                            
                            # Save the image
                            output_path = save_base64_image(
                                img_base64, 
                                output_dir=output_dir, 
                                prefix=f"{original_name}_transformed_{i+1}"
                            )
                        
                        print(f"All images saved to {output_dir}/ directory")
                    
                    # Save the original image too for comparison
                    original_img_path = save_base64_image(
                        source_image_base64,
                        output_dir="output_images",
                        prefix="original"
                    )
                    
                    # Save the metadata for inspection
                    print(f"Response metadata: {result.keys()}")
                else:
                    # For error responses, print content for debugging
                    print(f"Error response: {response.text}")
            except Exception as e:
                print(f"Error parsing response: {str(e)}")
                print(f"Raw response: {response.text[:100]}...")
        else:
            print("Empty response received")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

def test_inpainting_with_defined_mask(image_path, prompt, object_target, inferred_object=None, style="Photographic"):
    """
    Test inpainting with a defined mask using the VeniceAPI class
    
    Args:
        image_path (str): Path to the source image file
        prompt (str): Description of the image (including the changes that will be inpainted)
        object_target (str): Element in the image to inpaint over (used to create the mask)
        inferred_object (str, optional): Content to add via inpainting (replacing object_target)
        style (str): Style preset for the image generation
    """
    try:
        # Convert image to base64
        source_image_base64 = load_image_as_base64(image_path)
        
        # Print info about the base64 string (length, prefix)
        print(f"Base64 image string length: {len(source_image_base64)}")
        print(f"Base64 image string prefix: {source_image_base64[:50]}...")
        
        # Initialize VeniceAPI client
        venice_client = VeniceAPI()
        
        # Configure style for model selection if needed
        model = "fluently-xl"
        
        print(f"Making inpainting request with defined mask...")
        print(f"Prompt: {prompt}")
        print(f"Object Target: {object_target}")
        print(f"Inferred Object: {inferred_object}")
        print(f"Style: {style}")
        
        # Call the new inpaint_image method
        result = venice_client.inpaint_image(
            source_image_base64=source_image_base64,
            prompt=prompt,
            object_target=object_target,
            inferred_object=inferred_object,
            strength=80,  # Higher strength for more transformation
            model=model,
            width=512,
            height=512
        )
        
        # Process and save results
        if "images" in result and result["images"]:
            print("Success! Image transformed.")
            print(f"Response includes {len(result['images'])} images")
            
            # Create a folder for output
            output_dir = "output_images"
            
            # Save all generated images
            for i, img_base64 in enumerate(result["images"]):
                # Get original filename without extension
                original_name = os.path.splitext(os.path.basename(image_path))[0]
                
                # Save the image
                output_path = save_base64_image(
                    img_base64, 
                    output_dir=output_dir, 
                    prefix=f"{original_name}_mask_inpainted_{i+1}"
                )
            
            # Save the original image too for comparison
            original_img_path = save_base64_image(
                source_image_base64,
                output_dir="output_images",
                prefix="original"
            )
            
            print(f"All images saved to {output_dir}/ directory")
            print(f"Response metadata: {result.keys()}")
        else:
            print(f"No images returned in the response. Response keys: {result.keys()}")
            
    except Exception as e:
        print(f"Exception in defined mask inpainting: {str(e)}")

def test_simple_generation(prompt, style="Photographic"):
    """
    Test simple text-to-image generation (without inpainting)
    as a fallback to compare results
    """
    try:
        # Set up the headers with authentication
        headers = {
            'Authorization': f'Bearer {VENICE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Prepare a minimal payload without inpainting
        payload = {
            "model": "fluently-xl",
            "prompt": prompt,
            "style_preset": style,
            "height": 512,
            "width": 512,
            "steps": 30,
            "cfg_scale": 7.5,
            "safe_mode": False,
            "return_binary": False
        }
        
        print(f"\nRunning simple text-to-image generation for comparison...")
        print(f"Prompt: {prompt}")
        print(f"Style: {style}")
        
        # Make the API request
        response = requests.post(
            f"{API_BASE_URL}/image/generate",
            headers=headers,
            json=payload
        )
        
        # Print response info
        print(f"Response status code: {response.status_code}")
        
        # Check if response includes any content
        if response.text and response.status_code == 200:
            result = response.json()
            print("Success! Image generated.")
            
            if "images" in result and result["images"]:
                # Save all generated images
                output_dir = "output_images"
                for i, img_base64 in enumerate(result["images"]):
                    output_path = save_base64_image(
                        img_base64, 
                        output_dir=output_dir, 
                        prefix=f"simple_generation_{i+1}"
                    )
                print(f"Simple generation images saved to {output_dir}/ directory")
        else:
            print(f"Error response: {response.text[:200]}..." if response.text else "Empty response")
            
    except Exception as e:
        print(f"Exception occurred in simple generation: {str(e)}")

if __name__ == "__main__":
    # Ask the user for the image path
    print("Venice Inpainting Test")
    
    # Default test image path
    default_image = "test_images/sample.jpg"
    
    # Either provide the direct path or allow user to enter it
    image_path = input(f"Enter the path to the image file (press enter for default: {default_image}): ") or default_image
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        exit(1)
    
    # Ask for the prompt
    prompt = input("Enter the prompt for transformation (or press enter for default): ") or \
             "A high-resolution detailed photorealistic image of a cat, inspired by a child's drawing"
    
    # Ask for the object target for defined mask inpainting
    object_target = input("Enter the object target to inpaint (e.g., 'cat's face', or press enter for default): ") or "cat's face"
    
    # Ask for the inferred object (what to replace it with)
    inferred_object = input("Enter what to replace it with (optional, press enter to skip): ") or None
    
    # Ask for the style
    style = input("Enter the style (Photographic or Comic, press enter for default): ") or "Photographic"
    
    # Test inpainting options
    test_option = input("Select test option (1 for original inpainting, 2 for defined mask inpainting, 3 for both, press enter for default): ") or "3"
    
    if test_option in ["1", "3"]:
        # Test original inpainting
        print("\n=== Testing original inpainting with source image ===")
        test_inpainting_with_file(image_path, prompt, style)
    
    if test_option in ["2", "3"]:
        # Test defined mask inpainting
        print("\n=== Testing inpainting with defined mask ===")
        test_inpainting_with_defined_mask(image_path, prompt, object_target, inferred_object, style)
    
    # Test simple generation (fallback)
    test_simple = input("Do you want to test simple generation without inpainting? (y/n, press enter for default): ") or "y"
    if test_simple.lower() == "y":
        print("\n=== Testing simple text-to-image generation ===")
        test_simple_generation(prompt, style)
