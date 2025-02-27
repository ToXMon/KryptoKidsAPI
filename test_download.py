import requests
import os

# Create a directory for test images if it doesn't exist
if not os.path.exists('test_images'):
    os.makedirs('test_images')

# Download a sample image for testing
url = 'https://upload.wikimedia.org/wikipedia/commons/e/e1/FullMoon2010.jpg'
response = requests.get(url)

if response.status_code == 200:
    # Save the image
    with open('test_images/sample.jpg', 'wb') as f:
        f.write(response.content)
    print('Sample image downloaded to test_images/sample.jpg')
else:
    print(f'Failed to download sample image: {response.status_code}')
