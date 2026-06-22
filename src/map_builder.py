import folium
from folium import plugins
from typing import List
from .models import Session
from .analyzer import Insight
import os

class MapGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _get_color(self, speed, max_speed):
        # Green = fast, Red = slow
        if max_speed == 0:
            return '#ff0000'
        ratio = speed / max_speed
        if ratio > 0.8:
            return '#00ff00' # Green
        elif ratio > 0.5:
            return '#ffff00' # Yellow
        else:
            return '#ff0000' # Red

    def generate_session_map(self, session: Session, insights: List[Insight], filename: str):
        if not session.telemetry:
            return None
            
        # Center map on the first point
        start_lat = session.telemetry[0].lat
        start_lon = session.telemetry[0].lon
        
        m = folium.Map(location=[start_lat, start_lon], zoom_start=16, tiles='OpenStreetMap')
        
        # Add the trajectory as a sequence of colored line segments
        max_s = session.maxSpeed
        if max_s == 0:
            max_s = max([pt.speedKmh for pt in session.telemetry]) if session.telemetry else 1
            
        for i in range(len(session.telemetry) - 1):
            pt1 = session.telemetry[i]
            pt2 = session.telemetry[i+1]
            color = self._get_color(pt1.speedKmh, max_s)
            
            folium.PolyLine(
                locations=[(pt1.lat, pt1.lon), (pt2.lat, pt2.lon)],
                color=color,
                weight=5,
                opacity=0.8
            ).add_to(m)

        # Add insight markers
        for insight in insights:
            icon_color = 'red' if insight.type == 'braking' else 'orange' if insight.type == 'acceleration' else 'blue'
            icon = 'info-sign'
            
            html = f"""
            <div style="width:200px">
                <h4>{insight.title}</h4>
                <p>{insight.description}</p>
            </div>
            """
            iframe = folium.IFrame(html=html, width=220, height=120)
            popup = folium.Popup(iframe, max_width=265)
            
            folium.Marker(
                location=[insight.lat, insight.lon],
                popup=popup,
                icon=folium.Icon(color=icon_color, icon=icon)
            ).add_to(m)
            
        filepath = os.path.join(self.output_dir, filename)
        m.save(filepath)
        return filepath
