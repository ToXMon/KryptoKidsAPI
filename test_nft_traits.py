import os
import requests
import base64
import json
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load .env file
load_dotenv()

# Import the VeniceAPI class
from venice_api import VeniceAPI

def test_text_to_image_with_nft_traits():
    """Test the text-to-image generation with NFT traits for different children's drawings"""
    
    # Initialize Venice API client
    venice_client = VeniceAPI()
    
    # Test parameters with different themes
    test_cases = [
        {
            "name": "Alex",
            "description": "a magical unicorn in a rainbow forest",
            "style": "cartoon"
        },
        {
            "name": "Sam",
            "description": "a friendly blue dragon flying over a castle",
            "style": "watercolor"
        },
        {
            "name": "Taylor",
            "description": "a superhero cat saving the day in a city",
            "style": "sketch"
        }
    ]
    
    results = []
    
    # Test each case
    for i, test_case in enumerate(test_cases):
        print(f"\n\n===== Testing Case {i+1}: {test_case['name']} - {test_case['description']} =====")
        
        try:
            # Generate image using kid-friendly text-to-image method
            result = venice_client.text_to_image_for_kids(
                child_name=test_case["name"],
                description=test_case["description"],
                style=test_case["style"]
            )
            
            if not result.get('images') or len(result.get('images', [])) == 0:
                print(f"No images were generated for case {i+1}")
                continue
                
            # Get the first generated image
            base64_image = result['images'][0]
            
            # Create a unique filename
            filename = f"{test_case['name'].lower()}_{test_case['style']}.png"
            
            # Save the image
            image_url = venice_client.save_image_with_metadata(
                base64_image=base64_image,
                filename=filename
            )
            
            # Analyze the image to generate NFT traits
            nft_traits = venice_client.analyze_image_for_traits(base64_image)
            
            # Print image URL and traits
            print(f"Image saved at: {image_url}")
            print(f"NFT Traits: {json.dumps(nft_traits, indent=2)}")
            
            # Add to results
            results.append({
                "name": test_case["name"],
                "description": test_case["description"],
                "style": test_case["style"],
                "image_url": image_url,
                "nft_traits": nft_traits
            })
            
            # Show some specific traits
            print(f"\nHighlights:")
            print(f"- Rarity: {nft_traits['nft_traits']['rarity']}")
            print(f"- Magical Power: {nft_traits['nft_traits']['magical_power']}")
            print(f"- Special Ability: {nft_traits['nft_traits']['special_ability']}")
            if 'color_properties' in nft_traits:
                print(f"- Dominant Colors: {', '.join(nft_traits['color_properties'].get('dominant_colors', []))}")
            
        except Exception as e:
            print(f"Error testing case {i+1}: {str(e)}")
    
    # Summary of results
    print("\n\n===== Test Summary =====")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['name']}'s {result['style']} drawing:")
        print(f"   - Rarity: {result['nft_traits']['nft_traits']['rarity']}")
        print(f"   - Magical Power: {result['nft_traits']['nft_traits']['magical_power']}")
    
    return results

if __name__ == "__main__":
    test_text_to_image_with_nft_traits()
