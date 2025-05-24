import os
import json
import requests
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_MODEL_API', 'AIzaSyDmrKg1JyD1DLZFkv6LurlY8jizYUGQvi8'))

@dataclass
class MemeContext:
    """Class to hold meme generation context"""
    template_id: str
    text0: str
    text1: str = None

class GeminiMemeGenerator:
    def __init__(self):
        """Initialize the Gemini model and fetch available templates"""
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.templates = self._fetch_templates()
        # Create template map for quick lookups
        self.template_map = {
            template['name']: template['id'] 
            for template in self.templates
        } if self.templates else {
            'Drake': '181913649',
            'Distracted Boyfriend': '112126428',
            'Disaster Girl': '97984',
            'Left Exit': '124822590',
            'One Does Not Simply': '61579'
        }
    
    def _fetch_templates(self) -> list:
        """Fetch available meme templates from Imgflip API"""
        try:
            response = requests.get('https://api.imgflip.com/get_memes')
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    return data['data']['memes']
        except Exception as e:
            print(f"Error fetching meme templates: {e}")
        return []

    def _get_template_description(self, template_name: str) -> str:
        """Get a description for a template based on its common use cases"""
        descriptions = {
            'Drake': 'for preferences, comparisons, or choosing between options',
            'Distracted Boyfriend': 'for showing temptation or being distracted by alternatives',
            'Disaster Girl': 'for evil plans, chaos, or mischievous situations',
            'Left Exit': 'for sudden decisions, choosing between right and wrong',
            'One Does Not Simply': 'for pointing out difficult or complicated tasks',
            'Change My Mind': 'for controversial or debatable statements',
            'Two Buttons': 'for difficult choices or dilemmas',
            'This Is Fine': 'for ignoring obvious problems',
            'Expanding Brain': 'for increasingly complex or absurd ideas',
            'Woman Yelling at Cat': 'for absurd misunderstandings or conflicts'
        }
        return descriptions.get(template_name, 'versatile template for various situations')

    def generate_meme_context(self, prompt: str) -> Optional[MemeContext]:
        """Generate meme text and select template using Gemini"""
        try:
            # Create template descriptions for Gemini
            template_descriptions = []
            for template in self.templates:
                description = self._get_template_description(template['name'])
                template_descriptions.append(f"- {template['name']} ({description})")
            
            gemini_prompt = f"""
            As a meme generator, create a funny and engaging meme based on this prompt: "{prompt}"
            
            Choose from these available templates:
            {chr(10).join(template_descriptions)}
            
            Format your response as JSON:
            {{
                "template": "template_name",
                "text0": "top_text",
                "text1": "bottom_text",
                "reason": "why this template fits"
            }}
            
            Keep texts short, witty, and meme-worthy. Be creative and funny.
            """

            # Generate content
            response = self.model.generate_content(gemini_prompt)
            if response and response.text:
                # Extract and parse JSON from response
                json_str = response.text.strip()
                json_str = json_str.replace('```json', '').replace('```', '').strip()
                result = json.loads(json_str)
                
                # Get template ID from template name
                template_name = result['template']
                template = next(
                    (t for t in self.templates if template_name.lower() in t['name'].lower()),
                    None
                )
                
                if not template:
                    print(f"Invalid template: {template_name}, falling back to simple generation")
                    return self._generate_fallback_context(prompt)
                
                return MemeContext(
                    template_id=template['id'],
                    text0=result['text0'],
                    text1=result['text1']
                )

        except Exception as e:
            print(f"Error generating with Gemini: {e}")
        
        # Fallback to simple generation if anything fails
        return self._generate_fallback_context(prompt)

    def _generate_fallback_context(self, prompt: str) -> MemeContext:
        """Generate meme text using simple rules when Gemini fails"""
        prompt_lower = prompt.lower()
        
        # Simple template selection based on keywords
        template_id = None
        text0 = None
        text1 = None
        
        # Try to find a suitable template from available ones
        if any(word in prompt_lower for word in ['prefer', 'better', 'like', 'dislike', 'instead', 'vs', 'versus']):
            drake_template = next((t for t in self.templates if 'Drake' in t['name']), None)
            if drake_template:
                template_id = drake_template['id']
                if 'vs' in prompt_lower or 'versus' in prompt_lower:
                    parts = prompt_lower.replace('versus', 'vs').split('vs')
                    text0 = parts[0].strip().title()
                    text1 = parts[1].strip().title()
                else:
                    text0 = prompt.split()[0] + " the old way"
                    text1 = "Using " + " ".join(prompt.split()[1:])
        
        elif any(word in prompt_lower for word in ['tempt', 'distract', 'attracted']):
            boyfriend_template = next((t for t in self.templates if 'Boyfriend' in t['name']), None)
            if boyfriend_template:
                template_id = boyfriend_template['id']
                words = prompt.split()
                text0 = words[0] if words else "Me"
                text1 = " ".join(words[1:]) if len(words) > 1 else "Something shiny"
        
        elif any(word in prompt_lower for word in ['evil', 'chaos', 'disaster', 'destroy']):
            disaster_template = next((t for t in self.templates if 'Disaster' in t['name']), None)
            if disaster_template:
                template_id = disaster_template['id']
                text0 = "When " + prompt if not prompt.lower().startswith('when') else prompt
                text1 = "😈"
        
        elif any(word in prompt_lower for word in ['choice', 'path', 'decision']):
            exit_template = next((t for t in self.templates if 'Exit' in t['name']), None)
            if exit_template:
                template_id = exit_template['id']
                words = prompt.split()
                mid = len(words) // 2
                text0 = " ".join(words[:mid])
                text1 = " ".join(words[mid:])
        
        # Default to any available template if none matched or couldn't find specific template
        if not template_id and self.templates:
            # Try to find One Does Not Simply template first
            default_template = next(
                (t for t in self.templates if 'Simply' in t['name']),
                self.templates[0]  # Fallback to first available template
            )
            template_id = default_template['id']
            text0 = "One does not simply"
            text1 = prompt
        elif not template_id:
            # If no templates available at all, use hardcoded fallback
            template_id = '61579'  # One Does Not Simply
            text0 = "One does not simply"
            text1 = prompt
        
        return MemeContext(
            template_id=template_id,
            text0=text0,
            text1=text1
        )