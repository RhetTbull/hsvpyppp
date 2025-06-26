#!/usr/bin/env python3
"""
HSV.py Meetup Checker

A simple tool to check when the next HSV.py meetup is scheduled.
"""

import requests
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any


class HSVPyMeetupChecker:
    """Check for upcoming HSV.py meetups."""
    
    def __init__(self):
        self.meetup_url = "https://www.meetup.com/hsv-py/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_next_meetup(self) -> Optional[Dict[str, Any]]:
        """Fetch and parse the next upcoming meetup information."""
        try:
            response = self.session.get(self.meetup_url)
            response.raise_for_status()
            
            # Extract JSON-LD structured data
            json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            matches = re.findall(json_ld_pattern, response.text, re.DOTALL)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Event':
                                return self._parse_event(item)
                    elif data.get('@type') == 'Event':
                        return self._parse_event(data)
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching meetup page: {e}")
            return None
    
    def _parse_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse event data from JSON-LD structure."""
        parsed_event = {
            'name': event_data.get('name', 'Unknown Event'),
            'description': event_data.get('description', ''),
            'start_time': event_data.get('startDate'),
            'end_time': event_data.get('endDate'),
            'location': self._parse_location(event_data.get('location', {})),
            'url': event_data.get('url', self.meetup_url)
        }
        
        return parsed_event
    
    def _parse_location(self, location_data: Dict[str, Any]) -> str:
        """Parse location information."""
        if isinstance(location_data, dict):
            name = location_data.get('name', '')
            address = location_data.get('address', {})
            if isinstance(address, dict):
                street = address.get('streetAddress', '')
                city = address.get('addressLocality', '')
                state = address.get('addressRegion', '')
                return f"{name}, {street}, {city}, {state}".strip(', ')
            return name
        return str(location_data) if location_data else 'Location TBD'
    
    def format_meetup_info(self, meetup_data: Dict[str, Any]) -> str:
        """Format meetup information for display."""
        if not meetup_data:
            return "No upcoming meetup found."
        
        output = []
        output.append(f"Next HSV.py Meetup:")
        output.append(f"  Title: {meetup_data['name']}")
        
        if meetup_data['start_time']:
            try:
                dt = datetime.fromisoformat(meetup_data['start_time'].replace('Z', '+00:00'))
                formatted_time = dt.strftime('%A, %B %d, %Y at %I:%M %p %Z')
                output.append(f"  Date: {formatted_time}")
            except ValueError:
                output.append(f"  Date: {meetup_data['start_time']}")
        
        output.append(f"  Location: {meetup_data['location']}")
        
        if meetup_data['url']:
            output.append(f"  URL: {meetup_data['url']}")
        
        return '\n'.join(output)


def main():
    """Main function to check and display next meetup."""
    checker = HSVPyMeetupChecker()
    meetup = checker.get_next_meetup()
    print(checker.format_meetup_info(meetup))


if __name__ == "__main__":
    main()