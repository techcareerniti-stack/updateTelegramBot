import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_neet_notices():
    """NEET UG Maharashtra मधून फक्त REAL Notices काढण्यासाठी"""
    url = "https://medicalug2025.mahacet.org/NEET-UG-2025/login"
    news_list = []
    seen_titles = set()
    
    # वगळायचे headings
    unwanted_headings = ["News ( बातमी )", "Notification ( सूचना )", "Home", "Contact Us", "Login/Registration", "Note :"]
    
    try:
        response = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # सर्व links शोधा
        all_links = soup.find_all('a')
        
        for link in all_links:
            text = link.get_text(strip=True)
            link_url = link.get('href', '')
            
            # Clean the text (remove "New", "नवीन", ".", etc.)
            text = re.sub(r'\s*New\s*', ' ', text).strip()
            text = re.sub(r'\s*\.\s*', ' ', text).strip()
            text = re.sub(r'\s+', ' ', text)
            
            # Skip unwanted headings
            if text in unwanted_headings:
                continue
            
            # Skip short texts
            if not text or len(text) < 10:
                continue
            
            # Skip if it's just a number
            if text.isdigit():
                continue
            
            # Valid notice conditions
            is_valid = False
            
            # PDF link असल्यास valid
            if link_url and '.pdf' in link_url.lower():
                is_valid = True
            
            # Important keywords असल्यास valid
            keywords = ['notice', 'list', 'selection', 'merit', 'schedule', 'result', 
                        'counselling', 'vacancy', 'seat matrix', 'admit', 'hall ticket',
                        'सूचना', 'निवड', 'यादी', 'वेळापत्रक', 'निकाल', 'provisional',
                        'eligibility', 'registration', 'cut off', 'round', 'stray vacancy']
            for kw in keywords:
                if kw.lower() in text.lower() or (link_url and kw.lower() in link_url.lower()):
                    is_valid = True
                    break
            
            # Length check (real notices are usually longer)
            if len(text) < 15 and not link_url:
                is_valid = False
            
            if is_valid and text not in seen_titles:
                seen_titles.add(text)
                
                # Build full URL
                if link_url and not link_url.startswith('http'):
                    if link_url.startswith('/'):
                        link_url = "https://medicalug2025.mahacet.org" + link_url
                    else:
                        link_url = url.rstrip('/') + '/' + link_url.lstrip('/')
                
                news_list.append({
                    "title": text[:150],
                    "link": link_url if link_url else url,
                    "pub_date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "NEET"
                })
        
        # Remove duplicates by link
        unique_by_link = {}
        for item in news_list:
            if item['link'] not in unique_by_link:
                unique_by_link[item['link']] = item
        
        result = list(unique_by_link.values())
        print(f"📊 NEET: {len(result)} Real Notices सापडल्या")
        return result[:30]
        
    except Exception as e:
        print(f"❌ NEET Error: {e}")
        return []

if __name__ == "__main__":
    notices = fetch_neet_notices()
    print(f"\n📢 {len(notices)} NEET Notices:")
    for idx, notice in enumerate(notices, 1):
        print(f"{idx}. {notice['title'][:80]}")
        print(f"   🔗 {notice['link']}\n")