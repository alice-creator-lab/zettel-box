# 卡片盒

以原子化卡片與雙向連結思考的筆記工具。介面參考 Heptabase 的空間白板，方法取自《卡片盒筆記》（How to Take Smart Notes）。

單一 `index.html`，純前端，資料存於裝置的 IndexedDB，可加到 iPhone 主畫面離線使用。

線上版：https://alice-creator-lab.github.io/zettel-box/

## 三個原則

1. **原子化**：一張卡只講一個想法。
2. **用自己的話**：正文是你重寫過的句子，不是剪貼。
3. **連結要有理由**：每條連結都寫一句「為什麼相關」。

## 功能

**收件匣**：一開就打字的捕捉框，零分類負擔。整理時按「升級為卡片」，選永久／文獻／索引。

**卡片庫**：搜尋標題、內容、標籤；按類型篩選；點標籤可直接跳到該標籤的搜尋結果。

**白板**：自由畫布。單指拖卡片、單指拖空白處平移、雙指縮放。長按卡片開啟選單（編輯／連結／移出白板／刪除）。同一張卡可出現在多塊白板。

**連結**：白板下方「連結」→ 點兩張卡 → 寫下理由。也可以在正文寫 `[[卡片標題]]`，儲存時自動建立連結。卡片詳情底部列出「這張卡連到」與「連到這張卡」。

**索引卡**：正文每行寫 `[[卡片標題]]` 加一句說明，即成一張主題地圖（MOC）。

**備份**：更多 → 匯出備份（JSON，完整可還原）／匯出 Markdown（純文字，可讀）。匯入會取代現有資料。

## 資料模型

```js
card  = { id, type: 'fleeting'|'literature'|'permanent'|'index', title, body, tags[], source, created, updated }
link  = { id, from, to, why, auto, created }
board = { id, name, created }
pos   = { id: 'boardId|cardId', boardId, cardId, x, y }
```

`pos` 只記錄「某張卡在某塊白板的座標」，因此卡片與白板是多對多。

## 開發

```bash
python3 -m http.server 8811      # http://127.0.0.1:8811/
python3 tools/shot.py            # 手機尺寸自動流程測試 + 截圖（輸出至 shots/）
python3 tools/make_icons.py      # 重新產生 PWA 圖示
```

`tools/shot.py` 會實際跑一輪：寫兩則閃念 → 升級 → 編輯與 wiki 連結 → 白板加卡與拖曳 → 連結模式寫理由 → 重新載入驗證 IndexedDB → 匯入備份 → 深色模式 → 長按選單，並收集 JavaScript 錯誤。

## 已知限制

- 資料只存在目前這台裝置的瀏覽器，換裝置需自行匯出／匯入。
- 清除 Safari 網站資料會一併清除筆記，請定期匯出備份。
- 白板連結線只在兩張卡同時出現在同一塊白板時顯示。

## 版本

- 1.0.0：收件匣、卡片庫、白板、雙向連結（含理由）、索引卡、搜尋與標籤、JSON／Markdown 匯出、離線 PWA。
