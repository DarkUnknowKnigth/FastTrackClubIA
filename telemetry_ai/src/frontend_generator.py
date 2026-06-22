import json
import os
from jinja2 import Environment, FileSystemLoader

class FrontendGenerator:
    def __init__(self, templates_dir: str, output_dir: str):
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        self._create_template()
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def _create_template(self):
        template_path = os.path.join(self.templates_dir, 'index.html')
        html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Fast Track Club - AI Telemetry</title>
    <!-- Tailwind for styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Alpine.js for interactivity -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen p-8">
    <div class="max-w-6xl mx-auto" x-data="telemetryApp()">
        <header class="mb-8">
            <h1 class="text-4xl font-bold text-red-500">Fast Track Club</h1>
            <p class="text-gray-400">AI Telemetry Analyzer - GT3 Performance</p>
        </header>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <!-- Sidebar / Sessions List -->
            <div class="col-span-1 bg-gray-800 p-4 rounded-lg shadow-lg">
                <h2 class="text-xl font-bold mb-4 border-b border-gray-700 pb-2">Sesiones</h2>
                <ul class="space-y-2">
                    <template x-for="session in sessions" :key="session.id">
                        <li>
                            <button 
                                @click="selectSession(session)"
                                :class="selectedSession && selectedSession.id === session.id ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'"
                                class="w-full text-left p-3 rounded transition-colors duration-200">
                                <div class="font-semibold">Sesión #<span x-text="session.id"></span></div>
                                <div class="text-sm text-gray-300">Piloto: <span x-text="session.pilot"></span></div>
                                <div class="text-xs text-gray-400 mt-1">
                                    <span x-text="session.distance.toFixed(1)"></span> m | 
                                    <span x-text="session.maxSpeed.toFixed(1)"></span> km/h
                                </div>
                            </button>
                        </li>
                    </template>
                </ul>
            </div>
            
            <!-- Main Content Area -->
            <div class="col-span-1 md:col-span-3 space-y-6" x-show="selectedSession">
                <!-- Map Area -->
                <div class="bg-gray-800 p-4 rounded-lg shadow-lg h-[500px] flex flex-col">
                    <h3 class="text-xl font-bold mb-2">Mapa de Telemetría (Folium)</h3>
                    <div class="flex-grow rounded overflow-hidden bg-gray-700">
                        <iframe :src="selectedSession.map_file" class="w-full h-full border-0"></iframe>
                    </div>
                </div>
                
                <!-- GT3 Report Area -->
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <h3 class="text-2xl font-bold text-red-400 mb-4 border-b border-gray-700 pb-2">Informe del Ingeniero</h3>
                    <div class="prose prose-invert max-w-none" x-html="formatReport(selectedSession.report)">
                    </div>
                </div>
            </div>
            
            <div class="col-span-1 md:col-span-3 bg-gray-800 p-8 rounded-lg shadow-lg text-center" x-show="!selectedSession">
                <p class="text-gray-400 text-lg">Selecciona una sesión de la lista para ver el análisis de la IA y el mapa interactivo.</p>
            </div>
        </div>
    </div>

    <script>
        function telemetryApp() {
            return {
                sessions: {{ sessions_json | safe }},
                selectedSession: null,
                
                init() {
                    if (this.sessions.length > 0) {
                        this.selectedSession = this.sessions[0];
                    }
                },
                
                selectSession(session) {
                    this.selectedSession = session;
                },
                
                formatReport(text) {
                    if(!text) return "";
                    // Simple markdown to HTML for the report
                    return text
                        .replace(/### (.*)/g, '<h4 class="text-xl font-bold mt-4 mb-2 text-red-300">$1</h4>')
                        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                        .replace(/\\n/g, '<br/>');
                }
            }
        }
    </script>
</body>
</html>
"""
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def generate_index(self, sessions_data: list):
        template = self.env.get_template('index.html')
        # Convert list of dicts to JSON string
        sessions_json = json.dumps(sessions_data)
        
        output_html = template.render(sessions_json=sessions_json)
        output_path = os.path.join(self.output_dir, 'index.html')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
            
        return output_path
