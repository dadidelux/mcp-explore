from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
import os
from django.views.decorators.csrf import csrf_exempt
import random
from .gemini_meme_client import GeminiMemeGenerator

# Initialize the Gemini-powered meme generator
meme_generator = GeminiMemeGenerator()

def get_all_meme_templates():
    try:
        response = requests.get('https://api.imgflip.com/get_memes')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']['memes']
    except Exception as e:
        print(f"Error fetching meme templates: {e}")
    return []

def select_meme_template(prompt):
    """Select an appropriate meme template based on the prompt"""
    templates = get_all_meme_templates()
    
    # Keywords to help match templates with prompts
    template_keywords = {
        '181913649': ['choice', 'prefer', 'better', 'drake', 'like', 'dislike'],  # Drake
        '112126428': ['distract', 'tempt', 'attract', 'alternative'],  # Distracted Boyfriend
        '97984': ['disaster', 'evil', 'problem', 'chaos'],  # Disaster Girl
        '124822590': ['choice', 'exit', 'decision', 'turn', 'path'],  # Left Exit
        '61579': ['obvious', 'simple', 'warning', 'stark'],  # One Does Not Simply
    }
    
    # Default to Drake template if no good match
    best_template = next((t for t in templates if t['id'] == '181913649'), templates[0])
    max_matches = 0
    
    prompt_lower = prompt.lower()
    for template in templates:
        if template['id'] in template_keywords:
            matches = sum(1 for keyword in template_keywords[template['id']] 
                        if keyword in prompt_lower)
            if matches > max_matches:
                max_matches = matches
                best_template = template
    
    return best_template

def generate_meme_text(prompt):
    """Generate top and bottom text for the meme based on the prompt"""
    # Simple text generation rules based on common meme formats
    prompt_lower = prompt.lower()
    
    if 'versus' in prompt_lower or ' vs ' in prompt_lower:
        parts = prompt_lower.replace('versus', 'vs').split('vs')
        return parts[0].strip(), parts[1].strip()
    
    if '?' in prompt:
        return "Me wondering", prompt.strip('?')
    
    if 'when' in prompt_lower:
        return "When " + prompt.lower().split('when')[1].strip(), "😂"
    
    if 'what if' in prompt_lower:
        return "What if", prompt.lower().split('what if')[1].strip()
    
    # Default format: split into two parts
    words = prompt.split()
    mid = len(words) // 2
    return ' '.join(words[:mid]), ' '.join(words[mid:])

@csrf_exempt
def get_templates(request):
    templates = get_all_meme_templates()
    return JsonResponse({'success': True, 'templates': templates})

@csrf_exempt
def generate_meme(request):
    templates = get_all_meme_templates()
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON requests
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                template_id = data.get('template_id')
                text0 = data.get('text0')
                text1 = data.get('text1')
            else:
                template_id = request.POST.get('template_id')
                text0 = request.POST.get('text0')
                text1 = request.POST.get('text1')

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
                    meme_url = data['data']['url']
                    # Return JSON response for API requests
                    if request.content_type == 'application/json':
                        return JsonResponse({
                            'success': True,
                            'url': meme_url
                        })
                    # Return rendered template for form submissions
                    return render(request, 'meme_generator/index.html', {
                        'templates': templates,
                        'meme_url': meme_url
                    })
            
            error_msg = 'Failed to generate meme'
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': error_msg})
            return render(request, 'meme_generator/index.html', {
                'templates': templates,
                'error': error_msg
            })
                
        except Exception as e:
            error_msg = str(e)
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': error_msg})
            return render(request, 'meme_generator/index.html', {
                'templates': templates,
                'error': error_msg
            })
    
    # GET request - show the form with templates
    return render(request, 'meme_generator/index.html', {
        'templates': templates
    })

@csrf_exempt
def ai_generate_meme(request):
    """Generate a meme using AI-based text and template selection with Gemini"""
    if request.method == 'POST':
        try:
            # Get the prompt from form or JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                prompt = data.get('prompt', '')
            else:
                prompt = request.POST.get('prompt', '')
            
            if not prompt:
                raise ValueError("Prompt is required")
            
            # Get meme context using Gemini
            meme_context = meme_generator.generate_meme_context(prompt)
            
            # Generate meme using Imgflip API
            url = 'https://api.imgflip.com/caption_image'
            params = {
                'template_id': meme_context.template_id,
                'username': os.getenv('IMGFLIP_USERNAME'),
                'password': os.getenv('IMGFLIP_PASSWORD'),
                'text0': meme_context.text0,
            }
            if meme_context.text1:
                params['text1'] = meme_context.text1
            
            response = requests.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    meme_url = data['data']['url']
                      # Get the template name for display
                    templates = get_all_meme_templates()
                    template = next((t for t in templates if t['id'] == meme_context.template_id), None)
                    
                    if request.content_type == 'application/json':
                        return JsonResponse({
                            'success': True,
                            'url': meme_url,
                            'template': template['name'] if template else 'Unknown',
                            'text0': meme_context.text0,
                            'text1': meme_context.text1
                        })
                    
                    return render(request, 'meme_generator/index.html', {
                        'templates': get_all_meme_templates(),
                        'meme_url': meme_url,
                        'selected_template': template,
                        'text0': meme_context.text0,
                        'text1': meme_context.text1,
                        'prompt': prompt
                    })
            
            error_msg = 'Failed to generate meme'
            
        except Exception as e:
            error_msg = str(e)
            
        if request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': error_msg})
        return render(request, 'meme_generator/index.html', {
            'templates': get_all_meme_templates(),
            'error': error_msg
        })
    
    # GET request - show the form
    return render(request, 'meme_generator/index.html', {
        'templates': get_all_meme_templates()
    })

@csrf_exempt
def health_check(request):
    """
    Health check endpoint for monitoring and Docker health checks
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'meme-generator',
        'mode': 'development' if os.getenv('DEBUG') == '1' else 'production'
    })
