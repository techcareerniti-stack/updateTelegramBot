import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_education_notices():
    """Ministry of Education मधून फक्त Important Updates काढण्यासाठी"""
    news_list = []
    seen_titles = set()
    seen_links = set()
    
    # मुख्य URLs
    urls_to_try = [
        "https://www.education.gov.in/",
        "https://www.education.gov.in/updates"  # येथे महत्त्वाच्या updates आहेत
    ]
    
    # Important keywords (फक्त या keywords असतील तरच घ्या)
    important_keywords = [
        'scholarship', 'fellowship', 'nomination', 'programme', 'prize', 'award',
        'funding', 'opportunity', 'competition', 'call for', 'applications',
        'छात्रवृत्ति', 'कार्यक्रम', 'पुरस्कार', 'अवसर', 'आवेदन',
        'notice', 'notification', 'circular', 'उपलब्धियां', 'परिपत्र',
        'training', 'workshop', 'webinar', 'प्रशिक्षण', 'कार्यशाला',
        'appointment', 'extension', 'नियुक्ति', 'विस्तार',
        'mhrd', 'ministry', 'मंत्रालय', 'शिक्षा', 'विभाग',
        'नवाचार', 'अनुदान', 'योजना', 'पहल', 'प्रगति'
    ]
    
    # Unwanted navigation links
    unwanted_keywords = [
        "skip to main", "screen reader", "facebook", "twitter", "instagram", 
        "youtube", "tender", "recruitment", "job", "vacancy", "copyright", 
        "privacy", "terms", "sitemap", "feedback", "help", "contact us",
        "website", "visitor", "counter", "powered by", "archive",
        "iiser", "iit", "nit", "iiit", "iim", "university", "college", "council",
        "telephone", "directory", "राष्ट्रीय", "संस्थान", "प्रौद्योगिकी", "प्रबंधन"
    ]
    
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=25, verify=False, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # सर्व links शोधा
                all_links = soup.find_all('a')
                
                for link in all_links:
                    text = link.get_text(strip=True)
                    link_url = link.get('href', '')
                    
                    # Clean text
                    text = re.sub(r'\s+', ' ', text).strip()
                    text = re.sub(r'✅ Found:', '', text).strip()
                    text = re.sub(r'\.\.\.$', '', text).strip()
                    
                    # Skip short texts
                    if not text or len(text) < 20:
                        continue
                    
                    # Skip unwanted
                    is_unwanted = False
                    for uw in unwanted_keywords:
                        if uw.lower() in text.lower():
                            is_unwanted = True
                            break
                    
                    if is_unwanted:
                        continue
                    
                    # Check if important
                    is_important = False
                    for ik in important_keywords:
                        if ik.lower() in text.lower():
                            is_important = True
                            break
                    
                    # Check for file size (PDF indicators)
                    has_size = bool(re.search(r'\d+(\.\d+)?\s*(KB|MB)', text, re.I))
                    
                    # Check if it has a date
                    has_date = bool(re.search(r'\d{2}[-/]\d{2}[-/]\d{2,4}', text))
                    
                    if (is_important or has_size or has_date) and text not in seen_titles:
                        seen_titles.add(text)
                        
                        # Build full URL
                        if link_url and not link_url.startswith('http'):
                            if link_url.startswith('/'):
                                link_url = "https://www.education.gov.in" + link_url
                            else:
                                link_url = url.rstrip('/') + '/' + link_url.lstrip('/')
                        
                        # Limit title length
                        title_text = text[:200] if len(text) > 200 else text
                        
                        news_list.append({
                            "title": f"📖 EduMin: {title_text}",
                            "link": link_url if link_url else url,
                            "pub_date": datetime.now().strftime("%Y-%m-%d"),
                            "source": "Ministry of Education"
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
    
    print(f"📊 Education: {len(unique_news)} Important Updates सापडल्या")
    return unique_news[:15]

if __name__ == "__main__":
    notices = fetch_education_notices()
    for idx, notice in enumerate(notices, 1):
        print(f"{idx}. {notice['title'][:80]}")