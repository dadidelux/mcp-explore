from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
import os
from django.views.decorators.csrf import csrf_exempt

TEMPLATES = [
    {'id': '97984', 'name': 'Disaster Girl'},
    {'id': '112126428', 'name': 'Distracted Boyfriend'},
    {'id': '124822590', 'name': 'Left Exit 12 Off Ramp'},
    {'id': '61579', 'name': 'One Does Not Simply'},
    {'id': '181913649', 'name': 'Drake Hotline Bling'},
]

@csrf_exempt
def generate_meme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            template_id = data.get('template_id')
            text0 = data.get('text0')
            text1 = data.get('text1')

            # Imgflip API endpoint
            url = 'https://api.imgflip.com/caption_image'
            params = {
                'template_id': template_id,
                'username': os.getenv('IMGFLIP_USERNAME'),
                'password': os.getenv('IMGFLIP_PASSWORD'),
                'text0': text0,
                'text1': text1 or ''
            }

            response = requests.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    return JsonResponse({
                        'success': True,
                        'url': data['data']['url']
                    })
            
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate meme'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return render(request, 'meme_generator/index.html', {
        'templates': TEMPLATES
    })
