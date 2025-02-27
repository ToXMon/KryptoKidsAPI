import requests
import os
import sys

# API endpoint
BASE_URL = 'http://localhost:5001'

def test_file_upload(file_path):
    """
    Test uploading a local file to the API
    
    Args:
        file_path (str): Path to the local image file to upload
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
        
    # Check if file is an allowed extension
    allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        print(f"Error: File type not allowed. Must be one of: {', '.join(allowed_extensions)}")
        return
    
    # Prepare the multipart/form-data request
    url = f"{BASE_URL}/api/drawing"
    
    # Prepare form data
    form_data = {
        'name': 'Test Drawing',
        'holdjarID': '0xabc123def456',
        'animal': 'dog'
    }
    
    # Prepare the file
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'), f'image/{file_extension}')
    }
    
    # Send the POST request
    try:
        response = requests.post(url, data=form_data, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending request: {e}")
    finally:
        # Close the file
        files['file'][1].close()

if __name__ == "__main__":
    # Check if a file path was provided
    if len(sys.argv) < 2:
        print("Usage: python test_upload.py <path_to_image_file>")
        print("Example: python test_upload.py ./my_drawing.jpg")
        sys.exit(1)
    
    # Use the provided file path
    file_path = sys.argv[1]
    test_file_upload(file_path)
