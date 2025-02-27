# KryptoKids API

A simple API for accepting and validating children's drawings for the KryptoKids platform.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Environment Variables (Optional):
Create a `.env` file with the following variables:
```
PORT=5001
VENICE_API_KEY=your_venice_api_key_here
```

Note: The VENICE_API_KEY is required for the /api/transform-drawing endpoint to work. You can obtain an API key from [Venice AI](https://venice.ai/).

## Running the API

```
python app.py
```

The API will be available at http://localhost:5001

## API Endpoints

### POST /api/drawing

Accept a child's drawing submission. This endpoint supports two methods of submission:

#### Method 1: JSON Payload with URL

**Request Body:**
```json
{
  "imageUrl": "https://example.com/image.jpg",
  "name": "My Awesome Dog",
  "holdjarID": "0x123abc...",
  "animal": "dog"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Drawing submitted successfully",
  "data": {
    // Echo of the submitted data
  }
}
```

#### Method 2: File Upload with Form Data

Use a multipart/form-data request to upload a file directly:

**Form Fields:**
- `file`: The image file to upload (supported formats: PNG, JPG, JPEG, GIF)
- `name`: The name of the drawing or child
- `holdjarID`: Identifier (e.g., wallet address)
- `animal`: The subject of the drawing (e.g., "dog")

**Response (Success):**
```json
{
  "success": true,
  "message": "Drawing uploaded successfully",
  "data": {
    "name": "My Awesome Dog",
    "holdjarID": "0x123abc...",
    "animal": "dog",
    "filename": "my_drawing.jpg",
    "file_path": "uploads/my_drawing.jpg"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

### POST /api/transform-drawing

Transform a child's drawing into a new image using Venice's AI image generation API.

**Request Body:**
```json
{
  "imageUrl": "https://example.com/image.jpg",  // Either imageUrl or base64Image is required
  "base64Image": "data:image/png;base64,iVBOR...",  // Alternative to imageUrl
  "name": "Emma",
  "holdjarID": "0x123abc...",
  "animal": "dog",
  "style": "photorealistic"  // Either "photorealistic" or "cartoon"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Drawing transformed successfully",
  "data": {
    "original_prompt": "A high-resolution detailed photorealistic image of a dog...",
    "style": "photorealistic",
    "images": ["base64-encoded-image-data"],
    "id": "generate-image-1234567890",
    "timing": {
      "inferenceDuration": 123,
      "inferencePreprocessingTime": 123,
      "inferenceQueueTime": 123,
      "total": 123
    }
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## Testing

### Option 1: Use the Web Interface
Open a web browser and navigate to http://localhost:5001/. You'll see a form where you can:
1. Choose an image file from your local machine
2. Enter the required metadata (name, holdjarID, animal)
3. Submit the form to upload the drawing

### Option 2: Use the Python Test Scripts

#### Testing with URL Submission
```
python test_api.py
```

#### Testing with File Upload
```
python test_upload.py /path/to/your/image.jpg
```

Replace `/path/to/your/image.jpg` with the path to any image file on your computer (JPG, PNG, or GIF).

### Option 3: Use a Tool Like Postman
If you're familiar with API testing tools like Postman:
1. Create a new POST request to http://localhost:5001/api/drawing
2. Set the request type to "form-data"
3. Add a file field named "file" and select your image
4. Add text fields for "name", "holdjarID", and "animal"
5. Send the request

### Option 4: Use curl for Command Line Testing

#### For URL-based submission:
```bash
curl -X POST http://localhost:5001/api/drawing \
  -H "Content-Type: application/json" \
  -d '{"imageUrl":"https://example.com/image.jpg","name":"Test Drawing","holdjarID":"0x123abc","animal":"dog"}'
```

#### For file upload:
```bash
curl -X POST http://localhost:5001/api/drawing \
  -F "file=@/path/to/your/image.jpg" \
  -F "name=Test Drawing" \
  -F "holdjarID=0x123abc" \
  -F "animal=dog"
```

## How File Uploads Work

When a file is uploaded:
1. The file is sent to the server using multipart/form-data encoding
2. The API validates the file extension and form fields
3. If valid, the file is saved to the "uploads" directory in the project folder
4. The API returns a success response with details about the uploaded file

The uploaded files are stored in the `uploads` directory within the project. You can view them there after uploading.

## Project Structure

```
KryptoKidsAPI/
├── app.py              # Main Flask application
├── requirements.txt    # Dependencies
├── test_api.py         # Test script for URL-based submissions
├── test_upload.py      # Test script for file uploads
├── uploads/            # Directory where uploaded files are stored
└── static/
    └── index.html      # Web interface for testing file uploads
```

## API Status

You can check the API status by making a GET request to `/api/status`:

```
GET http://localhost:5001/api/status
```

**Response:**
```json
{
  "status": "ok",
  "message": "KryptoKids API is running"
}
