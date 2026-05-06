import requests
import ssl
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_nmc_notices():
    """NMC India मधून Notices काढण्यासाठी (SSL bypass with verify=False)"""
    urls_to_try = [
        "https://www.nmc.org.in/activities/notices/",
        "https://www.nmc.org.in/",
        "https://www.nmc.org.in/latest-updates/"
    ]
    
    news_list = []
    seen_titles = set()
    
    for url in urls_to_try:
        try:
            print(f"  📡 Trying NMC URL: {url}")
            # verify=False added to bypass SSL error
            response = requests.get(url, timeout=20, verify=False, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Rest of the code remains same...
            all_links = soup.find_all('a')
            
            for link in all_links:
                text = link.get_text(strip=True)
                link_url = link.get('href', '')
                
                keywords = ['notice', 'circular', 'notification', 'advisory', 
                           'press release', 'update', 'सूचना', 'परिपत्रक']
                
                is_notice = False
                for kw in keywords:
                    if kw.lower() in text.lower() or (link_url and kw.lower() in link_url.lower()):
                        is_notice = True
                        break
                
                has_date = bool(re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text))
                is_pdf = link_url and '.pdf' in link_url.lower()
                
                if text and len(text) > 15 and len(text) < 200 and (is_notice or has_date or is_pdf):
                    if text not in seen_titles:
                        seen_titles.add(text)
                        
                        if link_url and not link_url.startswith('http'):
                            if link_url.startswith('/'):
                                link_url = "https://www.nmc.org.in" + link_url
                            else:
                                link_url = url.rstrip('/') + '/' + link_url.lstrip('/')
                        
                        news_list.append({
                            "title": f"📢 {text[:100]}",
                            "link": link_url if link_url else url,
                            "pub_date": datetime.now().strftime("%Y-%m-%d"),
                            "source": "NMC India"
                        })
            
            if news_list:
                break
                
        except Exception as e:
            print(f"  ⚠️ NMC URL failed {url}: {e}")
            continue
    
    unique_news = []
    seen_links = set()
    for item in news_list:
        if item['link'] not in seen_links:
            seen_links.add(item['link'])
            unique_news.append(item)
    
    print(f"📊 NMC: {len(unique_news)} Notices सापडल्या")
    return unique_news[:20]

if __name__ == "__main__":
    notices = fetch_nmc_notices()
    print(f"\n📢 {len(notices)} NMC Notices:")
    for idx, notice in enumerate(notices, 1):
        print(f"{idx}. {notice['title'][:80]}")
        print(f"   🔗 {notice['link']}\n")