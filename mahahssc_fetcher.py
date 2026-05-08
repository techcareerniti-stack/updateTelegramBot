import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_mahahssc_notices():
    """
    Scrape notices from Maharashtra HSC Board website (Marathi page)
    URL: https://mahahsscboard.in/mr
    """
    url = "https://mahahsscboard.in/mr"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"    ⚠️ Failed to fetch HSC Board page: {e}")
        return []
    
    notices = []
    
    # Look for notice links (common patterns in this site)
    # Typically notices are in <a> tags inside specific divs or list items
    # We'll try multiple selectors to be safe
    
    # Selector 1: All <a> tags that contain "notice" or "सूचना" in href or text
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # Filter: must have notice-like keywords or be inside a news section
        # Also avoid empty or very short texts
        if not text or len(text) < 10:
            continue
        
        # Keywords (Marathi & English)
        keywords = ['सूचना', 'नोटीस', 'परीक्षा', 'निकाल', 'वेळापत्रक', 
                    'notice', 'exam', 'result', 'schedule', 'admit', 'hall ticket']
        
        if any(kw.lower() in text.lower() or kw.lower() in href.lower() for kw in keywords):
            # Build absolute URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = "https://mahahsscboard.in" + href
            else:
                full_url = "https://mahahsscboard.in/" + href.lstrip('./')
            
            # Try to extract date – default to today
            pub_date = datetime.now().strftime("%Y-%m-%d")
            
            # If there's a date near the link (e.g., in a <small> or <span>)
            parent = link.find_parent(['li', 'div', 'td'])
            if parent:
                date_candidate = parent.find(['small', 'span', '.date'])
                if date_candidate:
                    date_text = date_candidate.get_text(strip=True)
                    # Simple date extraction (DD/MM/YYYY or similar)
                    # You can enhance this pattern as needed
                    import re
                    match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', date_text)
                    if match:
                        pub_date = match.group(1)
            
            notices.append({
                'title': text[:200],  # limit length
                'link': full_url,
                'pub_date': pub_date
            })
    
    # Remove duplicates by title+link
    unique = {}
    for n in notices:
        key = (n['title'], n['link'])
        if key not in unique:
            unique[key] = n
    
    # Limit to 30 most recent (site may return many)
    return list(unique.values())[:30]