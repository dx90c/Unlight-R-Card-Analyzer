// --- 常數與資料設定 ---
const FRAGMENT_NAMES = ["記憶的碎片", "時間的碎片", "靈魂的碎片", "生命的碎片", "死亡的碎片"];
const WEIGHT_MAP = { "隨便用": 1, "不重要": 2, "重要": 3, "很重要": 4, "不能用": 5 };
const CONFIG_KEY = 'unlight_fragment_analyzer_config';

const R_CARD_CSV_DATA = `
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
`;

// --- 應用程式狀態 ---
let rCardRecipesFull = [];
let selectedCraftableRCards = [];

// --- DOM 元素 ---
const inputGrid = document.getElementById('input-grid');
const resultText = document.getElementById('result-text');
const analyzeButton = document.getElementById('analyze-button');
const settingsButton = document.getElementById('settings-button');
const settingsModal = document.getElementById('settings-modal');
const closeModalButton = document.getElementById('close-modal-button');
const saveSettingsButton = document.getElementById('save-settings-button');
const cardSelectionGrid = document.getElementById('card-selection-grid');

// --- 函式 ---

/**
 * 解析CSV字串為物件陣列
 * @param {string} csvText 
 * @returns {Array<Object>}
 */
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',');
    return lines.slice(1).map(line => {
        const values = line.split(',');
        const obj = {};
        headers.forEach((header, i) => {
            const value = values[i];
            // 將 '-' 和空值轉換為0
            obj[header] = (value === '-' || !value) ? 0 : isNaN(Number(value)) ? value : Number(value);
        });
        return obj;
    });
}

/**
 * 載入設定，若無則使用預設值
 */
function loadConfig() {
    const savedConfig = localStorage.getItem(CONFIG_KEY);
    if (savedConfig) {
        const config = JSON.parse(savedConfig);
        // 設定碎片數量
        FRAGMENT_NAMES.forEach(name => {
            document.getElementById(`count-${name}`).value = config.fragmentCounts?.[name] || 0;
            document.getElementById(`weight-${name}`).value = config.fragmentWeights?.[name] || '重要';
        });
        // 設定可選角色
        selectedCraftableRCards = config.selectedRCards || rCardRecipesFull.filter(c => c['已上線'] === '是').map(c => c['名字']);
    } else {
        // 首次使用，預設選擇已上線角色
        selectedCraftableRCards = rCardRecipesFull.filter(c => c['已上線'] === '是').map(c => c['名字']);
    }
}

/**
 * 儲存目前設定到瀏覽器的 localStorage
 */
function saveConfig() {
    const config = {
        fragmentCounts: {},
        fragmentWeights: {},
        selectedRCards: selectedCraftableRCards,
    };
    FRAGMENT_NAMES.forEach(name => {
        config.fragmentCounts[name] = document.getElementById(`count-${name}`).value;
        config.fragmentWeights[name] = document.getElementById(`weight-${name}`).value;
    });
    localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
}

/**
 * 產生陣列中 k 個元素的所有組合 (JavaScript 版本的 itertools.combinations)
 * @param {Array} arr 
 * @param {number} k 
 * @returns {Array<Array>}
 */
function getCombinations(arr, k) {
    const result = [];
    function combine(startIndex, currentCombo) {
        if (currentCombo.length === k) {
            result.push([...currentCombo]);
            return;
        }
        for (let i = startIndex; i < arr.length; i++) {
            currentCombo.push(arr[i]);
            combine(i + 1, currentCombo);
            currentCombo.pop();
        }
    }
    combine(0, []);
    return result;
}


/**
 * 執行分析
 */
function runAnalysis() {
    // 1. 取得使用者輸入
    const currentFragments = {};
    const fragmentWeights = {};
    try {
        FRAGMENT_NAMES.forEach(name => {
            const count = parseInt(document.getElementById(`count-${name}`).value, 10);
            if (isNaN(count) || count < 0) throw new Error(`"${name}" 的存量必須是正整數。`);
            currentFragments[name] = count;
            fragmentWeights[name] = WEIGHT_MAP[document.getElementById(`weight-${name}`).value];
        });
    } catch (e) {
        resultText.textContent = `輸入錯誤：\n${e.message}`;
        return;
    }

    // 2. 篩選可用的R卡
    const availableCards = rCardRecipesFull.filter(card => selectedCraftableRCards.includes(card['名字']));
    if (availableCards.length < 3) {
        resultText.textContent = `考量範圍內的角色不足3個 (${availableCards.length}個)，無法分析。\n請進入'進階設定'勾選更多角色。`;
        return;
    }

    // 3. 核心分析邏輯
    let bestCombination = null;
    let minWeightedCost = Infinity;

    const cardCombinations = getCombinations(availableCards, 3);

    for (const combo of cardCombinations) {
        const totalNeeded = {};
        FRAGMENT_NAMES.forEach(name => totalNeeded[name] = 0);

        combo.forEach(card => {
            FRAGMENT_NAMES.forEach(name => {
                totalNeeded[name] += card[name];
            });
        });

        // 檢查碎片是否足夠
        const isPossible = FRAGMENT_NAMES.every(name => currentFragments[name] >= totalNeeded[name]);

        if (isPossible) {
            // 計算加權成本
            let currentCost = 0;
            FRAGMENT_NAMES.forEach(name => {
                currentCost += totalNeeded[name] * fragmentWeights[name];
            });

            if (currentCost < minWeightedCost) {
                minWeightedCost = currentCost;
                bestCombination = {
                    combo: combo,
                    cost: currentCost,
                    totalNeeded: totalNeeded
                };
            }
        }
    }

    // 4. 顯示結果
    if (bestCombination) {
        let output = `--- 最佳R卡製作方案 ---\n`;
        output += `總加權消耗 (越低越好): ${bestCombination.cost}\n`;
        output += "建議製作以下三張R卡：\n";

        bestCombination.combo.forEach(card => {
            output += `\n- 角色：${card['名字']}\n`;
            output += "  所需碎片：\n";
            FRAGMENT_NAMES.forEach(name => {
                if (card[name] > 0) {
                    output += `    ${name}: ${card[name]}\n`;
                }
            });
        });

        output += "\n--- 製作總消耗與剩餘量 ---\n";
        output += `碎片名稱      目前存量   消耗   剩餘\n`;
        output += `---------------------------------------\n`;
        FRAGMENT_NAMES.forEach(name => {
            const current = currentFragments[name];
            const consumed = bestCombination.totalNeeded[name];
            const left = current - consumed;
            output += `${name.padEnd(7, '　')} ${String(current).padStart(7)} ${String(consumed).padStart(7)} ${String(left).padStart(7)}\n`;
        });
        
        resultText.textContent = output;
    } else {
        resultText.textContent = "抱歉，根據您目前的碎片存量，找不到可以一次製作三張R卡的組合。\n\n" +
                               "可能原因：\n" +
                               "- 碎片存量不足。\n" +
                               "- 可選角色太少，請至'進階設定'檢查。\n";
    }
    
    // 分析完自動儲存
    saveConfig();
}


/**
 * 初始化應用程式
 */
function initialize() {
    // 1. 動態生成輸入欄位
    inputGrid.innerHTML = `
        <div class="grid-header">碎片名稱</div>
        <div class="grid-header">目前存量</div>
        <div class="grid-header">重要性</div>
    `;
    FRAGMENT_NAMES.forEach(name => {
        inputGrid.innerHTML += `
            <label for="count-${name}">${name}</label>
            <input type="number" id="count-${name}" min="0" value="0">
            <select id="weight-${name}">
                ${Object.keys(WEIGHT_MAP).map(key => `<option value="${key}" ${key === '重要' ? 'selected' : ''}>${key}</option>`).join('')}
            </select>
        `;
    });
    
    // 2. 解析並載入資料
    rCardRecipesFull = parseCSV(R_CARD_CSV_DATA);
    loadConfig(); // 會載入使用者設定或預設值

    // 3. 綁定事件監聽
    analyzeButton.addEventListener('click', runAnalysis);

    // -- Modal 相關事件 --
    settingsButton.addEventListener('click', () => {
        // 每次打開時重新生成，以反映最新選擇
        cardSelectionGrid.innerHTML = '';
        rCardRecipesFull.forEach(card => {
            const isChecked = selectedCraftableRCards.includes(card['名字']);
            const totalFragments = FRAGMENT_NAMES.reduce((sum, name) => sum + card[name], 0);
            const displayName = totalFragments === 0 ? `${card['名字']} (無資料)` : card['名字'];

            cardSelectionGrid.innerHTML += `
                <div class="checkbox-item">
                    <input type="checkbox" id="card-${card['名字']}" value="${card['名字']}" ${isChecked ? 'checked' : ''}>
                    <label for="card-${card['名字']}">${displayName}</label>
                </div>
            `;
        });
        settingsModal.style.display = 'flex';
    });

    closeModalButton.addEventListener('click', () => {
        settingsModal.style.display = 'none';
    });
    
    saveSettingsButton.addEventListener('click', () => {
        const selected = [];
        const checkboxes = cardSelectionGrid.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            if (cb.checked) {
                selected.push(cb.value);
            }
        });
        selectedCraftableRCards = selected;
        saveConfig();
        alert(`設定已儲存！共選擇了 ${selected.length} 個角色。`);
        settingsModal.style.display = 'none';
    });
    
    window.addEventListener('click', (event) => {
        if (event.target === settingsModal) {
             settingsModal.style.display = 'none';
        }
    });
}

// 當DOM載入完成後，執行初始化
document.addEventListener('DOMContentLoaded', initialize);