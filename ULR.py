import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import pandas as pd
import itertools # 用於產生所有R卡組合
from io import StringIO # 用於從字串讀取CSV數據
import math # 用於計算向上取整
import json # 用於設定持久化儲存
import os # 用於檢查檔案是否存在

# --- 全域變數或常數設定 ---
# 碎片名稱 (從提供的CSV標頭直接獲取)
FRAGMENT_NAMES = ["記憶的碎片", "時間的碎片", "靈魂的碎片", "生命的碎片", "死亡的碎片"]

# 權重映射
WEIGHT_MAP = {
    "隨便用": 1,
    "不重要": 2,
    "重要": 3,
    "很重要": 4,
    "不能用": 5
}

# 這是你提供的CSV數據，作為程式內建的R卡製作數據
# 將其儲存在一個多行字串中
R_CARD_CSV_DATA = """
名字,記憶的碎片,時間的碎片,靈魂的碎片,生命的碎片,死亡的碎片,已上線
艾伯李斯特,10,10,10,10,-,是
艾依查庫,10,15,5,-,10,是
古魯瓦爾多,10,10,10,-,10,是
阿貝爾,15,10,5,10,-,是
利恩,10,10,10,-,10,是
庫勒尼西,5,10,15,10,-,是
傑多,10,10,10,-,10,是
阿奇波爾多,5,15,10,10,-,是
布列依斯,10,10,10,10,-,是
雪莉,5,10,15,-,10,是
艾茵,10,5,15,10,-,是
伯恩哈德,15,5,10,-,10,是
弗雷特里西,15,5,10,10,-,是
瑪格莉特,10,5,15,-,10,是
多妮妲,15,10,5,-,10,是
史普拉多,15,5,10,10,-,是
貝琳達,5,10,15,-,10,是
羅索,15,10,5,-,10,是
馬庫斯,15,5,10,10,-,是
艾妲,10,10,10,10,-,是
梅倫,15,5,5,15,-,是
薩爾卡多,10,10,10,10,-,是
蕾格烈芙,10,10,10,10,-,是
里斯,15,5,10,10,-,是
米利安,5,10,15,-,10,是
沃肯,5,10,10,-,15,是
帕茉,15,15,5,5,-,是
阿修羅,10,10,-,10,10,是
佛羅倫斯,10,10,-,10,10,是
布朗寧,20,10,-,5,5,是
瑪爾瑟斯,15,10,5,-,10,是
路德,25,5,5,-,5,是
魯卡,10,10,10,10,-,是
史塔夏,10,10,10,10,-,是
沃蘭德,15,15,5,5,-,是
C.C.,10,15,5,-,10,是
柯布,5,5,5,-,25,是
伊芙琳,15,15,5,5,-,否
布勞,5,15,15,5,-,是
凱倫貝克,10,10,10,10,-,否
音音夢,10,15,5,-,10,否
康拉德,5,5,15,-,15,否
碧姬媞,15,5,5,-,15,否
庫恩,5,15,15,-,5,否
夏洛特,10,10,10,10,-,是
泰瑞爾,5,-,5,15,15,否
露緹亞,15,5,5,15,-,否
威廉,10,10,10,-,10,否
梅莉,5,15,15,5,-,否
古斯塔夫,5,10,10,-,15,否
尤莉卡,5,10,-,10,15,否
林奈烏斯,-,5,5,15,15,否
娜汀,10,10,10,-,10,否
迪諾,5,15,5,15,,否
奧蘭,,, ,,,否
諾伊庫洛姆,10,10,10,10,-,否
初葉,15,5,10,10,-,否
希拉莉,15,10,5,10,,否
克洛維斯,10,10,10,-,10,否
艾莉絲泰莉雅,10,10,10,10,-,否
雨果,10,15,5,-,10,否
艾莉亞娜,10,10,10,-,10,否
格雷高爾,,, ,,,否
蕾塔,5,10,15,-,10,否
伊普西隆,15,5,10,10,-,否
波蕾特,10,10,10,-,10,否
尤哈尼,10,10,10,-,-,否
諾艾菈,5,10,15,-,-,否
勞爾,5,15,-,10,-,否
潔米,,, ,,,否
瑟法斯,5,15,-,10,-,否
維若妮卡,-,10,10,10,-,否
里卡多,,, ,,,否
"""

# R卡製作成本數據 (將從CSV載入)
R_CARD_RECIPES_FULL = pd.DataFrame() # 載入所有R卡數據
R_CARD_RECIPES_FILTERED = pd.DataFrame() # 根據使用者選擇過濾後的數據

# 配置檔案名稱
CONFIG_FILE = 'config.json'

class AdvancedSettingsDialog(Toplevel):
    def __init__(self, parent, initial_selected_cards):
        super().__init__(parent)
        self.parent = parent
        self.title("進階設定：選擇可製作角色")
        # 設置視窗為模態，阻止與主視窗互動
        self.transient(parent)
        self.grab_set()

        # 儲存核取方塊的狀態
        self.checkbox_vars = {}
        self.selected_cards_on_close = initial_selected_cards.copy() # 初始化為傳入的當前選擇

        self.create_widgets()

        # 確保視窗在中心
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


    def create_widgets(self):
        # 標題
        ttk.Label(self, text="請勾選你擁有或可製作的R卡角色：", font=('Arial', 10, 'bold')).pack(pady=10)

        # 直接使用 Frame 來包含核取方塊，並使用 grid 佈局
        checkbox_frame = ttk.Frame(self)
        checkbox_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # 設定每行顯示的角色數量，從 3 列改為 4 列
        NUM_COLUMNS = 4
        
        # 配置列寬，讓輸入框和下拉選單更好地對齊，實現響應式佈局
        for col in range(NUM_COLUMNS):
            checkbox_frame.grid_columnconfigure(col, weight=1)
        
        # 填充核取方塊
        r_card_names = R_CARD_RECIPES_FULL.index.tolist()
        for i, r_card_name in enumerate(r_card_names):
            row = i // NUM_COLUMNS
            col = i % NUM_COLUMNS
            
            display_name = r_card_name
            # 檢查該R卡是否為「無資料」R卡 (所有碎片消耗為0)
            if r_card_name in R_CARD_RECIPES_FULL.index:
                recipe_data = R_CARD_RECIPES_FULL.loc[r_card_name, FRAGMENT_NAMES]
                # 將非數值（如'-'）轉為0，並檢查總和
                numeric_recipe_data = pd.to_numeric(recipe_data, errors='coerce').fillna(0)
                if numeric_recipe_data.sum() == 0:
                    display_name += " (無資料)"

            var = tk.BooleanVar(value=r_card_name in self.selected_cards_on_close)
            cb = ttk.Checkbutton(checkbox_frame, text=display_name, variable=var)
            cb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            self.checkbox_vars[r_card_name] = var
        
        # 調整視窗高度以容納所有角色
        expected_rows = math.ceil(len(r_card_names) / NUM_COLUMNS)
        # 調整 min_height 考量 4 列和標題/按鈕高度
        min_height = 100 + (expected_rows * 25) # 100 for title/buttons, 25 per checkbox row
        self.geometry(f"600x{max(500, min_height)}") # 最小高度500，並調整寬度適應4列

        # 按鈕框架
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="儲存設定", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=self.destroy).pack(side="right", padx=5)

        # 設定視窗關閉時的行為
        self.protocol("WM_DELETE_WINDOW", self.destroy)
    
    def save_settings(self):
        # 收集所有被勾選的角色
        self.selected_cards_on_close = []
        for r_card_name, var in self.checkbox_vars.items():
            if var.get():
                self.selected_cards_on_close.append(r_card_name)
        
        # 通知父視窗更新篩選後的R卡列表，並觸發儲存
        self.parent.update_filtered_r_cards(self.selected_cards_on_close, show_message=True)
        self.destroy() # 關閉設定視窗


class ULFragmentAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UNLIGHT:Revive R卡碎片分析器")
        self.geometry("700x700") # 調整視窗大小以容納更多內容

        # 設定風格
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # 儲存目前使用者選擇的可製作R卡列表
        self.selected_craftable_r_cards = [] 
        # 儲存載入的碎片存量和權重，用於初始化UI
        self._loaded_fragment_counts = {}
        self._loaded_fragment_weights = {}

        self.create_widgets()
        # 載入R卡數據
        self.load_r_card_data(R_CARD_CSV_DATA)
        # 載入配置檔案，覆蓋預設值或CSV初始值
        self._load_config()

        # 設定應用程式關閉時的處理
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        messagebox.showinfo("程式啟動", "R卡製作數據與上次設定已載入，並已預設勾選'已上線'角色（若設定中無記錄）。")


    def create_widgets(self):
        # --- 碎片輸入框架 ---
        input_frame = ttk.LabelFrame(self, text="碎片存量與權重", padding="10")
        input_frame.pack(padx=10, pady=10, fill="x")

        self.fragment_entries = {}
        self.fragment_weights = {}

        # 標題行
        ttk.Label(input_frame, text="碎片名稱", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(input_frame, text="目前存量", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(input_frame, text="權重 (越珍貴越高)", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=2)

        for i, name in enumerate(FRAGMENT_NAMES):
            row = i + 1 # 從第二行開始，第一行是標題

            ttk.Label(input_frame, text=f"{name}:").grid(row=row, column=0, sticky="w", pady=2)

            # 存量輸入框
            entry = ttk.Entry(input_frame, width=10)
            entry.grid(row=row, column=1, padx=5, pady=2)
            # 嘗試從載入的配置中設定預設值，否則設為0
            entry.insert(0, str(self._loaded_fragment_counts.get(name, 0))) 
            self.fragment_entries[name] = entry

            # 權重選擇下拉選單
            weight_var = tk.StringVar(self)
            # 嘗試從載入的配置中設定預設值，否則設為"重要"
            initial_weight_key = self._loaded_fragment_weights.get(name, "重要")
            weight_var.set(initial_weight_key) 
            weight_dropdown = ttk.Combobox(input_frame, textvariable=weight_var,
                                            values=list(WEIGHT_MAP.keys()), state="readonly", width=12)
            weight_dropdown.grid(row=row, column=2, padx=5, pady=2)
            self.fragment_weights[name] = weight_var
            
        # 配置列寬，讓輸入框和下拉選單更好地對齊
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(2, weight=1)

        # --- 按鈕框架 (分析 & 進階設定) ---
        button_container = ttk.Frame(self)
        button_container.pack(pady=10)

        analyze_button = ttk.Button(button_container, text="分析最佳製作方案 (製作3張R卡)", command=self.analyze_fragments)
        analyze_button.pack(side="left", padx=5)

        settings_button = ttk.Button(button_container, text="進階設定：可製作角色", command=self.open_advanced_settings)
        settings_button.pack(side="right", padx=5)

        # --- 結果顯示區 ---
        result_frame = ttk.LabelFrame(self, text="分析結果", padding="10")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.result_text = tk.Text(result_frame, wrap="word", height=15, width=80, font=('Arial', 10))
        self.result_text.pack(side="left", expand=True, fill="both") # 滾動條修正點1

        # 滾動條修正點2: 滾動條依附於 result_frame
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y") # 滾動條修正點3

    def _save_config(self):
        """將當前碎片數量、權重和選擇的角色儲存到配置檔案"""
        config_data = {}
        # 儲存碎片數量
        current_fragments = {}
        for name in FRAGMENT_NAMES:
            try:
                current_fragments[name] = int(self.fragment_entries[name].get())
            except ValueError:
                current_fragments[name] = 0 # 避免錯誤輸入導致儲存失敗
        config_data['fragment_counts'] = current_fragments

        # 儲存碎片權重
        current_weights = {}
        for name in FRAGMENT_NAMES:
            current_weights[name] = self.fragment_weights[name].get()
        config_data['fragment_weights'] = current_weights

        # 儲存已選擇的角色
        config_data['selected_r_cards'] = self.selected_craftable_r_cards

        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            # print("設定已成功儲存。")
        except Exception as e:
            print(f"儲存設定時發生錯誤: {e}")
            messagebox.showerror("儲存錯誤", f"無法儲存設定：\n{e}")

    def _load_config(self):
        """從配置檔案載入碎片數量、權重和選擇的角色"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 載入碎片數量
                self._loaded_fragment_counts = config_data.get('fragment_counts', {})
                for name, entry in self.fragment_entries.items():
                    entry.delete(0, tk.END)
                    entry.insert(0, str(self._loaded_fragment_counts.get(name, 0)))

                # 載入碎片權重
                self._loaded_fragment_weights = config_data.get('fragment_weights', {})
                for name, var in self.fragment_weights.items():
                    # 確保載入的權重值存在於 WEIGHT_MAP 的鍵中
                    if self._loaded_fragment_weights.get(name) in WEIGHT_MAP:
                        var.set(self._loaded_fragment_weights.get(name))
                    else:
                        var.set("重要") # 載入無效值時使用預設

                # 載入已選擇的角色
                loaded_selected_cards = config_data.get('selected_r_cards', [])
                if loaded_selected_cards: # 如果配置檔案中有記錄，則使用記錄
                    # 篩選掉CSV中不存在的角色名，避免錯誤
                    valid_selected_cards = [
                        card for card in loaded_selected_cards if card in R_CARD_RECIPES_FULL.index
                    ]
                    self.selected_craftable_r_cards = valid_selected_cards
                    # 更新篩選後的R卡數據，不顯示提示訊息
                    self.update_filtered_r_cards(self.selected_craftable_r_cards, show_message=False)
                else: # 如果配置檔案中沒有記錄，則使用CSV的'已上線'預設值
                    # load_r_card_data 已經初始化了 self.selected_craftable_r_cards
                    # 這裡只需確保 R_CARD_RECIPES_FILTERED 是正確的
                    self.update_filtered_r_cards(self.selected_craftable_r_cards, show_message=False)
                
                # print("設定已成功載入。")

            except json.JSONDecodeError:
                print("配置檔案損壞或格式不正確，將使用預設設定。")
                messagebox.showwarning("載入錯誤", "配置檔案損壞或格式不正確，將使用預設設定。")
                self._reset_default_settings_from_csv() # 重新從CSV預設值初始化
            except Exception as e:
                print(f"載入設定時發生錯誤: {e}，將使用預設設定。")
                messagebox.showwarning("載入錯誤", f"載入設定時發生錯誤：\n{e}\n將使用預設設定。")
                self._reset_default_settings_from_csv() # 重新從CSV預設值初始化
        else:
            print("未找到配置檔案，將使用預設設定。")
            # 第一次運行時，selected_craftable_r_cards 已經由 load_r_card_data 初始化為 '已上線' 角色
            # 這裡只需確保 R_CARD_RECIPES_FILTERED 是正確的
            self.update_filtered_r_cards(self.selected_craftable_r_cards, show_message=False)
    
    def _reset_default_settings_from_csv(self):
        """當配置檔案載入失敗時，將設定重設為從CSV中讀取的預設值"""
        # 重設碎片數量為0
        for name, entry in self.fragment_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        # 重設碎片權重為「重要」
        for name, var in self.fragment_weights.items():
            var.set("重要")
        # 重設可製作角色為CSV中的「已上線」角色
        if '已上線' in R_CARD_RECIPES_FULL.columns:
            self.selected_craftable_r_cards = R_CARD_RECIPES_FULL[R_CARD_RECIPES_FULL['已上線'] == '是'].index.tolist()
        else:
            self.selected_craftable_r_cards = R_CARD_RECIPES_FULL.index.tolist()
        self.update_filtered_r_cards(self.selected_craftable_r_cards, show_message=False)


    def on_closing(self):
        """應用程式關閉時的處理，儲存設定並銷毀視窗"""
        self._save_config()
        self.destroy()


    def load_r_card_data(self, csv_content):
        """
        從提供的CSV內容載入R卡製作配方。
        CSV應包含'名字'（R卡名稱）以及五種碎片欄位。
        """
        global R_CARD_RECIPES_FULL
        try:
            csv_file = StringIO(csv_content)
            df = pd.read_csv(csv_file)
            
            # 填充所有NaN（空白格）為0，並將'-'替換為0
            df = df.replace('-', 0)
            df = df.fillna(0) 

            # 確保碎片欄位是數值類型
            for frag_name in FRAGMENT_NAMES:
                if frag_name in df.columns:
                    df[frag_name] = pd.to_numeric(df[frag_name], errors='coerce').fillna(0).astype(int)
                else:
                    messagebox.showwarning("CSV錯誤", f"CSV中缺少碎片欄位: '{frag_name}'。請檢查CSV標頭。")
                    return # 如果缺少關鍵碎片欄位，則無法繼續

            # 將'名字'欄位設為索引
            if '名字' in df.columns:
                R_CARD_RECIPES_FULL = df.set_index('名字')
                
                # 初始化 self.selected_craftable_r_cards 根據 '已上線' 欄位
                # 此處設定為預設值，如果配置檔案存在會覆寫
                if '已上線' in R_CARD_RECIPES_FULL.columns:
                    self.selected_craftable_r_cards = R_CARD_RECIPES_FULL[R_CARD_RECIPES_FULL['已上線'] == '是'].index.tolist()
                    # R_CARD_RECIPES_FULL = R_CARD_RECIPES_FULL.drop(columns=['已上線']) # 移除此欄位，分析時不需用
                else:
                    # 如果沒有 '已上線' 欄位，預設所有R卡都可製作
                    self.selected_craftable_r_cards = R_CARD_RECIPES_FULL.index.tolist()

                # 初始化過濾後的R卡數據，此處不顯示messagebox
                # update_filtered_r_cards 會在 _load_config 中被呼叫，確保順序
                # self.update_filtered_r_cards(self.selected_craftable_r_cards, show_message=False)

            else:
                messagebox.showerror("CSV錯誤", "CSV中缺少R卡名稱欄位 '名字'。")
                return

        except Exception as e:
            messagebox.showerror("數據載入錯誤", f"載入CSV時發生錯誤：\n{e}\n請檢查CSV格式是否正確。")
            print(f"錯誤：{e}")


    def open_advanced_settings(self):
        """開啟進階設定視窗讓使用者選擇可製作角色"""
        # 傳遞當前選擇的角色列表
        dialog = AdvancedSettingsDialog(self, self.selected_craftable_r_cards)
        self.wait_window(dialog) # 等待設定視窗關閉

    def update_filtered_r_cards(self, new_selected_cards, show_message=True):
        """根據使用者在進階設定中的選擇來更新R卡列表，並觸發設定儲存"""
        global R_CARD_RECIPES_FILTERED
        self.selected_craftable_r_cards = new_selected_cards
        
        if not R_CARD_RECIPES_FULL.empty and self.selected_craftable_r_cards:
            # 從完整的數據中篩選出使用者選擇的角色
            R_CARD_RECIPES_FILTERED = R_CARD_RECIPES_FULL.loc[self.selected_craftable_r_cards]
        else:
            R_CARD_RECIPES_FILTERED = pd.DataFrame() # 如果沒有選擇任何卡片或數據未載入，則為空DataFrame

        if show_message: # 根據參數決定是否顯示訊息框
            messagebox.showinfo("設定更新", f"已更新可製作角色列表，共 {len(self.selected_craftable_r_cards)} 個角色。")
        
        # 每次更新篩選列表後都儲存設定
        self._save_config()


    def analyze_fragments(self):
        self.result_text.delete('1.0', tk.END) # 清空之前的結果

        # 1. 取得使用者輸入
        current_fragments = {}
        fragment_weights_val = {} # 轉換成數值權重
        try:
            for name in FRAGMENT_NAMES:
                count_str = self.fragment_entries[name].get()
                count = int(count_str)
                if count < 0:
                    raise ValueError("碎片存量不能為負數。")
                current_fragments[name] = count

                weight_text = self.fragment_weights[name].get()
                fragment_weights_val[name] = WEIGHT_MAP[weight_text]
        except ValueError as e:
            messagebox.showerror("輸入錯誤", f"請確認所有碎片存量都輸入了有效的數字。\n錯誤: {e}")
            return
        except Exception as e:
            messagebox.showerror("輸入錯誤", f"獲取輸入時發生未知錯誤：{e}")
            return
        
        # 保存當前輸入的碎片數量和權重
        self._save_config()

        if R_CARD_RECIPES_FULL.empty:
            messagebox.showwarning("數據缺失", "R卡製作數據尚未載入。")
            return
            
        if R_CARD_RECIPES_FILTERED.empty:
            self.result_text.insert(tk.END, "目前沒有可製作的R卡角色被選取。\n請進入'進階設定'勾選希望考量的角色。")
            return

        # 2. 核心分析邏輯
        best_combination = None
        min_weighted_cost = float('inf') # 初始化為無限大
        
        # 儲存最佳組合製作後的碎片剩餘量
        best_combo_fragments_left = {} 

        # 取得篩選後的可製作R卡的名稱列表
        available_r_cards = R_CARD_RECIPES_FILTERED.index.tolist()

        if len(available_r_cards) < 3:
            self.result_text.insert(tk.END, f"目前僅有 {len(available_r_cards)} 種R卡在考量範圍內，無法製作3張R卡。\n請進入'進階設定'勾選更多角色。")
            return

        # 產生所有製作3張R卡的組合
        for r_card_combo in itertools.combinations(available_r_cards, 3):
            temp_fragments_needed = {name: 0 for name in FRAGMENT_NAMES}
            current_combo_weighted_cost = 0
            is_possible = True

            # 計算這個組合總共需要的碎片
            for r_card_name in r_card_combo:
                # 確保 recipe_data 僅包含 FRAGMENT_NAMES 中的列
                recipe = R_CARD_RECIPES_FILTERED.loc[r_card_name]
                for frag_name in FRAGMENT_NAMES:
                    # 使用 .get() 並提供預設值 0，處理數據中可能缺失的碎片列
                    needed = recipe.get(frag_name, 0)
                    temp_fragments_needed[frag_name] += needed

            # 檢查當前碎片是否足夠，並計算加權成本
            temp_fragments_left = current_fragments.copy() # 複製一份用於模擬消耗
            for frag_name in FRAGMENT_NAMES:
                needed = temp_fragments_needed[frag_name]
                if temp_fragments_left[frag_name] < needed:
                    is_possible = False
                    break # 碎片不足，這個組合不可行

                # 模擬消耗碎片
                temp_fragments_left[frag_name] -= needed
                
                # 計算加權成本 (只計算實際消耗的碎片的加權成本)
                current_combo_weighted_cost += needed * fragment_weights_val[frag_name]

            if is_possible:
                if current_combo_weighted_cost < min_weighted_cost:
                    min_weighted_cost = current_combo_weighted_cost
                    best_combination = r_card_combo
                    best_combo_fragments_left = temp_fragments_left.copy() # 儲存此時的剩餘碎片

        # 3. 顯示結果
        if best_combination:
            output = f"--- 最佳R卡製作方案 ---\n"
            output += f"總加權消耗 (越低越好): {min_weighted_cost}\n"
            output += "建議製作以下三張R卡：\n"
            
            total_consumed_fragments = {name: 0 for name in FRAGMENT_NAMES}

            for r_card_name in best_combination:
                output += f"\n- 角色：{r_card_name}\n"
                output += "  所需碎片：\n"
                recipe = R_CARD_RECIPES_FILTERED.loc[r_card_name]
                for frag_name in FRAGMENT_NAMES:
                    consumed = recipe.get(frag_name, 0) # 使用 .get()
                    if consumed > 0:
                        output += f"    {frag_name}: {consumed}\n"
                        total_consumed_fragments[frag_name] += consumed

            output += "\n--- 製作總消耗碎片 ---\n"
            for frag_name in FRAGMENT_NAMES:
                if total_consumed_fragments[frag_name] > 0:
                    output += f"- {frag_name}: {total_consumed_fragments[frag_name]}\n"
            
            output += "\n--- 製作後碎片剩餘量 ---\n"
            # 這裡使用 best_combo_fragments_left，它已經是準確的剩餘量
            for frag_name in FRAGMENT_NAMES:
                output += f"- {frag_name}: {best_combo_fragments_left[frag_name]}\n"

            self.result_text.insert(tk.END, output)
        else:
            self.result_text.insert(tk.END, "抱歉，沒有找到符合條件的最佳R卡製作方案。\n可能原因：\n- 碎片存量不足以製作任何三張R卡組合。\n- 權重設定過高，導致沒有符合成本效益的組合。\n- 所選可製作角色數量不足3個。\n\n請檢查碎片存量、調整權重，或進入'進階設定'勾選更多角色。")


def main():
    app = ULFragmentAnalyzer()
    app.mainloop()

if __name__ == "__main__":
    main()
