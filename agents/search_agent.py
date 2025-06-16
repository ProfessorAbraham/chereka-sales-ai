# agents/search_agent.py
import requests
import re
from typing import List, Dict
from pathlib import Path

class SearchAgent:
    def __init__(self, api_key: str, cx: str):
        self.api_key = api_key
        self.cx = cx
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    def find_schools(self, region: str, school_type: str = "private") -> List[Dict]:
        """Find schools with phone-focused search"""
        queries = [
            f"{school_type} schools in {region} Ethiopia phone number",
            f"{school_type} academies in {region} contact",
            f"list of {school_type} schools in {region}"
        ]
        
        all_results = []
        for query in queries:
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.cx,
                "num": 3  # Fewer results but higher quality
            }
            try:
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                all_results.extend(self._parse_results(response.json()))
            except Exception as e:
                print(f"Query '{query}' failed: {e}")
        
        return self._deduplicate(all_results)

    def _parse_results(self, results: Dict) -> List[Dict]:
        """Extract school info from snippets"""
        parsed = []
        for item in results.get("items", []):
            name = item.get("title", "").split(" - ")[0].split(" | ")[0]
            snippet = item.get("snippet", "")
            
            # Ethiopian phone pattern (+251 or 0 followed by 9 digits)
            phones = re.findall(r'(\+251|0)\s?\d{1,2}\s?\d{3}\s?\d{4}', snippet)
            
            parsed.append({
                "name": name,
                "source": item.get("link", ""),
                "phones": list(set(phones)),  # Remove duplicates
                "snippet": snippet,
                "has_website": bool(item.get("link", "").startswith("http"))
            })
        return parsed

    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicates by phone number"""
        unique = {}
        for school in results:
            for phone in school["phones"]:
                if phone not in unique:
                    unique[phone] = school
        return list(unique.values())

# Updated test case
if __name__ == "__main__":
    from config.settings import GOOGLE_API_KEY, GOOGLE_CX
    
    agent = SearchAgent(GOOGLE_API_KEY, GOOGLE_CX)
    schools = agent.find_schools("Addis Ababa")
    
    print(f"Found {len(schools)} unique schools:")
    for i, school in enumerate(schools[:5], 1):  # Show top 5
        print(f"\n{i}. {school['name']}")
        print(f"   Phone(s): {', '.join(school['phones'])}")
        print(f"   Source: {school['source'] if school['source'] else 'No website'}")