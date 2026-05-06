import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_cet_cell_notices():
    """CET Cell मधून सर्व Announcements/Notices काढण्यासाठी (फक्त unwanted वगळून)"""
    url = "https://cetcell.mahacet.org/"
    news_list = []
    seen_titles = set()
    
    # फक्त हे absolute unwanted वगळा (जी announcements नाहीत)
    absolute_unwanted = [
        "skip to main content", "search", "menu", "facebook", "twitter", 
        "instagram", "youtube", "visitor counter", "last updated", "gallery",
        "ask pragati", "user manual", "work with us", "rti", "downloads",
        "statistics", "contact", "about us", "home", "CET (Examination) Portal",
        "सीईटी पोर्टल", "Psychometric Test", "Mock Test", "मोक टेस्ट",
        "Foreign Candidate Registration", "Candidate Help", "Instructions",
        "Number of Departments", "Number of CETs", "Number of Courses",
        "Number of Institutes", "About CET Cell", "Technical Education",
        "Higher Education", "Agriculture Education", "Fine Art Education",
        "Medical Education", "AYUSH", "All", "Sr.No", "Course Name",
        "Subject", "Published Date", "Download", "Load More", "Previous",
        "Next", "exam", "id-card", "Address", "Quick Links", "Follow Us",
        "Social Media", "Last Updated", "Powered By", "Synthesys EduCMS"
    ]
    
    try:
        response = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # ========== METHOD 1: Announcement divs मधून ==========
        announcement_divs = soup.find_all(['div', 'section'], class_=re.compile(r'announcement|notification|notice|alert|update', re.I))
        
        for div in announcement_divs:
            links = div.find_all('a')
            for link in links:
                text = link.get_text(strip=True)
                link_url = link.get('href', '')
                
                if text and len(text) > 10 and text not in seen_titles:
                    # Unwanted check
                    is_unwanted = False
                    for uw in absolute_unwanted:
                        if uw.lower() in text.lower():
                            is_unwanted = True
                            break
                    
                    if not is_unwanted and text not in seen_titles:
                        seen_titles.add(text)
                        if link_url and not link_url.startswith('http'):
                            link_url = "https://cetcell.mahacet.org/" + link_url.lstrip('/')
                        
                        news_list.append({
                            "title": text,
                            "link": link_url if link_url else url,
                            "pub_date": datetime.now().strftime("%Y-%m-%d"),
                            "source": url
                        })
        
        # ========== METHOD 2: टेबलमधून notices (सर्वात महत्त्वाचा) ==========
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # Title extract करा (दुसरा column)
                    title_col = cols[1] if len(cols) > 1 else cols[0]
                    title = title_col.get_text(strip=True)
                    
                    # Link extract करा
                    link_tag = title_col.find('a')
                    link_url = link_tag.get('href') if link_tag else ""
                    
                    if title and len(title) > 10 and title not in seen_titles:
                        # Unwanted check
                        is_unwanted = False
                        for uw in absolute_unwanted:
                            if uw.lower() in title.lower():
                                is_unwanted = True
                                break
                        
                        if not is_unwanted:
                            seen_titles.add(title)
                            if link_url and not link_url.startswith('http'):
                                link_url = "https://cetcell.mahacet.org/" + link_url.lstrip('/')
                            
                            news_list.append({
                                "title": title,
                                "link": link_url if link_url else url,
                                "pub_date": cols[2].get_text(strip=True) if len(cols) > 2 else datetime.now().strftime("%Y-%m-%d"),
                                "source": url
                            })
        
        # ========== METHOD 3: मुख्य announcement बॉक्समधून ==========
        main_content = soup.find('main') or soup.find('div', class_='main-content') or soup.find('div', class_='content-area')
        if main_content:
            all_links = main_content.find_all('a')
            for link in all_links:
                text = link.get_text(strip=True)
                link_url = link.get('href', '')
                
                if text and 15 < len(text) < 200 and text not in seen_titles:
                    # Unwanted check
                    is_unwanted = False
                    for uw in absolute_unwanted:
                        if uw.lower() in text.lower():
                            is_unwanted = True
                            break
                    
                    # Date check (announcement मध्ये तारीख असावी)
                    has_date = bool(re.search(r'\d{2}[/-]\d{2}[/-]\d{2,4}', text))
                    
                    if not is_unwanted and (has_date or "notice" in text.lower() or "सूचना" in text.lower()):
                        seen_titles.add(text)
                        if link_url and not link_url.startswith('http'):
                            link_url = "https://cetcell.mahacet.org/" + link_url.lstrip('/')
                        
                        news_list.append({
                            "title": text,
                            "link": link_url if link_url else url,
                            "pub_date": datetime.now().strftime("%Y-%m-%d"),
                            "source": url
                        })
        
        # ========== METHOD 4: विशेष CET announcements ==========
        cet_links = soup.find_all('a', href=re.compile(r'cet|notice|schedule|exam|admit|result', re.I))
        for link in cet_links:
            text = link.get_text(strip=True)
            link_url = link.get('href', '')
            
            if text and 15 < len(text) < 200 and text not in seen_titles:
                is_unwanted = False
                for uw in absolute_unwanted:
                    if uw.lower() in text.lower():
                        is_unwanted = True
                        break
                
                if not is_unwanted:
                    seen_titles.add(text)
                    if link_url and not link_url.startswith('http'):
                        link_url = "https://cetcell.mahacet.org/" + link_url.lstrip('/')
                    
                    # फक्त PDF किंवा notice pages ठेवा
                    if '.pdf' in link_url or 'notice' in link_url.lower() or 'cet' in link_url.lower():
                        news_list.append({
                            "title": text,
                            "link": link_url,
                            "pub_date": datetime.now().strftime("%Y-%m-%d"),
                            "source": url
                        })
        
        # ========== Duplicates remove करा ==========
        unique_news = []
        seen_final = set()
        for item in news_list:
            # पहिले 80 अक्षरे unique identifier म्हणून
            key = item['title'][:80]
            if key not in seen_final:
                seen_final.add(key)
                unique_news.append(item)
        
        # तारखेनुसार sort करा (नवीन वरती)
        unique_news = unique_news[:25]  # फक्त 25 latest
        
        print(f"📊 CET Cell: {len(unique_news)} Announcements सापडल्या")
        return unique_news
        
    except Exception as e:
        print(f"❌ CET Cell Error: {e}")
        return []

# टेस्टिंग साठी
if __name__ == "__main__":
    notices = fetch_cet_cell_notices()
    print(f"\n📢 {len(notices)} Announcements/Notices:")
    print("=" * 70)
    for idx, notice in enumerate(notices, 1):
        print(f"{idx}. {notice['title']}")
        print(f"   📅 {notice['pub_date']}")
        print(f"   🔗 {notice['link']}\n")