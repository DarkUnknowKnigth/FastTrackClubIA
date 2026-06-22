import json
import os
from jinja2 import Environment, FileSystemLoader

class FrontendGenerator:
    def __init__(self, templates_dir: str, output_dir: str):
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def generate_index(self, sessions_data: list):
        template = self.env.get_template('index.html')
        # Convert list of dicts to JSON string
        sessions_json = json.dumps(sessions_data)
        
        output_html = template.render(sessions_json=sessions_json)
        output_path = os.path.join(self.output_dir, 'index.html')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
            
        return output_path
