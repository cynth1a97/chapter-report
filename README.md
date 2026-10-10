# chapter-report

一個給 Claude Code 用的 skill：把**一章課本或一篇論文**（PDF，掃描版也可以）加上 **Critical Form**（Word 檔），做成一整套讀書報告：

- **上台版簡報**：16:9 網頁投影片，方向鍵翻頁
- **詳細版網頁**：一頁式、手機也能看，分成「報告內容」和「Critical Form」兩個分頁
- **入口頁**：選擇要看簡報還是詳細版
- （選用）**部署到 Cloudflare Pages**，拿到公開網址，組員可以直接在網頁上改字

視覺風格由 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 產生 3 個預覽讓你挑，所以要先裝它。

## 安裝

```bash
git clone https://github.com/zarazhangrui/frontend-slides.git ~/.claude/skills/frontend-slides
git clone https://github.com/cynth1a97/chapter-report.git ~/.claude/skills/chapter-report
```

裝好後開一個新的 Claude Code 對話就能用。

## 使用

把章節 PDF 和 Critical Form 拖進對話，然後說：

```
用 chapter-report 幫我做這一章的讀書報告。
報告人：〔學號〕〔姓名〕、〔學號〕〔姓名〕
報告時間大約 10 分鐘
```

Claude 會：讀完整章 → 規劃簡報大綱 → 給你 3 個風格挑 → 做出簡報、詳細版、入口頁 → 逐頁檢查排版。

想放上網路、讓組員一起改，再說：

```
幫我部署到 Cloudflare Pages，並開啟線上編輯
```

（需要免費的 Cloudflare 帳號，登入步驟 Claude 會帶你做。）

## 小提醒

- 請 AI 對照原文檢查內容，特別是你貼了別的 AI 整理的摘要時。
- 線上編輯開放給拿到網址的所有人，修改次數無限；停手 5 秒或點到別處才存檔。每個人每段編輯會自動備份一次（保留最近 30 份），可以還原。
- 要增減頁面或換版型時，先請 AI 把線上改過的文字併回原始檔，再重新產生，不然修改會跑到錯的位置。

## 檔案

| 檔案 | 用途 |
|---|---|
| `SKILL.md` | 給 AI 看的完整流程 |
| `scripts/pdf_pages.py` | 掃描版 PDF 轉成一頁一張圖 |
| `scripts/read_docx.py` | 讀出 Critical Form 的文字 |
| `scripts/stamp.py` | 幫頁面加上版本編號 |
| `templates/` | 簡報產生器、詳細版、入口頁、線上編輯程式、部署設定 |

## 授權

MIT。投影片的固定 16:9 版型與風格探索流程來自 frontend-slides（MIT, Zara Zhang）。
