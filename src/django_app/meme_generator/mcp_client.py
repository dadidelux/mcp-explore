import json
import os
import subprocess
import tempfile
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mcp_meme_generator')
logger.info('MCP Meme Generator initialized')

@dataclass
class MemeContext:
    template_id: str
    text0: str
    text1: Optional[str] = None
    reason: Optional[str] = None

class MCPMemeGenerator:
    def __init__(self):
        self.template_map = {
            'Drake': '181913649',
            'Distracted Boyfriend': '112126428',
            'Disaster Girl': '97984',
            'Left Exit': '124822590',
            'One Does Not Simply': '61579'
        }

        # Also keep lowercase keys for matching
        self.template_suggestions = {k.lower(): v for k, v in self.template_map.items()}

    def _generate_fallback_response(self, prompt: str) -> MemeContext:
        """
        Generate meme text without Context7 using simple rules.
        """
        prompt_lower = prompt.lower()
        
        template_id = None
        text0 = None
        text1 = None
        reason = "Fallback generation (Context7 not available)"
        
        # Simple template selection based on keywords
        if any(word in prompt_lower for word in ['prefer', 'better', 'like', 'dislike', 'instead', 'vs', 'versus']):
            template_id = self.template_map['Drake']
            if 'vs' in prompt_lower or 'versus' in prompt_lower:
                parts = prompt_lower.replace('versus', 'vs').split('vs')
                text0 = parts[0].strip().title()
                text1 = parts[1].strip().title()
            else:
                text0 = prompt.split()[0] + " the old way"
                text1 = "Using " + " ".join(prompt.split()[1:])
        
        elif any(word in prompt_lower for word in ['tempt', 'distract', 'attracted']):
            template_id = self.template_map['Distracted Boyfriend']
            words = prompt.split()
            text0 = words[0] if words else "Me"
            text1 = " ".join(words[1:]) if len(words) > 1 else "Something shiny"
        
        elif any(word in prompt_lower for word in ['evil', 'chaos', 'disaster', 'destroy']):
            template_id = self.template_map['Disaster Girl']
            text0 = "When " + prompt if not prompt.lower().startswith('when') else prompt
            text1 = "😈"
        
        elif any(word in prompt_lower for word in ['choice', 'path', 'decision']):
            template_id = self.template_map['Left Exit']
            words = prompt.split()
            mid = len(words) // 2
            text0 = " ".join(words[:mid])
            text1 = " ".join(words[mid:])
        
        else:
            template_id = self.template_map['One Does Not Simply']
            text0 = "One does not simply"
            text1 = prompt
        
        return MemeContext(
            template_id=template_id,
            text0=text0,
            text1=text1,
            reason=reason
        )

    def _send_mcp_request(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Send a request to the VS Code Context7 MCP server and get a response"""
        try:
            logger.info(f"Generating meme for prompt: {prompt}")
            
            # Create the request as a JSON object
            request = {
                "type": "completion",
                "input": {
                    "prompt": prompt,
                    "context": """You are a witty meme creator. Generate an original, funny meme based on the given prompt.
                Your response must be valid JSON with this structure:
                {
                    "template": "Choose one: Drake, Distracted Boyfriend, Disaster Girl, Left Exit, One Does Not Simply",
                    "text0": "Top text - be creative and funny",
                    "text1": "Bottom text - deliver the punchline",
                    "reason": "Explain why you chose this template and how it fits the humor"
                }"""
                },
                "temperature": 0.85,
                "max_tokens": 300
            }

            # Convert to JSON string
            request_str = json.dumps(request)
            
            logger.info("Executing MCP request...")
            
            # Use local node_modules path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            commands = [
                f"node {base_dir}/node_modules/@upstash/context7-mcp/dist/index.js",
                f"{base_dir}/node_modules/.bin/context7-mcp"
            ]
            
            for cmd in commands:
                try:
                    process = subprocess.run(
                        cmd,
                        input=request_str,
                        text=True,
                        capture_output=True,
                        shell=True,
                        cwd=os.path.dirname(os.path.abspath(__file__))
                    )
                    
                    stdout, stderr = process.stdout, process.stderr
                    
                    if stderr:
                        logger.warning(f"MCP stderr: {stderr}")
                    
                    if stdout:
                        logger.info(f"Raw MCP stdout: {stdout}")
                        
                        # Try to find a JSON object in the output
                        stdout_lines = stdout.strip().split('\n')
                        for line in stdout_lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            try:
                                data = json.loads(line)
                                if 'completion' in data:
                                    response_text = data['completion'].strip()
                                    
                                    # Extract JSON from the completion
                                    if '```json' in response_text:
                                        json_part = response_text.split('```json')[1].split('```')[0].strip()
                                    elif '```' in response_text:
                                        json_part = response_text.split('```')[1].split('```')[0].strip()
                                    else:
                                        json_part = response_text
                                    
                                    meme_data = json.loads(json_part)
                                    if all(k in meme_data for k in ['template', 'text0', 'text1', 'reason']):
                                        logger.info(f"Successfully generated meme with template: {meme_data['template']}")
                                        return meme_data
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                logger.error(f"Error parsing response line: {str(e)}")
                                continue
                    
                    logger.warning(f"Command '{cmd}' didn't return valid response")
                except Exception as e:
                    logger.error(f"Error running command '{cmd}': {str(e)}")
            
            logger.warning("All MCP commands failed")
            return None
            
        except Exception as e:
            logger.error(f"MCP error: {str(e)}")
            return None
            
    def generate_meme_context(self, prompt: str) -> MemeContext:
        """
        Generate a meme context with template and text based on the prompt.
        Will try Context7 first, then fall back to simple rules if needed.
        """
        try:
            # Get meme data from MCP
            meme_data = self._send_mcp_request(prompt)
            
            if meme_data:
                # Convert template name to template ID
                template_key = next(
                    (key for key, _ in self.template_suggestions.items() 
                     if key.lower() in meme_data['template'].lower()),
                    'drake'  # Default to Drake template if no match
                )
                
                return MemeContext(
                    template_id=self.template_suggestions[template_key],
                    text0=meme_data['text0'],
                    text1=meme_data['text1'],
                    reason=meme_data.get('reason', '')
                )
            
        except Exception as e:
            logger.error(f"Error generating meme context: {str(e)}")
            
        # Fallback to basic template matching if MCP fails
        logger.warning("MCP interaction failed or returned no data. Falling back to basic generation.") # Enhanced log
        from .views import select_meme_template, generate_meme_text
        template = select_meme_template(prompt)
        text0, text1 = generate_meme_text(prompt)
        return MemeContext(
            template_id=template['id'],
            text0=text0,
            text1=text1,
            reason="Fallback: AI generation failed. Using basic text splitting." # Enhanced reason
        )
