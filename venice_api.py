import os
import requests
import base64
import random
from io import BytesIO
from dotenv import load_dotenv
try:
    from PIL import Image, ImageStat
except ImportError:
    print("PIL not installed. Image analysis functionality will be limited.")

# Load environment variables
load_dotenv()

# Get API key from environment variables
VENICE_API_KEY = os.getenv('VENICE_API_KEY')

class VeniceAPI:
    """
    Class to interact with Venice AI's image generation API
    """
    API_BASE_URL = "https://api.venice.ai/api/v1"
    
    def __init__(self, api_key=None):
        """
        Initialize the Venice API client
        
        Args:
            api_key (str): Venice API key. If not provided, it will be loaded from environment variables.
        """
        self.api_key = api_key or VENICE_API_KEY
        if not self.api_key:
            raise ValueError("Venice API key not found. Set the VENICE_API_KEY environment variable.")
    
    def generate_image(self, prompt, style='photorealistic', source_image_base64=None, 
                       negative_prompt=None, width=1024, height=1024):
        """
        Generate an image based on the provided prompt and parameters
        
        Args:
            prompt (str): Description of the image to generate
            style (str): Style of the generated image - 'photorealistic' or 'cartoon'
            source_image_base64 (str): Base64 encoded source image (optional)
            negative_prompt (str): What not to include in the image (optional)
            width (int): Width of the generated image
            height (int): Height of the generated image
            
        Returns:
            dict: Response from the Venice API containing the generated image(s)
        """
        # Set the appropriate model and style_preset based on the desired style
        if style.lower() == 'photorealistic':
            model = "fluently-xl"
            style_preset = "Photographic"
        else:  # cartoonish
            model = "fluently-xl"
            style_preset = "Comic"
        
        # Prepare the request payload - keeping it minimal based on our test success
        payload = {
            "model": model,
            "prompt": prompt,
            "height": height,
            "width": width,
            "steps": 30,
            "cfg_scale": 7.5,
            "safe_mode": False,
            "return_binary": False
        }
        
        # Add style preset if needed
        if style_preset:
            payload["style_preset"] = style_preset
        
        # Add optional parameters if provided
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        # Remove inpainting for now as it appears to be causing issues
        # We'll focus on getting the basic text-to-image working first
        # The source image will be used for inspiration in the prompt instead
        
        # Set up the headers with authentication
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Make the API request
        print(f"Making request to Venice API with payload structure: {list(payload.keys())}")
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/image/generate",
                headers=headers,
                json=payload
            )
            
            # Log the response for debugging
            print(f"Venice API Response Status: {response.status_code}")
            print(f"Full response headers: {response.headers}")
            
            # Print full response for debugging
            print(f"Venice API Response: {response.text[:200]}...")
            
            # Raise an exception for failed requests
            if response.status_code != 200:
                error_detail = response.json() if response.text else "No error details provided"
                print(f"Error details: {error_detail}")
                
            response.raise_for_status()
            
            # Return the API response as JSON
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {str(e)}")
            raise
    
    def build_prompt(self, child_name, animal, style='photorealistic'):
        """
        Build a prompt for image generation based on child's drawing metadata
        
        Args:
            child_name (str): Name of the child
            animal (str): Subject of the drawing (e.g., "dog")
            style (str): 'photorealistic' or 'cartoon'
            
        Returns:
            str: Crafted prompt for image generation
        """
        if style.lower() == 'photorealistic':
            return (f"A high-resolution detailed photorealistic image of a {animal}, "
                   f"inspired by a child's drawing made by {child_name}. "
                   f"The {animal} should be in a natural environment, with lifelike features, "
                   f"realistic fur/skin texture, and proper anatomical proportions.")
        else:
            return (f"A cute cartoon illustration of a {animal}, "
                   f"inspired by a child's drawing made by {child_name}. "
                   f"The {animal} should have exaggerated features, bright colors, "
                   f"and a playful expression in a fun, cartoon-style environment.")
    
    def build_kid_friendly_prompt(self, child_name, description, style='cartoon'):
        """
        Build a kid-friendly prompt for text-to-image generation
        with appropriate guardrails and enhancements
        
        Args:
            child_name (str): Name of the child
            description (str): Child's description of what they want to draw
            style (str): 'cartoon', 'watercolor', or 'sketch'
            
        Returns:
            str: Crafted prompt for image generation with appropriate guardrails
        """
        # Apply safety guardrails by ensuring content is kid-friendly
        safety_prefix = "A child-safe, friendly, G-rated illustration suitable for all ages. "
        
        # Check if we need to filter out any problematic content
        filtered_description = self._filter_inappropriate_content(description)
        
        # Style-specific formatting
        if style.lower() == 'cartoon':
            style_suffix = (f"in a cute cartoon style with bright colors, soft shapes, and a cheerful mood. "
                          f"The illustration should look like it belongs in a children's book, "
                          f"with simple but expressive features and a playful atmosphere.")
        elif style.lower() == 'watercolor':
            style_suffix = (f"in a soft watercolor style with gentle colors and dreamy atmosphere. "
                          f"The illustration should have a hand-painted quality with slightly blurred edges, "
                          f"pastel tones, and a magical, serene feeling.")
        elif style.lower() == 'sketch':
            style_suffix = (f"in a pencil sketch style with simple lines and minimal shading. "
                          f"The illustration should look like a child's coloring book page with "
                          f"clear outlines and a hand-drawn quality.")
        else:
            # Default to cartoon style
            style_suffix = "in a cute cartoon style suitable for a children's book."
        
        # Combine elements into final prompt
        final_prompt = (f"{safety_prefix} "
                       f"A delightful illustration of {filtered_description}, "
                       f"created in a style that a child named {child_name} would love, "
                       f"{style_suffix}")
        
        # Add negative prompt elements when returning
        return final_prompt
    
    def _filter_inappropriate_content(self, description):
        """
        Filter out potentially inappropriate content from a child's description
        
        Args:
            description (str): Child's description of what they want to draw
            
        Returns:
            str: Filtered description safe for image generation
        """
        # List of words to replace with more kid-friendly alternatives
        # This is a very basic implementation - in production you'd want a more robust solution
        replacements = {
            "scary": "friendly",
            "frightening": "surprising",
            "violent": "playful",
            "blood": "paint",
            "weapon": "toy",
            "gun": "water pistol",
            "knife": "paintbrush",
            "kill": "tag",
            "dead": "sleeping",
            "death": "nap",
            "hate": "dislike",
            "fight": "dance",
            "monster": "friendly creature",
            "zombie": "sleepy character",
            "devil": "playful character",
            "demon": "magical creature"
        }
        
        # Apply replacements
        filtered = description.lower()
        for bad_word, replacement in replacements.items():
            filtered = filtered.replace(bad_word, replacement)
        
        return filtered
    
    def text_to_image_for_kids(self, child_name, description, style='cartoon',
                            width=1024, height=1024, negative_prompt=None):
        """
        Generate a kid-friendly image from text description
        
        Args:
            child_name (str): Name of the child
            description (str): Child's description of what they want to draw
            style (str): 'cartoon', 'watercolor', or 'sketch'
            width (int): Width of the generated image
            height (int): Height of the generated image
            negative_prompt (str): Optional negative prompt to further guide generation
            
        Returns:
            dict: Response from the Venice API containing the generated image(s)
        """
        # Set the appropriate model and style_preset based on the desired style
        model = "fluently-xl"  # Using the same model as we use for other generation
        
        # For now, let's not use style_preset since we're having issues with the valid values
        style_preset = None
        
        # Build a kid-friendly prompt with guardrails
        prompt = self.build_kid_friendly_prompt(child_name, description, style)
        
        # Default negative prompt if none provided
        if negative_prompt is None:
            negative_prompt = ("photorealistic, realistic, photo, photograph, adult themes, "
                             "scary, frightening, text, words, realistic, detailed facial features, "
                             "complex background, dark themes, violent imagery")
        
        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "height": height,
            "width": width,
            "steps": 30,
            "cfg_scale": 7.5,
            "safe_mode": True,  # Always enable safe mode for kids
            "return_binary": False,
            "negative_prompt": negative_prompt
        }
        
        # Add style preset if needed
        if style_preset:
            payload["style_preset"] = style_preset
        
        # Set up the headers with authentication
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Make the API request
        print(f"Making request to Venice API for kid's text-to-image with payload structure: {list(payload.keys())}")
        print(f"Prompt: {prompt}")
        print(f"Negative prompt: {negative_prompt}")
        
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/image/generate",
                headers=headers,
                json=payload
            )
            
            # Log the response for debugging
            print(f"Venice API Response Status: {response.status_code}")
            
            # Raise an exception for failed requests
            if response.status_code != 200:
                error_detail = response.json() if response.text else "No error details provided"
                print(f"Error details: {error_detail}")
                
            response.raise_for_status()
            
            # Return the API response as JSON
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {str(e)}")
            raise

    def inpaint_image(self, source_image_base64, prompt, object_target, inferred_object=None, 
                     strength=50, model="fluently-xl", width=1024, height=1024):
        """
        Perform inpainting on a source image with a defined mask
        
        Args:
            source_image_base64 (str): Base64 encoded source image to inpaint
            prompt (str): Description of the image (including the changes that will be inpainted)
            object_target (str): Element in the image to inpaint over (used to create the mask)
            inferred_object (str, optional): Content to add via inpainting (replacing object_target)
            strength (int): Strength of the inpainting (0-100)
            model (str): Model to use for inpainting
            width (int): Width of the generated image
            height (int): Height of the generated image
            
        Returns:
            dict: Response from the Venice API containing the inpainted image(s)
        """
        # Validate source image
        if not source_image_base64 or not isinstance(source_image_base64, str):
            raise ValueError("Source image must be provided as a base64 string")
        
        # Ensure source_image_base64 has the proper format prefix if not already present
        if not source_image_base64.startswith('data:image/'):
            image_format = 'png'  # Default format assumption
            source_image_base64 = f"data:image/{image_format};base64,{source_image_base64.split(',')[-1]}"
        
        # Prepare the request payload for inpainting
        payload = {
            "model": model,
            "prompt": prompt,
            "height": height,
            "width": width,
            "steps": 30,
            "cfg_scale": 7.5,
            "safe_mode": False,
            "return_binary": False,
            "inpaint": {
                "strength": strength,
                "source_image_base64": source_image_base64,
                "mask": {
                    "image_prompt": prompt,
                    "object_target": object_target
                }
            }
        }
        
        # Add the inferred object if provided
        if inferred_object:
            payload["inpaint"]["mask"]["inferred_object"] = inferred_object
        
        # Set up the headers with authentication
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Make the API request
        print(f"Making inpainting request to Venice API with payload structure: {list(payload.keys())}")
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/image/generate",
                headers=headers,
                json=payload
            )
            
            # Log the response for debugging
            print(f"Venice API Response Status: {response.status_code}")
            print(f"Full response headers: {response.headers}")
            
            # Print partial response for debugging (to avoid large outputs)
            print(f"Venice API Response: {response.text[:200]}...")
            
            # Raise an exception for failed requests
            if response.status_code != 200:
                error_detail = response.json() if response.text else "No error details provided"
                print(f"Error details: {error_detail}")
                
            response.raise_for_status()
            
            # Return the API response as JSON
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {str(e)}")
            raise

    def analyze_image_for_traits(self, base64_image):
        """
        Analyze a base64 encoded image to extract properties for NFT traits
        
        Args:
            base64_image (str): Base64 encoded image to analyze
            
        Returns:
            dict: Dictionary containing image traits suitable for NFT metadata
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
                
            # Convert base64 to image
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
            
            # Extract image properties
            width, height = image.size
            format_type = image.format
            mode = image.mode
            
            # Calculate color statistics if possible
            color_stats = {}
            dominant_colors = []
            color_diversity = "medium"
            brightness = "medium"
            
            try:
                # Convert to RGB if not already
                if mode != 'RGB':
                    image = image.convert('RGB')
                
                # Get image stats
                stat = ImageStat.Stat(image)
                r, g, b = stat.mean
                
                # Calculate brightness
                brightness_value = (r + g + b) / 3
                if brightness_value < 85:
                    brightness = "dark"
                elif brightness_value > 170:
                    brightness = "bright"
                else:
                    brightness = "medium"
                
                # Determine dominant color palette
                if r > g and r > b:
                    dominant_colors.append("red")
                elif g > r and g > b:
                    dominant_colors.append("green")
                elif b > r and b > g:
                    dominant_colors.append("blue")
                
                if abs(r - g) < 20 and abs(r - b) < 20 and abs(g - b) < 20:
                    dominant_colors.append("balanced")
                
                # Calculate color diversity using standard deviation
                r_std, g_std, b_std = stat.stddev
                color_diversity_value = (r_std + g_std + b_std) / 3
                
                if color_diversity_value < 50:
                    color_diversity = "low"
                elif color_diversity_value > 100:
                    color_diversity = "high"
                else:
                    color_diversity = "medium"
                
                color_stats = {
                    "r_mean": r,
                    "g_mean": g,
                    "b_mean": b,
                    "brightness_value": brightness_value,
                    "color_diversity_value": color_diversity_value
                }
                
            except Exception as e:
                print(f"Error analyzing image colors: {str(e)}")
            
            # Generate randomized trait values for properties that can't be directly extracted
            rarity_values = ["common", "uncommon", "rare", "epic", "legendary"]
            rarity_weights = [50, 30, 15, 4, 1]  # Probability weights
            
            # Generate rarity based on color properties
            if color_diversity == "high" and brightness == "bright":
                rarity_weights = [30, 35, 20, 10, 5]  # Higher chance of better rarity
            elif color_diversity == "low" and brightness == "dark":
                rarity_weights = [60, 25, 10, 4, 1]  # Lower chance of better rarity
            
            # Select rarity based on weighted random choice
            rarity = random.choices(rarity_values, weights=rarity_weights, k=1)[0]
            
            # Compile traits
            traits = {
                "image_properties": {
                    "width": width,
                    "height": height,
                    "format": format_type,
                    "aspect_ratio": round(width / height, 2)
                },
                "color_properties": {
                    "dominant_colors": dominant_colors,
                    "brightness": brightness,
                    "color_diversity": color_diversity
                },
                "nft_traits": {
                    "rarity": rarity,
                    "creativity_score": random.randint(1, 100),
                    "uniqueness_factor": random.randint(1, 100),
                    "magical_power": random.choice(["fire", "water", "earth", "air", "cosmic", "nature", "tech", "rainbow"]),
                    "special_ability": random.choice([
                        "flying", "invisibility", "super speed", "telepathy", 
                        "teleportation", "shape shifting", "healing", "time control"
                    ])
                },
                "metadata": {
                    "timestamp": self._get_current_timestamp(),
                    "generator": "KryptoKids Magic Drawing Creator",
                    "version": "1.0.0"
                }
            }
            
            return traits
            
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            # Return basic traits if analysis fails
            return {
                "nft_traits": {
                    "rarity": random.choice(["common", "uncommon", "rare"]),
                    "creativity_score": random.randint(1, 100),
                    "uniqueness_factor": random.randint(1, 100),
                    "magical_power": random.choice(["fire", "water", "earth", "air", "cosmic"]),
                    "special_ability": random.choice(["flying", "invisibility", "super speed", "healing"])
                },
                "metadata": {
                    "timestamp": self._get_current_timestamp(),
                    "generator": "KryptoKids Magic Drawing Creator",
                    "version": "1.0.0"
                }
            }
    
    def _get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_image_with_metadata(self, base64_image, filename, output_dir="generated_images"):
        """
        Save a base64 encoded image to file and return a URL path
        
        Args:
            base64_image (str): Base64 encoded image to save
            filename (str): Filename to save the image as
            output_dir (str): Directory to save the image in
            
        Returns:
            str: URL path to the saved image
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Remove data URL prefix if present
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        
        # Save the image
        img_data = base64.b64decode(base64_image)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        # Return URL path (relative for now, would be absolute URL in production)
        return f"/{output_dir}/{filename}"
