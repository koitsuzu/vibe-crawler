import cloudscraper
from bs4 import BeautifulSoup
import json
import os

import time

def crawl_kktix(max_pages=3):
    print(f"正在啟動 KKTIX 爬蟲 (預計爬取 {max_pages} 頁)...")
    scraper = cloudscraper.create_scraper()
    base_url = "https://kktix.com/events"
    all_events = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        print(f"正在爬取第 {page} 頁: {url}")
        
        try:
            # 加入 Referer 模擬正常瀏覽行為
            headers = {'Referer': 'https://kktix.com/events'} if page > 1 else {}
            response = scraper.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"第 {page} 頁請求失敗，狀態碼: {response.status_code}")
                # 如果是 403，顯示一下開頭內容以便除錯
                if response.status_code == 403:
                    print(f"錯誤內容預覽: {response.text[:200]}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尋找所有活動項目 (li)
            # KKTIX 頁面項目通常在 class 包含 type- 的 li 中
            items = soup.find_all('li', class_=lambda x: x and x.startswith('type-'))
            
            if not items:
                print(f"第 {page} 頁沒有找到活動，停止爬取。")
                break
                
            for item in items:
                link_tag = item.find('a', class_='cover')
                if not link_tag:
                    continue
                
                event_url = link_tag['href']
                
                # 活動名稱
                title_tag = item.find('h2')
                name = title_tag.text.strip() if title_tag else "無名稱"
                
                # 日期
                date_tag = item.find('span', class_='date')
                date = date_tag.text.strip() if date_tag else "無日期"
                
                # 狀態
                status_tag = item.find('span', class_='fake-btn')
                status = status_tag.text.strip() if status_tag else "未知狀態"
                
                all_events.append({
                    "名稱": name,
                    "日期": date,
                    "網址": event_url,
                    "狀態": status
                })
            
            print(f"第 {page} 頁完成，目前累計 {len(all_events)} 個活動。")
            
            # 稍微停頓，避免請求過快
            if page < max_pages:
                time.sleep(3)

        except Exception as e:
            print(f"爬取第 {page} 頁時發生錯誤: {e}")
            break
            
    # 輸出成 JSON
    output_file = "events.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)
    
    print(f"--- 爬取完成 ---")
    print(f"總共爬取 {len(all_events)} 個活動，已儲存至 {output_file}")
    return all_events

if __name__ == "__main__":
    crawl_kktix(max_pages=3)
