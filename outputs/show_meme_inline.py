import requests
from IPython.display import Image, display
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Imgflip API endpoint
url = 'https://api.imgflip.com/caption_image'

# Meme template and text
params = {
    'template_id': '112126428',  # Distracted Boyfriend
    'username': os.getenv('IMGFLIP_USERNAME', ''),
    'password': os.getenv('IMGFLIP_PASSWORD', ''),
    'text0': 'Tried using env vars in mcp.json',
    'text1': 'Ended up hardcoding values so everything works'
}

response = requests.post(url, params=params)
data = response.json()

if data['success']:
    meme_url = data['data']['url']
    display(Image(url=meme_url))
else:
    print('Failed to generate meme:', data['error_message'])
