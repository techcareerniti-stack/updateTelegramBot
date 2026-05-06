import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_pib_notices():
    """PIB मधून फक्त शिक्षण संबंधित Press Releases काढण्यासाठी"""
    news_list = []
    seen_titles = set()
    seen_links = set()
    
    # शिक्षण संबंधित keywords (English + Hindi)
    education_keywords = [
        # English
        'education', 'school', 'college', 'university', 'student', 'teacher',
        'exam', 'result', 'admission', 'scholarship', 'council', 'board',
        'ministry of education', 'ugc', 'net', 'jrf', 'nta', 'cet', 'neet',
        'jee', 'cuet', 'awards', 'curriculum', 'syllabus', 'textbook',
        'literacy', 'vocational', 'training', 'internship', 'fellowship',
        'research', 'phd', 'masters', 'bachelor', 'diploma', 'certificate',
        'library', 'digital education', 'online learning', 'mid-day meal',
        'academic', 'pedagogy', 'institution', 'icssr', 'aicte', 'ncert',
        # Hindi
        'शिक्षण', 'विद्यार्थी', 'शिक्षक', 'महाविद्यालय', 'विद्यापीठ',
        'परीक्षा', 'निकाल', 'प्रवेश', 'शिष्यवृत्ती', 'परिषद', 'मंडळ',
        'शिक्षण मंत्रालय', 'अभ्यासक्रम', 'पाठ्यपुस्तक', 'साक्षरता',
        'व्यावसायिक', 'प्रशिक्षण', 'इंटर्नशिप', 'फेलोशिप', 'संशोधन',
        'पीएचडी', 'पदवी', 'डिप्लोमा', 'प्रमाणपत्र', 'ग्रंथालय'
    ]
    
    # Ministry of Education and related ministries
    education_ministries = [
        'ministry of education', 'शिक्षा मंत्रालय', 'ugc', 'aicte', 'ncert',
        'nios', 'kvs', 'nvs', 'cbs', 'ignou', 'iit', 'nit', 'iiit'
    ]
    
    # URLs to try
    urls_to_try = [
        "https://pib.gov.in/PressReleasePage.aspx",
        "https://pib.gov.in/allPressRelease.aspx"
    ]
    
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=20, verify=False, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Find all press release links
                all_links = soup.find_all('a')
                
                for link in all_links:
                    text = link.get_text(strip=True)
                    link_url = link.get('href', '')
                    
                    # Skip short texts
                    if not text or len(text) < 20:
                        continue
                    
                    # Check if education related
                    is_education = False
                    
                    # Check by ministry
                    for em in education_ministries:
                        if em.lower() in text.lower():
                            is_education = True
                            break
                    
                    # Check by keywords
                    if not is_education:
                        for ek in education_keywords:
                            if ek.lower() in text.lower():
                                is_education = True
                                break
                    
                    if is_education and text not in seen_titles:
                        seen_titles.add(text)
                        
                        # Build full URL
                        if link_url and not link_url.startswith('http'):
                            if link_url.startswith('/'):
                                link_url = "https://pib.gov.in" + link_url
                            else:
                                link_url = "https://pib.gov.in/" + link_url
                        
                        news_list.append({
                            "title": f"📰 PIB: {text[:200]}",
                            "link": link_url if link_url else url,
                            "pub_date": datetime.now().strftime("%Y-%m-%d"),
                            "source": "PIB"
                        })
                        
            time.sleep(1)
            
        except Exception as e:
            print(f"  ⚠️ URL failed {url}: {e}")
            continue
    
    # Remove duplicates
    unique_news = []
    seen_final = set()
    for item in news_list:
        key = f"{item['title'][:80]}_{item['link']}"
        if key not in seen_final:
            seen_final.add(key)
            unique_news.append(item)
    
    print(f"📊 PIB: {len(unique_news)} Education Releases सापडल्या")
    
    # If no education releases found, return empty list
    if len(unique_news) == 0:
        print("  📭 सध्या कोणतीही शिक्षण संबंधित प्रेस रिलीज नाही")
    
    return unique_news[:15]

# Simplify: Return empty list directly if RSS is down
def fetch_pib_notices_simple():
    """Simplified version - returns empty list as PIB RSS is currently down"""
    print("📊 PIB: RSS feeds currently unavailable")
    return []

if __name__ == "__main__":
    notices = fetch_pib_notices()
    for idx, notice in enumerate(notices, 1):
        print(f"{idx}. {notice['title'][:80]}")
        print(f"   🔗 {notice['link']}\n")