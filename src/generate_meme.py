import requests
import os

def save_meme(template_id, text0, text1=None, output_path=None):
    # Imgflip API endpoint
    url = 'https://api.imgflip.com/caption_image'
    
    # Your credentials from mcp.json
    params = {
        'template_id': template_id,
        'username': os.environ.get('IMGFLIP_USERNAME'),
        'password': os.environ.get('IMGFLIP_PASSWORD'),
        'text0': text0,
    }
    if text1:
        params['text1'] = text1
    
    # Generate meme
    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            # Get the meme URL
            meme_url = data['data']['url']
            
            # Download the image
            img_response = requests.get(meme_url)
            if img_response.status_code == 200:
                # Create outputs directory if it doesn't exist
                if not output_path:
                    output_path = os.path.join('outputs', 'meme.png')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save the image
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"Meme saved to {output_path}")
                return True
    
    print("Failed to generate or download meme")
    return False

if __name__ == "__main__":
    # Save the environment variables vs hardcoding meme
    output_path = os.path.join('outputs', 'env_vars_meme.png')
    save_meme(
        template_id=97984,
        text0="Path 1: Using environment variables in mcp.json",
        text1="Path 2: Just hardcoding the values",
        output_path=output_path
    )
