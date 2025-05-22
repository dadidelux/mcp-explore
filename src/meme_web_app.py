from flask import Flask, render_template_string, request
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# HTML template with Bootstrap styling
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Meme Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
        .meme-form { max-width: 600px; margin: 0 auto; }
        .meme-preview { margin-top: 20px; text-align: center; }
        .meme-preview img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">Meme Generator</h1>
        
        <div class="meme-form">
            <form method="post">
                <div class="mb-3">
                    <label for="template_id" class="form-label">Choose Template</label>
                    <select name="template_id" id="template_id" class="form-control" required>
                        {% for template in templates %}
                            <option value="{{ template.id }}">{{ template.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="mb-3">
                    <label for="text0" class="form-label">Top Text</label>
                    <input type="text" name="text0" id="text0" class="form-control" required>
                </div>
                
                <div class="mb-3">
                    <label for="text1" class="form-label">Bottom Text</label>
                    <input type="text" name="text1" id="text1" class="form-control">
                </div>
                
                <button type="submit" class="btn btn-primary">Generate Meme</button>
            </form>
        </div>
        
        {% if meme_url %}
            <div class="meme-preview">
                <h2>Your Meme:</h2>
                <img src="{{ meme_url }}" alt="Generated Meme">
                <div class="mt-3">
                    <a href="{{ meme_url }}" class="btn btn-secondary" target="_blank">Open in New Tab</a>
                </div>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

# Available meme templates
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

@app.route('/', methods=['GET', 'POST'])
def index():
    meme_url = None
    if request.method == 'POST':
        template_id = request.form.get('template_id')
        text0 = request.form.get('text0')
        text1 = request.form.get('text1')
        if template_id and text0:
            meme_url = generate_meme(template_id, text0, text1)
    
    return render_template_string(HTML_TEMPLATE, templates=TEMPLATES, meme_url=meme_url)

if __name__ == '__main__':
    print("Meme Generator is running at http://127.0.0.1:5000")
    app.run(debug=True)
