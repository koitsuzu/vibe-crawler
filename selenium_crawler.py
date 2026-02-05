# /// script
# dependencies = [
#   "selenium>=4.40.0",
#   "selenium-stealth",
#   "requests",
# ]
# ///

import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

# ================= 配置區域 =================
# 在此填入您的 Discord Webhook 網址
DISCORD_WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1468798065900257351/Avbn5GcBK5TP9YIdWfCYeRmueRkcSZ4aq0aqJN9-Iq5mMzodVVSurNBhZt-z087hSqY0" 

# 要盯的網址清單 (可以放 5 個或更多)
TARGET_URLS = [
    "https://kktix.com/events/69aeba2f/registrations/new",
    "https://kktix.com/events/a3e28733/registrations/new",
    "https://kktix.com/events/080bd3e0/registrations/new",
    # 您可以在此繼續貼上其他網址
]

# 監控間隔 (秒)，預設 10 分鐘 = 600 秒
MONITOR_INTERVAL = 600
# ===========================================

def send_discord_notification(activity_name, available_tickets, url):
    """發送 Discord 通知"""
    if not DISCORD_WEBHOOK_URL:
        print(f"!!! [提醒] 未設定 Discord Webhook，無法發送通知。")
        return

    content = f" **KKTIX 票務異動通知**\n**活動名稱**: {activity_name}\n"
    content += "**偵測到可用區位**:\n"
    for t in available_tickets:
        content += f"- {t['區位']} ({t['狀態']})\n"
    content += f"\n**立即前往**: {url}"

    payload = {"content": content}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"Successfully notified Discord for {activity_name}")
        else:
            print(f"Failed to notify Discord: {response.status_code}")
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

def init_driver():
    """初始化瀏覽器 (使用 Stealth 模式)"""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # 如果不想要看到視窗，可以開啟 headless
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    stealth(driver,
        languages=["zh-TW", "zh"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver

def scan_kktix(driver, url):
    """掃描單一網址的狀態"""
    print(f"\n正在掃描: {url}")
    driver.get(url)
    
    # 處理彈窗
    time.sleep(2)
    try:
        abort_btn = driver.find_elements(By.XPATH, "//button[contains(text(), '暫時不要') or contains(text(), 'No for now') or contains(@class, 'btn-abort')]")
        if abort_btn:
            abort_btn[0].click()
            time.sleep(1)
    except:
        pass

    # 等待載入
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "ticket-unit")))
    except:
        print("等待超時或無票區位。")
        return "未知活動", []

    # 獲取活動名稱
    try:
        activity_name = driver.title.split('- KKTIX')[0].strip()
    except:
        activity_name = "KKTIX 活動"

    # 解析區位
    ticket_rows = driver.find_elements(By.CLASS_NAME, "ticket-unit")
    found_tickets = []
    
    for row in ticket_rows:
        try:
            name = row.find_element(By.CLASS_NAME, "ticket-name").text.strip()
            status_text = row.get_attribute("innerText").replace("\n", " ").strip()
            
            # 判定狀態
            has_comp = False
            if row.find_elements(By.TAG_NAME, "select") or \
               row.find_elements(By.CLASS_NAME, "plus") or \
               row.find_elements(By.XPATH, ".//input[@type='text' or @type='number']"):
                has_comp = True
            
            if has_comp:
                status = "有票"
            elif "需要資格" in status_text:
                status = "需要資格"
            elif "尚未開賣" in status_text or "尚未開始" in status_text:
                status = "尚未開賣"
            else:
                status = "已售完"

            # 只要不是已售完，都記錄下來
            if status != "已售完":
                found_tickets.append({"區位": name, "狀態": status})
                print(f"  [!] 發現可用: {name} ({status})")
        except:
            continue
            
    return activity_name, found_tickets

def main():
    print(f"=== KKTIX 多網址監控啟動 (間隔: {MONITOR_INTERVAL}秒) ===")
    
    # 儲存每個網址上一次偵測到的可用票券清單，避免重複通知
    last_state = {}

    while True:
        driver = None
        try:
            # 每輪掃描重新啟動瀏覽器，掃描完就關閉，節省資源
            driver = init_driver()
            current_round_results = []
            
            for url in TARGET_URLS:
                if not url or not url.strip(): continue
                
                activity_name, available = scan_kktix(driver, url)
                
                # 判定是否需要發送通知
                current_ticket_names = {t['區位'] for t in available}
                previous_ticket_names = last_state.get(url, set())
                
                if available and current_ticket_names != previous_ticket_names:
                    print(f"新增可用票券! 發送通知中...")
                    send_discord_notification(activity_name, available, url)
                    last_state[url] = current_ticket_names
                elif not available:
                    last_state[url] = set() # 回到全售完狀態
                
                current_round_results.append({
                    "url": url,
                    "name": activity_name,
                    "available": available
                })

            # 更新 JSON 結果
            with open("inventory_status.json", "w", encoding="utf-8") as f:
                json.dump(current_round_results, f, ensure_ascii=False, indent=4)

            print(f"\n一輪掃描完成。")
            
        except Exception as e:
            print(f"本輪執行發生錯誤: {e}")
        finally:
            if driver:
                print("關閉瀏覽器，進入休眠...")
                try:
                    driver.quit()
                except:
                    pass

        print(f"休息 {MONITOR_INTERVAL} 秒後進行下一輪...")
        try:
            time.sleep(MONITOR_INTERVAL)
        except KeyboardInterrupt:
            print("\n使用者停止監控。")
            break

if __name__ == "__main__":
    main()
