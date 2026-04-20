import pandas as pd

# 1. 準備你要處理的檔案清單 (請確認檔名與你實際的檔案一致)
# 這裡假設你已經跑過之前的清洗程式，把大家統一成頓號格式了
files_to_process = [
    "乾淨版_115錄取分數.csv",
    "乾淨版_114錄取分數.csv",
    "乾淨版_113錄取分數.csv",
    "乾淨版_112錄取分數.csv"
]

# 2. 定義你的完美排序字典
priority = {
    "國": 1, "英": 2, "數A": 3, "數B": 4,
    "自": 5, "社": 6, "數甲": 7, "數乙": 8,
    "物": 9, "化": 10, "生": 11, "地": 12,
    "歷": 13, "公": 14
}


def sort_subjects_standard(subject_str):
    """將採計科目字串依照指定順序重新排列"""
    # 處理空值或沒有科目的情況
    if pd.isna(subject_str) or str(subject_str).strip() in ["—", "??", ""]:
        return subject_str

    # 用頓號切開 (例如: ['物x1.00', '數甲x1.00'])
    items = str(subject_str).split('、')

    # 定義排序規則
    def get_rank(item):
        subject_name = item.split('x')[0]  # 抓出 "數甲" 等科目名稱
        # 如果科目在字典裡就回傳排名，如果是不認識的奇葩科目就給 99 丟到最後面
        return priority.get(subject_name, 99)

    # 進行排序
    items.sort(key=get_rank)

    # 用頓號黏回去
    return "、".join(items)


# 3. 跑迴圈，把每個檔案都抓出來洗一遍
for file_name in files_to_process:
    try:
        # 讀取 CSV
        df = pd.read_csv(file_name, encoding='utf-8-sig')

        # 自動找出包含「採計科目」四個字的欄位 (防呆機制，不管欄位全名是什麼都能抓到)
        col_candidates = [col for col in df.columns if "採計" in col]

        if not col_candidates:
            print(f"⚠️ 在 {file_name} 中找不到包含『採計』的欄位，跳過此檔。")
            continue

        col_name = col_candidates[0]

        # 套用排序魔法
        df[col_name] = df[col_name].apply(sort_subjects_standard)

        # 直接覆蓋原本的檔案存檔
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"✅ {file_name} 排序完成並儲存成功！")

    except FileNotFoundError:
        print(f"⚠️ 找不到檔案：{file_name}，請確認檔案是否跟這支程式放在同一個資料夾。")
    except Exception as e:
        print(f"❌ 處理 {file_name} 時發生錯誤：{e}")

print("🎉 所有檔案的採計科目都已經乖乖排隊啦！")