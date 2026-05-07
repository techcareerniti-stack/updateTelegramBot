import os
import json
import hashlib
from datetime import datetime
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests

# ================== 🔴 येथे तुझा Telegram Bot Token आणि Chat ID लिहा 🔴 ==================
TELEGRAM_BOT_TOKEN = "8581753072:AAF-p6R6TLgkNI5B19ZGXzWwW5LOJ9UgWPw"   # उदा: "789456123:ABCdefGHIjklm..."
TELEGRAM_CHAT_IDS = ["2035322636", "536815190"]  # ====================================================================================

# Import fetchers
from cet_cell_fetcher import fetch_cet_cell_notices
from neet_fetcher import fetch_neet_notices
from nmc_fetcher import fetch_nmc_notices
from nta_fetcher import fetch_nta_notices
from pib_fetcher import fetch_pib_notices
from education_fetcher import fetch_education_notices

app = Flask(__name__)

SENT_HASHES_FILE = "sent_hashes.json"
updates_history = []

# ================== Website Configurations ==================
WEBSITES = [
    {
        "name": "🎓 CET Cell Maharashtra",
        "icon": "🎓",
        "type": "custom",
        "custom_function": fetch_cet_cell_notices
    },
    {
        "name": "🩺 NEET UG Maharashtra",
        "icon": "🩺",
        "type": "custom",
        "custom_function": fetch_neet_notices
    },
    {
        "name": "🏛️ NMC India",
        "icon": "🏛️",
        "type": "custom",
        "url": "https://www.nmc.org.in/",
        "custom_function": fetch_nmc_notices
    },
    {
        "name": "📝 NTA India",
        "icon": "📝",
        "type": "custom",
        "custom_function": fetch_nta_notices
    },
    {
        "name": "📰 PIB News",
        "icon": "📰",
        "type": "custom",
        "custom_function": fetch_pib_notices
    },
    {
        "name": "📖 Ministry of Education",
        "icon": "📖",
        "type": "custom",
        "custom_function": fetch_education_notices
    }
]

# ================== Telegram Function ==================
def send_telegram_message(message):
    """Telegram ला मेसेज पाठवते"""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("    📨 Telegram मेसेज पाठवला!")
            return True
        else:
            print(f"    ❌ Telegram Error: {response.text}")
            return False
    except Exception as e:
        print(f"    ❌ Telegram Exception: {e}")
        return False

def format_telegram_message(update):
    """Telegram साठी मेसेज फॉरमॅट करते"""
    message = f"""
<b>📢 {update['site']}</b>

📄 <b>{update['title'][:200]}</b>

🔗 <a href="{update['link']}">पूर्ण नोटीस वाचा</a>

🕐 {update['timestamp']}
    """
    return message.strip()

# ================== File Functions (FIXED) ==================
def load_sent_hashes():
    """Safe way to load sent hashes - handles empty/corrupt files"""
    if not os.path.exists(SENT_HASHES_FILE):
        return set()
    
    try:
        with open(SENT_HASHES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:  # Empty file
                print("  ⚠️ sent_hashes.json is empty, creating new")
                return set()
            data = json.loads(content)
            return set(data) if isinstance(data, list) else set()
    except json.JSONDecodeError as e:
        print(f"  ⚠️ sent_hashes.json is corrupt: {e}")
        print(f"  ⚠️ Creating backup and new file")
        # Backup corrupt file
        if os.path.exists(SENT_HASHES_FILE):
            backup_file = f"{SENT_HASHES_FILE}.corrupt_backup"
            try:
                os.rename(SENT_HASHES_FILE, backup_file)
                print(f"  📁 Backed up corrupt file to {backup_file}")
            except:
                pass
        return set()
    except Exception as e:
        print(f"  ⚠️ Error reading sent_hashes.json: {e}")
        return set()

def save_sent_hashes(hashes_set):
    """Save sent hashes safely"""
    try:
        with open(SENT_HASHES_FILE, "w", encoding="utf-8") as f:
            json.dump(list(hashes_set), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  ❌ Error saving sent_hashes: {e}")

# ================== Check All Sites ==================
def check_all_sites():
    global updates_history
    sent_hashes = load_sent_hashes()
    new_updates = []
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for updates...")
    
    for site in WEBSITES:
        print(f"  🔍 {site['name']}...")
        try:
            news_items = site["custom_function"]()
            
            for item in news_items:
                unique_string = f"{site['name']}_{item['title']}_{item.get('pub_date', '')}"
                item_hash = hashlib.md5(unique_string.encode()).hexdigest()
                
                if item_hash not in sent_hashes:
                    update = {
                        "id": item_hash,
                        "site": site['name'],
                        "icon": site['icon'],
                        "title": item['title'],
                        "link": item['link'],
                        "pub_date": item['pub_date'],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    new_updates.append(update)
                    sent_hashes.add(item_hash)
                    print(f"    ✅ New: {item['title'][:50]}...")
                    
                    # 🔔 Telegram ला नवीन update पाठवा (IMMEDIATE)
                    telegram_msg = format_telegram_message(update)
                    send_telegram_message(telegram_msg)
                    
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    if new_updates:
        updates_history = new_updates + updates_history
        updates_history = updates_history[:100]
        save_sent_hashes(sent_hashes)
        print(f"  📊 Total {len(new_updates)} new updates found!")
        print(f"  📨 Telegram वर {len(new_updates)} notifications पाठवल्या!")
    else:
        print("  📭 No new updates found")
    
    return new_updates

# ================== Flask Routes ==================
@app.route('/')
def dashboard():
    return render_template('dashboard.html', updates=updates_history, websites=WEBSITES)

@app.route('/api/updates')
def api_updates():
    return jsonify({
        "updates": updates_history,
        "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_websites": len(WEBSITES)
    })

@app.route('/api/check-now')
def api_check_now():
    new_updates = check_all_sites()
    return jsonify({"success": True, "new_count": len(new_updates), "updates": new_updates})

# ================== Scheduler ==================
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_all_sites, trigger="interval", minutes=5)
scheduler.start()

# ================== Main ==================
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Education News Bot सुरू होत आहे...")
    print("📱 Web Dashboard: http://localhost:5000")
    print("⏰ Updates दर 5 मिनिटांनी check होतील")
    print(f"📊 Websites: {len(WEBSITES)}")
    
    # Telegram Bot status
    if TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        print("🤖 Telegram Bot: ✅ सक्रिय")
        # Test message
        send_telegram_message("✅ *Education News Bot सुरू झाला आहे!*\n\nनवीन शैक्षणिक सूचना आल्या की तुम्हाला येथे notification मिळेल.")
    else:
        print("🤖 Telegram Bot: ⚠️ निष्क्रिय (Token set नाही)")
    print("=" * 60)
    
    # पहिल्यांदा check करा
    check_all_sites()
    
    app.run(debug=False, host='0.0.0.0', port=5000)