import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_nta_notices():
    urls_to_try = ["https://nta.ac.in/", "https://ugcnet.nta.nic.in/"]
    news_list = []
    seen_titles = set()
    seen_links = set()
    
    unwanted = ["read more", "home", "contact us", "about us", "rti", "tender"]
    
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=30, verify=False, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            all_links = soup.find_all('a')
            
            for link in all_links:
                text = link.get_text(strip=True)
                link_url = link.get('href', '')
                text = re.sub(r'\s+', ' ', text)
                text = re.sub(r'Read More$', '', text).strip()
                
                if not text or len(text) < 15:
                    continue
                if any(uw.lower() in text.lower() for uw in unwanted):
                    continue
                
                is_valid = bool(link_url and '.pdf' in link_url.lower())
                keywords = ['notice', 'notification', 'schedule', 'result', 'answer key', 'admit card', 'exam date']
                if any(kw.lower() in text.lower() for kw in keywords):
                    is_valid = True
                if re.search(r'NEET|JEE|CUET|UGC|NET|NTA|CMAT|NIFT|NTET|ICAR', text, re.I):
                    is_valid = True
                
                if is_valid and text not in seen_titles and link_url not in seen_links:
                    seen_titles.add(text)
                    seen_links.add(link_url)
                    if link_url and not link_url.startswith('http'):
                        base = "https://nta.ac.in" if 'nta.ac.in' in url else "https://ugcnet.nta.nic.in"
                        link_url = base + link_url if link_url.startswith('/') else url.rstrip('/') + '/' + link_url.lstrip('/')
                    
                    prefix = "📚 UGC-NET: " if 'ugcnet' in url else "📢 NTA: "
                    news_list.append({
                        "title": f"{prefix}{text[:180]}",
                        "link": link_url,
                        "pub_date": datetime.now().strftime("%Y-%m-%d"),
                        "source": "NTA/UGC-NET"
                    })
        except Exception as e:
            print(f"  ⚠️ URL failed {url}: {e}")
            continue
    
    unique = []
    seen = set()
    for item in news_list:
        key = item['title'][:80]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    print(f"📊 NTA: {len(unique)} Notices सापडल्या")
    return unique[:25]

if __name__ == "__main__":
    notices = fetch_nta_notices()
    for idx, notice in enumerate(notices, 1):
        print(f"{idx}. {notice['title'][:80]}")