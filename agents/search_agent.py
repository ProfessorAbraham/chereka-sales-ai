# agents/search_agent.py
import requests
import json
from typing import List, Dict
from pathlib import Path

class SearchAgent:
    def __init__(self, api_key: str, cx: str):
        self.api_key = api_key
        self.cx = cx  # Search Engine ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def find_schools(self, query: str, region: str, num_results: int = 5) -> List[Dict]:
        """Search for schools matching criteria"""
        params = {
            "q": f"{query} in {region} Ethiopia contact",
            "key": self.api_key,
            "cx": self.cx,
            "num": num_results
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return self._parse_results(response.json())
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def _parse_results(self, results: Dict) -> List[Dict]:
        """Extract school data from API response"""
        return [{
            "name": item.get("title", "").split(" - ")[0],
            "link": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": "Google Search"
        } for item in results.get("items", [])]

# Example usage (for testing)
if __name__ == "__main__":
    # Load credentials from config (we'll set this up next)
    from config.settings import GOOGLE_API_KEY, GOOGLE_CX
    
    agent = SearchAgent(GOOGLE_API_KEY, GOOGLE_CX)
    schools = agent.find_schools("private high school", "Addis Ababa")
    print(json.dumps(schools, indent=2))