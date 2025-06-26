import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import pandas as pd
import itertools
from io import StringIO
import math
import json
from pathlib import Path  # 現代化的路徑處理
from typing import Dict, List, Tuple, Optional, Any # 用於型別提示

# --- 常數設定 (Constants) ---
# 使用大寫蛇形命名法來表示常數，提高可讀性
FRAGMENT_NAMES: List[str] = ["記憶的碎片", "時間的碎片", "靈魂的碎片", "生命的碎片", "死亡的碎片"]

WEIGHT_MAP: Dict[str, int] = {
    "隨便用": 1,
    "不重要": 2,
    "重要": 3,
    "很重要": 4,
    "不能用": 5,
}

# 內建R卡製作數據
R_CARD_CSV_DATA: str = """
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
布朗NING,20,10,-,5,5,是
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
迪諾,5,15,5,15,-,否
奧蘭,-,-,-,-,-,否
諾伊庫洛姆,10,10,10,10,-,否
初葉,15,5,10,10,-,否
希拉莉,15,10,5,10,-,否
克洛維斯,10,10,10,-,10,否
艾莉絲泰莉雅,10,10,10,10,-,否
雨果,10,15,5,-,10,否
艾莉亞娜,10,10,10,-,10,否
格雷高爾,-,-,-,-,-,否
蕾塔,5,10,15,-,10,否
伊普西隆,15,5,10,10,-,否
波蕾特,10,10,10,-,10,否
尤哈尼,10,10,10,-,-,否
諾艾菈,5,10,15,-,-,否
勞爾,5,15,-,10,-,否
潔米,-,-,-,-,-,否
瑟法斯,5,15,-,10,-,否
維若妮卡,-,10,10,10,-,否
里卡多,-,-,-,-,-,否
"""

CONFIG_FILE = Path("unlight_config.json") # 使用Path物件

class AdvancedSettingsDialog(Toplevel):
    """進階設定彈出視窗，用於選擇可製作的角色。"""
    def __init__(self, parent: tk.Tk, initial_selected_cards: List[str]):
        super().__init__(parent)
        self.parent = parent
        self.title("進階設定：選擇可製作角色")
        self.transient(parent)
        self.grab_set()

        self.checkbox_vars: Dict[str, tk.BooleanVar] = {}
        # 直接使用傳入的列表，不需複製，因為我們只在關閉時才更新父視窗的狀態
        self.initial_selected_cards = initial_selected_cards
        
        self.create_widgets()
        self.center_window()

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def create_widgets(self) -> None:
        """建立視窗中的所有UI元件。"""
        ttk.Label(self, text="請勾選你擁有或可製作的R卡角色：", font=('Arial', 10, 'bold')).pack(pady=10)

        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=5, fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        checkbox_frame = ttk.Frame(canvas)

        checkbox_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 填充核取方塊
        # 從父元件(主視窗)安全地獲取R卡數據
        r_card_recipes_full = getattr(self.parent, 'r_card_recipes_full', pd.DataFrame())
        if r_card_recipes_full.empty:
            ttk.Label(checkbox_frame, text="R卡數據未載入").pack()
            return

        NUM_COLUMNS = 4
        for col in range(NUM_COLUMNS):
            checkbox_frame.grid_columnconfigure(col, weight=1)

        r_card_names = r_card_recipes_full.index.tolist()
        for i, r_card_name in enumerate(r_card_names):
            row, col = divmod(i, NUM_COLUMNS)
            
            # 檢查是否為無資料R卡
            recipe_data = r_card_recipes_full.loc[r_card_name, FRAGMENT_NAMES]
            numeric_recipe_data = pd.to_numeric(recipe_data, errors='coerce').fillna(0)
            display_name = f"{r_card_name} (無資料)" if numeric_recipe_data.sum() == 0 else r_card_name

            var = tk.BooleanVar(value=(r_card_name in self.initial_selected_cards))
            cb = ttk.Checkbutton(checkbox_frame, text=display_name, variable=var)
            cb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            self.checkbox_vars[r_card_name] = var

        # 按鈕框架
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="儲存設定", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=self.destroy).pack(side="right", padx=5)

    def center_window(self) -> None:
        """將視窗置於父視窗中央。"""
        self.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        w = 800 # 增加寬度以容納4列
        h = 600
        
        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')
        self.minsize(w, h)

    def save_settings(self) -> None:
        """收集勾選的角色並更新父視窗。"""
        selected_cards = [name for name, var in self.checkbox_vars.items() if var.get()]
        # 呼叫父視窗的更新方法
        if hasattr(self.parent, 'update_filtered_r_cards'):
            self.parent.update_filtered_r_cards(selected_cards, show_message=True)
        self.destroy()

class ULFragmentAnalyzer(tk.Tk):
    """UNLIGHT:Revive R卡碎片分析器主應用程式。"""
    def __init__(self) -> None:
        super().__init__()
        self.title("UNLIGHT:Revive R卡碎片分析器 (Gemini Pro 優化版)")
        self.geometry("750x750")
        self.minsize(700, 700)

        # --- 狀態與資料 (封裝) ---
        self.r_card_recipes_full: pd.DataFrame = pd.DataFrame()
        self.r_card_recipes_filtered: pd.DataFrame = pd.DataFrame()
        self.selected_craftable_r_cards: List[str] = []
        
        # --- UI 元件 ---
        self.fragment_entries: Dict[str, ttk.Entry] = {}
        self.fragment_weights: Dict[str, tk.StringVar] = {}
        self.result_text: tk.Text

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.create_widgets()
        self._load_data_and_config()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def create_widgets(self) -> None:
        """建立主視窗的所有UI元件。"""
        # --- 碎片輸入框架 ---
        input_frame = ttk.LabelFrame(self, text="碎片存量與權重", padding="10")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="碎片名稱", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(input_frame, text="目前存量", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(input_frame, text="重要性 (值越高越珍貴)", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=2)

        for i, name in enumerate(FRAGMENT_NAMES, start=1):
            ttk.Label(input_frame, text=f"{name}:").grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(input_frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.fragment_entries[name] = entry

            weight_var = tk.StringVar(self, value="重要")
            weight_dropdown = ttk.Combobox(input_frame, textvariable=weight_var, values=list(WEIGHT_MAP.keys()), state="readonly", width=12)
            weight_dropdown.grid(row=i, column=2, padx=5, pady=2)
            self.fragment_weights[name] = weight_var

        for col in range(3):
            input_frame.grid_columnconfigure(col, weight=1)

        # --- 按鈕框架 ---
        button_container = ttk.Frame(self)
        button_container.pack(pady=10)
        ttk.Button(button_container, text="分析最佳製作方案 (3張R卡)", command=self.run_analysis).pack(side="left", padx=5)
        ttk.Button(button_container, text="進階設定：可製作角色", command=self.open_advanced_settings).pack(side="right", padx=5)

        # --- 結果顯示區 ---
        result_frame = ttk.LabelFrame(self, text="分析結果", padding="10")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.result_text = tk.Text(result_frame, wrap="word", height=15, width=80, font=('Consolas', 10)) # 使用等寬字體
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=scrollbar.set)
        self.result_text.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
    def _load_data_and_config(self) -> None:
        """統一個函式處理資料和設定的載入流程"""
        # 1. 載入內建的R卡CSV數據
        self._load_r_card_data_from_string(R_CARD_CSV_DATA)
        
        # 2. 載入使用者設定檔(如果存在)，這會覆蓋CSV中的預設值
        self._load_config()

        messagebox.showinfo("程式啟動", "R卡製作數據與上次設定已載入。")

    def _load_r_card_data_from_string(self, csv_content: str) -> None:
        """從字串載入R卡製作配方到 self.r_card_recipes_full。"""
        try:
            df = pd.read_csv(StringIO(csv_content))
            df = df.replace('-', 0).fillna(0)
            
            for frag_name in FRAGMENT_NAMES:
                df[frag_name] = pd.to_numeric(df[frag_name], errors='coerce').fillna(0).astype(int)

            if '名字' not in df.columns:
                raise ValueError("CSV中缺少R卡名稱欄位 '名字'。")
            
            self.r_card_recipes_full = df.set_index('名字')
            
            # 預設選擇"已上線"的角色，如果設定檔沒有紀錄的話
            if '已上線' in self.r_card_recipes_full.columns:
                default_online_cards = self.r_card_recipes_full[self.r_card_recipes_full['已上線'] == '是'].index.tolist()
                self.update_filtered_r_cards(default_online_cards, show_message=False)
            else:
                self.update_filtered_r_cards(self.r_card_recipes_full.index.tolist(), show_message=False)
                
        except Exception as e:
            messagebox.showerror("數據載入錯誤", f"載入內建CSV時發生嚴重錯誤：\n{e}\n程式可能無法正常運作。")
            self.r_card_recipes_full = pd.DataFrame() # 發生錯誤時清空

    def _load_config(self) -> None:
        """從JSON設定檔載入使用者設定。"""
        if not CONFIG_FILE.exists():
            print("未找到設定檔，將使用預設設定。")
            return
            
        try:
            with CONFIG_FILE.open('r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 載入碎片數量
            counts = config_data.get('fragment_counts', {})
            for name, entry in self.fragment_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(counts.get(name, 0)))

            # 載入碎片權重
            weights = config_data.get('fragment_weights', {})
            for name, var in self.fragment_weights.items():
                if weights.get(name) in WEIGHT_MAP:
                    var.set(weights.get(name))

            # 載入已選擇的角色
            loaded_cards = config_data.get('selected_r_cards', [])
            if loaded_cards:
                valid_cards = [card for card in loaded_cards if card in self.r_card_recipes_full.index]
                self.update_filtered_r_cards(valid_cards, show_message=False)

        except (json.JSONDecodeError, TypeError) as e:
            messagebox.showwarning("設定檔錯誤", f"設定檔 '{CONFIG_FILE}' 損毀或格式不正確，將使用預設值。\n錯誤: {e}")
        except Exception as e:
            messagebox.showerror("載入錯誤", f"載入設定檔時發生未知錯誤：\n{e}")

    def _save_config(self) -> None:
        """將當前設定儲存到JSON檔案。"""
        config_data = {
            'fragment_counts': {name: entry.get() for name, entry in self.fragment_entries.items()},
            'fragment_weights': {name: var.get() for name, var in self.fragment_weights.items()},
            'selected_r_cards': self.selected_craftable_r_cards
        }
        try:
            with CONFIG_FILE.open('w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("儲存錯誤", f"無法儲存設定檔：\n{e}")

    def _on_closing(self) -> None:
        """應用程式關閉時，儲存設定並銷毀視窗。"""
        self._save_config()
        self.destroy()

    def open_advanced_settings(self) -> None:
        """開啟進階設定視窗。"""
        dialog = AdvancedSettingsDialog(self, self.selected_craftable_r_cards)
        self.wait_window(dialog)

    def update_filtered_r_cards(self, new_selected_cards: List[str], show_message: bool = True) -> None:
        """根據選擇更新可用的R卡列表。"""
        self.selected_craftable_r_cards = new_selected_cards
        
        if not self.r_card_recipes_full.empty and self.selected_craftable_r_cards:
            self.r_card_recipes_filtered = self.r_card_recipes_full.loc[self.selected_craftable_r_cards]
        else:
            self.r_card_recipes_filtered = pd.DataFrame()

        if show_message:
            messagebox.showinfo("設定更新", f"已更新可製作角色列表，共 {len(self.selected_craftable_r_cards)} 個角色。設定已自動儲存。")
        
        # 每次更新都儲存一次設定
        self._save_config()

    def _get_user_inputs(self) -> Optional[Tuple[Dict[str, int], Dict[str, int]]]:
        """從UI獲取並驗證使用者輸入的碎片數量和權重。"""
        try:
            current_fragments = {name: int(self.fragment_entries[name].get()) for name in FRAGMENT_NAMES}
            if any(v < 0 for v in current_fragments.values()):
                raise ValueError("碎片存量不能為負數。")
            
            fragment_weights_val = {name: WEIGHT_MAP[self.fragment_weights[name].get()] for name in FRAGMENT_NAMES}
            return current_fragments, fragment_weights_val
        except (ValueError, KeyError) as e:
            messagebox.showerror("輸入錯誤", f"請檢查所有輸入是否正確。\n錯誤: {e}")
            return None

    def _find_best_combination(self, available_cards: List[str], current_fragments: Dict[str, int], weights: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """核心演算法：尋找成本最低的R卡組合。"""
        best_combo = None
        min_weighted_cost = float('inf')
        
        for combo in itertools.combinations(available_cards, 3):
            total_needed = {name: 0 for name in FRAGMENT_NAMES}
            for card_name in combo:
                for frag_name in FRAGMENT_NAMES:
                    total_needed[frag_name] += self.r_card_recipes_filtered.loc[card_name, frag_name]

            if all(current_fragments[name] >= total_needed[name] for name in FRAGMENT_NAMES):
                # 組合可行，計算成本
                cost = sum(total_needed[name] * weights[name] for name in FRAGMENT_NAMES)
                if cost < min_weighted_cost:
                    min_weighted_cost = cost
                    best_combo = {
                        "combination": combo,
                        "cost": cost,
                        "total_needed": total_needed,
                        "fragments_left": {name: current_fragments[name] - total_needed[name] for name in FRAGMENT_NAMES}
                    }
        return best_combo

    def _format_results(self, best_result: Dict[str, Any]) -> str:
        """將分析結果格式化為易於閱讀的字串。"""
        output = []
        output.append(f"--- 最佳R卡製作方案 ---\n")
        output.append(f"總加權消耗 (越低越好): {best_result['cost']}\n")
        output.append("建議製作以下三張R卡：")
        
        for r_card_name in best_result['combination']:
            output.append(f"\n- 角色：{r_card_name}")
            output.append("  所需碎片：")
            recipe = self.r_card_recipes_filtered.loc[r_card_name]
            for frag_name in FRAGMENT_NAMES:
                if (consumed := recipe.get(frag_name, 0)) > 0:
                    output.append(f"    {frag_name:<6}: {consumed:>3}")

        output.append("\n--- 製作總消耗與剩餘量 ---")
        header = f"{'碎片名稱':<8} {'目前':>5} {'消耗':>5} {'剩餘':>5}"
        output.append(header)
        output.append("-" * len(header))
        
        for name in FRAGMENT_NAMES:
            current = self.fragment_entries[name].get()
            consumed = best_result['total_needed'][name]
            left = best_result['fragments_left'][name]
            output.append(f"{name:<7} {current:>5} {consumed:>5} {left:>5}")
            
        return "\n".join(output)

    def run_analysis(self) -> None:
        """執行完整分析流程的控制器。"""
        self.result_text.delete('1.0', tk.END)

        if self.r_card_recipes_filtered.empty:
            self.result_text.insert(tk.END, "目前沒有可製作的R卡角色被選取。\n請進入'進階設定'勾選希望考量的角色。")
            return

        if len(self.r_card_recipes_filtered) < 3:
            self.result_text.insert(tk.END, f"考量範圍內的角色不足3個 ({len(self.r_card_recipes_filtered)}個)，無法分析。\n請進入'進階設定'勾選更多角色。")
            return

        inputs = self._get_user_inputs()
        if inputs is None:
            return # 輸入有誤，已彈出提示

        current_fragments, fragment_weights = inputs
        available_cards = self.r_card_recipes_filtered.index.tolist()
        
        best_result = self._find_best_combination(available_cards, current_fragments, fragment_weights)

        if best_result:
            result_string = self._format_results(best_result)
            self.result_text.insert(tk.END, result_string)
        else:
            self.result_text.insert(tk.END, "抱歉，根據您目前的碎片存量，找不到可以一次製作三張R卡的組合。\n\n"
                                          "可能原因：\n"
                                          "- 碎片存量不足。\n"
                                          "- 可選角色太少，請至'進階設定'檢查。\n")
        
        # 每次分析完自動儲存輸入的碎片數量
        self._save_config()

def main() -> None:
    app = ULFragmentAnalyzer()
    app.mainloop()

if __name__ == "__main__":
    main()
