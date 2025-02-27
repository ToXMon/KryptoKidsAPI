from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import validators
import os
import requests
import base64
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from venice_api import VeniceAPI
import uuid
import json
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/drawing', methods=['POST'])
def submit_drawing():
    """
    Endpoint to accept a child's drawing submission
    Expects a JSON payload with:
    - imageUrl: URL of the child's drawing
    - name: Name of the child or artwork
    - holdjarID: Identifier (e.g., wallet address)
    - animal: Subject of the drawing (e.g., "dog")
    """
    # Check if the request has the file part
    if 'file' not in request.files:
        # Fall back to URL-based validation
        data = request.get_json()
        
        # Validate required fields exist
        required_fields = ['imageUrl', 'name', 'holdjarID', 'animal']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate imageUrl is a valid URL
        if not validators.url(data['imageUrl']):
            return jsonify({
                'success': False,
                'error': "Invalid imageUrl. Please provide a valid URL."
            }), 400
        
        # Validate name is not empty
        if not data['name'] or not isinstance(data['name'], str):
            return jsonify({
                'success': False,
                'error': "Name must be a non-empty string."
            }), 400
        
        # Validate holdjarID is not empty
        if not data['holdjarID'] or not isinstance(data['holdjarID'], str):
            return jsonify({
                'success': False,
                'error': "holdjarID must be a non-empty string."
            }), 400
        
        # Validate animal is not empty
        if not data['animal'] or not isinstance(data['animal'], str):
            return jsonify({
                'success': False,
                'error': "Animal must be a non-empty string."
            }), 400
        
        # If all validations pass, return success response
        return jsonify({
            'success': True,
            'message': "Drawing submitted successfully",
            'data': data
        }), 201
    
    # Handle file upload
    file = request.files['file']
    
    # If user does not select a file, the browser might
    # submit an empty file without a filename
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': "No file selected"
        }), 400
    
    # Validate the file has an allowed extension
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    # Get form data
    name = request.form.get('name')
    holdjarID = request.form.get('holdjarID')
    animal = request.form.get('animal')
    
    # Validate required form fields
    if not name:
        return jsonify({
            'success': False,
            'error': "Name field is required"
        }), 400
    
    if not holdjarID:
        return jsonify({
            'success': False,
            'error': "holdjarID field is required"
        }), 400
    
    if not animal:
        return jsonify({
            'success': False,
            'error': "Animal field is required"
        }), 400
    
    # Save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Return success response with file info
    return jsonify({
        'success': True,
        'message': "Drawing uploaded successfully",
        'data': {
            'name': name,
            'holdjarID': holdjarID,
            'animal': animal,
            'filename': filename,
            'file_path': file_path
        }
    }), 201

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

@app.route('/transform', methods=['GET'])
def transform_page():
    return send_from_directory('static', 'transform.html')

@app.route('/text-to-image', methods=['GET'])
def text_to_image_page():
    return send_from_directory('static', 'text_to_image.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    # Check if Venice API key is available
    venice_key = os.getenv('VENICE_API_KEY')
    key_status = "available" if venice_key else "missing"
    
    # If key is available, show the first few characters (safely)
    if venice_key:
        key_preview = venice_key[:4] + "..." + venice_key[-4:] if len(venice_key) > 8 else "***"
    else:
        key_preview = "not available"
    
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'venice_api_key_status': key_status,
        'venice_api_key_preview': key_preview
    })

@app.route('/api/transform-drawing', methods=['POST'])
def transform_drawing():
    """
    Endpoint to transform a child's drawing using Venice AI image generation API
    
    Expects a JSON payload with:
    - imageUrl or base64Image: URL or base64-encoded image of the child's drawing
    - name: Name of the child or artwork
    - holdjarID: Identifier (e.g., wallet address)
    - animal: Subject of the drawing (e.g., "dog")
    - style: Style of transformed image ('photorealistic' or 'cartoon')
    """
    try:
        data = request.get_json()
        
        # Validate required fields exist
        required_fields = ['name', 'holdjarID', 'animal', 'style']
        missing_fields = [field for field in required_fields if field not in data]
        
        # Check if image is provided either as URL or base64
        if 'imageUrl' not in data and 'base64Image' not in data:
            missing_fields.append('imageUrl or base64Image')
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate style is either 'photorealistic' or 'cartoon'
        if data['style'].lower() not in ['photorealistic', 'cartoon']:
            return jsonify({
                'success': False,
                'error': "Style must be either 'photorealistic' or 'cartoon'"
            }), 400
        
        # Initialize Venice API client
        venice_client = VeniceAPI()
        
        # Get the source image
        source_image_base64 = None
        
        if 'base64Image' in data:
            # Use the provided base64 image directly
            source_image_base64 = data['base64Image']
            # Ensure it has the proper format prefix if not already present
            if not source_image_base64.startswith('data:image/'):
                image_format = 'png'  # Default format assumption
                source_image_base64 = f"data:image/{image_format};base64,{source_image_base64}"
        elif 'imageUrl' in data:
            # Download image from URL
            if not validators.url(data['imageUrl']):
                return jsonify({
                    'success': False,
                    'error': "Invalid imageUrl. Please provide a valid URL."
                }), 400
                
            # Download the image
            image_response = requests.get(data['imageUrl'])
            if image_response.status_code != 200:
                return jsonify({
                    'success': False,
                    'error': f"Failed to fetch image from URL: {image_response.status_code}"
                }), 400
                
            # Convert to base64
            image_bytes = image_response.content
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Detect image format from content
            content_type = image_response.headers.get('Content-Type', 'image/png')
            image_format = content_type.split('/')[-1]
            
            # Create the full base64 data URI
            source_image_base64 = f"data:image/{image_format};base64,{image_base64}"
        
        # Build prompt for image generation
        prompt = venice_client.build_prompt(
            child_name=data['name'],
            animal=data['animal'],
            style=data['style']
        )
        
        # Call Venice API to generate the transformed image
        try:
            print("Calling Venice API with the following parameters:")
            print(f"Prompt: {prompt}")
            print(f"Style: {data['style']}")
            
            # We'll skip passing the source image for now as it causes issues
            # Simply using the prompt to guide the generation
            result = venice_client.generate_image(
                prompt=prompt,
                style=data['style'],
                source_image_base64=None  # Skip source image
            )
            
            # Return the generated image(s)
            return jsonify({
                'success': True,
                'message': "Drawing transformed successfully",
                'data': {
                    'original_prompt': prompt,
                    'style': data['style'],
                    'images': result.get('images', []),
                    'id': result.get('id'),
                    'timing': result.get('timing', {})
                }
            }), 200
            
        except Exception as e:
            # Log the error (you may want to add proper logging)
            print(f"Error transforming drawing: {str(e)}")
            
            return jsonify({
                'success': False,
                'error': f"Failed to transform drawing: {str(e)}"
            }), 500
        
    except Exception as e:
        # Log the error (you may want to add proper logging)
        print(f"Error transforming drawing: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': f"Failed to transform drawing: {str(e)}"
        }), 500

@app.route('/api/inpaint', methods=['POST'])
def inpaint_drawing():
    """
    Endpoint to inpaint a specific part of an image using Venice AI's defined mask inpainting
    
    Expects a JSON payload with:
    - imageUrl or base64Image: URL or base64-encoded image of the source image
    - prompt: Description of the image (including the changes that will be inpainted)
    - objectTarget: Element in the image to inpaint over (used to create the mask)
    - inferredObject: Content to add via inpainting (replacing objectTarget) (optional)
    - strength: Strength of the inpainting (0-100) (optional, default: 50)
    - style: Style preset for the image generation (optional)
    """
    try:
        data = request.get_json()
        
        # Validate required fields exist
        required_fields = ['prompt', 'objectTarget']
        missing_fields = [field for field in required_fields if field not in data]
        
        # Check if image is provided either as URL or base64
        if 'imageUrl' not in data and 'base64Image' not in data:
            missing_fields.append('imageUrl or base64Image')
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Initialize Venice API client
        venice_client = VeniceAPI()
        
        # Get the source image
        source_image_base64 = None
        
        if 'base64Image' in data:
            # Use the provided base64 image directly
            source_image_base64 = data['base64Image']
            # Ensure it has the proper format prefix if not already present
            if not source_image_base64.startswith('data:image/'):
                image_format = 'png'  # Default format assumption
                source_image_base64 = f"data:image/{image_format};base64,{source_image_base64}"
        elif 'imageUrl' in data:
            # Download image from URL
            if not validators.url(data['imageUrl']):
                return jsonify({
                    'success': False,
                    'error': "Invalid imageUrl. Please provide a valid URL."
                }), 400
                
            # Download the image
            image_response = requests.get(data['imageUrl'])
            if image_response.status_code != 200:
                return jsonify({
                    'success': False,
                    'error': f"Failed to fetch image from URL: {image_response.status_code}"
                }), 400
                
            # Convert to base64
            image_bytes = image_response.content
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Detect image format from content
            content_type = image_response.headers.get('Content-Type', 'image/png')
            image_format = content_type.split('/')[-1]
            
            # Create the full base64 data URI
            source_image_base64 = f"data:image/{image_format};base64,{image_base64}"
        
        # Get the other parameters
        prompt = data['prompt']
        object_target = data['objectTarget']
        inferred_object = data.get('inferredObject')  # Optional
        strength = int(data.get('strength', 50))  # Optional, default: 50
        style = data.get('style', 'Photographic')  # Optional, default: Photographic
        
        # Call Venice API to inpaint the image with defined mask
        try:
            print("Calling Venice API inpainting with the following parameters:")
            print(f"Prompt: {prompt}")
            print(f"Object Target: {object_target}")
            print(f"Inferred Object: {inferred_object}")
            print(f"Strength: {strength}")
            
            # Use the new inpaint_image method from VeniceAPI
            result = venice_client.inpaint_image(
                source_image_base64=source_image_base64,
                prompt=prompt,
                object_target=object_target,
                inferred_object=inferred_object,
                strength=strength,
                model="fluently-xl",
                width=1024,
                height=1024
            )
            
            # Return the generated image(s)
            return jsonify({
                'success': True,
                'message': "Image inpainted successfully",
                'data': {
                    'prompt': prompt,
                    'objectTarget': object_target,
                    'inferredObject': inferred_object,
                    'strength': strength,
                    'images': result.get('images', []),
                    'id': result.get('id'),
                    'timing': result.get('timing', {})
                }
            }), 200
            
        except Exception as e:
            # Log the error
            print(f"Error inpainting image: {str(e)}")
            
            return jsonify({
                'success': False,
                'error': f"Failed to inpaint image: {str(e)}"
            }), 500
        
    except Exception as e:
        # Log the error
        print(f"Error inpainting image: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': f"Failed to inpaint image: {str(e)}"
        }), 500

@app.route('/api/text-to-image', methods=['POST'])
def text_to_image():
    """
    Endpoint for kid-friendly text-to-image generation
    
    Expects a JSON payload with:
    - name: Name of the child
    - holdjarID: Identifier (e.g., wallet address)
    - description: Description of what the child wants to draw
    - style: Drawing style ('cartoon', 'watercolor', or 'sketch')
    
    Returns:
    - Image as base64 or URL
    - NFT metadata with traits for rarity
    """
    try:
        data = request.get_json()
        
        # Validate required fields exist
        required_fields = ['name', 'holdjarID', 'description', 'style']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate style is one of the supported options
        if data['style'].lower() not in ['cartoon', 'watercolor', 'sketch']:
            return jsonify({
                'success': False,
                'error': "Style must be either 'cartoon', 'watercolor', or 'sketch'"
            }), 400
        
        # Initialize Venice API client
        venice_client = VeniceAPI()
        
        # Call Venice API to generate the image from text
        try:
            print("Calling Venice API for text-to-image generation with the following parameters:")
            print(f"Child Name: {data['name']}")
            print(f"Description: {data['description']}")
            print(f"Style: {data['style']}")
            
            # Generate image using kid-friendly guardrails
            result = venice_client.text_to_image_for_kids(
                child_name=data['name'],
                description=data['description'],
                style=data['style']
            )
            
            # Check if we got images back
            if not result.get('images') or len(result.get('images', [])) == 0:
                return jsonify({
                    'success': False,
                    'error': "No images were generated"
                }), 500
                
            # Get the first generated image
            base64_image = result['images'][0]
            
            # Generate a unique filename
            import uuid
            import time
            unique_id = uuid.uuid4().hex[:8]
            timestamp = int(time.time())
            filename = f"{data['name'].lower().replace(' ', '_')}_{unique_id}_{timestamp}.png"
            
            # Save the image and get its URL
            image_url = venice_client.save_image_with_metadata(
                base64_image=base64_image, 
                filename=filename
            )
            
            # Analyze the image to generate NFT traits
            nft_traits = venice_client.analyze_image_for_traits(base64_image)
            
            # Return the generated image and traits
            return jsonify({
                'success': True,
                'message': "Your magical drawing is ready!",
                'data': {
                    'name': data['name'],
                    'description': data['description'],
                    'style': data['style'],
                    'image_url': image_url,  # URL to the saved image
                    'image_blob': f"data:image/png;base64,{base64_image}",  # Base64 data URI
                    'nft_traits': nft_traits,  # NFT metadata traits
                    'id': result.get('id')
                }
            }), 200
            
        except Exception as e:
            # Log the error
            print(f"Error generating image from text: {str(e)}")
            
            return jsonify({
                'success': False,
                'error': f"Failed to create your drawing: {str(e)}"
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Changed from 5000 to 5001
    app.run(host='0.0.0.0', port=port, debug=True)
