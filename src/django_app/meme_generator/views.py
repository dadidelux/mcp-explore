from django.shortcuts import render
from django.http import HttpResponse
import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TEMPLATES = [
    {'id': '97984', 'name': 'Disaster Girl'},
    {'id': '112126428', 'name': 'Distracted Boyfriend'},
    {'id': '124822590', 'name': 'Left Exit 12 Off Ramp'},
    {'id': '61579', 'name': 'One Does Not Simply'},
    {'id': '181913649', 'name': 'Drake Hotline Bling'},
]

def generate_meme(template_id, text0, text1=None):
    url = 'https://api.imgflip.com/caption_image'
    params = {
        'template_id': template_id,
        'username': os.getenv('IMGFLIP_USERNAME'),
        'password': os.getenv('IMGFLIP_PASSWORD'),
        'text0': text0,
    }
    if text1:
        params['text1'] = text1
    
    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            return data['data']['url']
    return None

def index(request):
    meme_url = None
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        text0 = request.POST.get('text0')
        text1 = request.POST.get('text1')
        if template_id and text0:
            meme_url = generate_meme(template_id, text0, text1)
    
    return render(request, 'meme_generator/index.html', {
        'templates': TEMPLATES,
        'meme_url': meme_url
    })
