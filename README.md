# UNLIGHT:Revive R卡碎片分析器

這是一個為《UNLIGHT:Revive》遊戲設計的桌面應用程式，旨在幫助玩家分析和優化 R 卡的製作方案，最小化碎片消耗。

## 功能特色

* **碎片存量管理：** 輸入您當前擁有的記憶、時間、靈魂、生命和死亡碎片數量。
* **碎片權重設定：** 為每種碎片設定重要程度，程式將根據您的權重找到「成本效益」最佳的製作組合。
* **R卡製作分析：** 程式會自動計算並推薦製作三張 R 卡的最佳方案。
* **進階角色選擇：** 允許您自定義可供分析的 R 卡角色列表，包含或排除特定角色，也顯示「(無資料)」的角色。
* **設定持久化：** 自動保存您的碎片數量、權重和角色選擇，下次啟動時無需重複輸入。

## 如何使用 (針對已打包的 .exe 執行檔)

1.  從 [GitHub Release 頁面連結，待填寫] 下載最新的 `UNLIGHT_R卡分析器.exe` (或類似名稱的執行檔)。
2.  雙擊執行檔啟動應用程式。
3.  在主介面輸入您目前的碎片存量，並設定各碎片的權重。
4.  (選填) 點擊「進階設定：可製作角色」按鈕，選擇您希望納入分析範圍的 R 卡角色。
5.  點擊「分析最佳製作方案 (製作3張R卡)」按鈕，查看結果。
6.  您的設定將自動保存，下次開啟程式時會自動載入。

## 如何從原始碼運行 (開發者/進階用戶)

1.  **克隆儲存庫：**
    ```bash
    git clone [您的 GitHub 儲存庫 URL]
    cd [您的儲存庫名稱]
    ```
2.  **創建並激活虛擬環境 (建議)：**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  **安裝依賴：**
    ```bash
    pip install pandas tk
    ```
4.  **運行應用程式：**
    ```bash
    python ULR.py
    ```

## 如何打包成 .exe (開發者)

您可以使用 PyInstaller 將此應用程式打包為獨立的 `.exe` 檔案。

1.  **安裝 PyInstaller：**
    ```bash
    pip install pyinstaller
    ```
2.  **下載 UPX (可選，用於減小檔案大小)：**
    訪問 [https://upx.github.io/](https://upx.github.io/) 下載 UPX，並將 `upx.exe` 放在您的 PATH 中或專案目錄下。
3.  **執行打包命令：**
    ```bash
    pyinstaller --onefile --windowed --upx-dir . --hidden-import=pandas._libs.tslibs.timestamps --hidden-import=pandas._libs.interval ULR.py
    ```
    生成的執行檔會在 `dist` 資料夾內。

## 許可證 (License)

[在此處填寫您的許可證資訊，例如：MIT License]

## 貢獻

歡迎任何形式的貢獻！如果您有任何建議或發現錯誤，請隨時提出 Issue 或提交 Pull Request。
