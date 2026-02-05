# KKTIX 多網址自動化監控爬蟲 (Selenium + Discord)

這是一個基於 Selenium 的 KKTIX 購票網頁監控工具，支援一次監控多個網址，並在偵測到「有票」、「需要資格」或「尚未開賣」時，自動透過 Discord Webhook 發送通知。

## 功能特點

- **多網址循環監控**: 可自訂網址清單與掃描間隔。
- **自動化處理**: 自動關閉 KKTIX 登入提示與公告彈窗。
- **智慧狀態辨識**: 精確區分有票、需要資格、尚未開賣、已售完。
- **即時通知**: 整合 Discord Webhook，狀態變動時第一時間推播。
- **高度穩定**: 使用 `selenium-stealth` 規避機器人偵測。
- **資源優化**: 監控期間自動開關瀏覽器，不佔用系統資源。

## 安裝與執行

### 1. 安裝環境
本專案建議使用 [uv](https://github.com/astral-sh/uv) 進行管理。請先確保電腦已安裝 Chrome 瀏覽器。

### 2. 下載並安裝依賴
```bash
git clone <repository_url>
cd event_crawler
uv sync
```

### 3. 設定監控參數
編輯 `selenium_crawler.py` 頂部的配置區域：

```python
# --- 配置區域 ---
DISCORD_WEBHOOK_URL = "您的_DISCORD_WEBHOOK_網址"
TARGET_URLS = [
    "https://kktix.com/events/example1/registrations/new",
    "https://kktix.com/events/example2/registrations/new",
]
MONITOR_INTERVAL = 600  # 每 10 分鐘偵測一次
# ---------------
```

### 4. 啟動監控
```bash
uv run selenium_crawler.py
```

## 注意事項

- **驗證碼**: 若 KKTIX 彈出人機驗證 (CAPTCHA)，請在開啟的瀏覽器視窗中手動完成。
- **頻率**: 建議間隔不要低於 1 分鐘，以免觸發頻率限制。
- **免責聲明**: 本工具僅供學術與技術研究使用，請遵守 KKTIX 服務條款。
