import pandas as pd
import re

# 要處理的舊檔案列表
past_years_files = [
    "乾淨版_114錄取分數.csv",
    "乾淨版_113錄取分數.csv",
    "乾淨版_112錄取分數.csv"
]


def clean_past_years_subjects(text):
    if pd.isna(text) or str(text).strip() == "":
        return "—"

    text = str(text).strip()

    # 使用 Regex 把中間的「一個或多個空白」替換成「、」
    # 這樣 "數甲x1.00 物x1.00" 就會變成 "數甲x1.00、物x1.00"
    text = re.sub(r'\s+', '、', text)

    return text


# 迴圈處理每年的檔案
for file_name in past_years_files:
    try:
        df = pd.read_csv(file_name, encoding='utf-8-sig')

        # 假設你的欄位名稱也叫做這個 (如果不同請自行修改)
        # 前三年的檔案裡，欄位名稱可能叫做 "採計科目" 或 "採計科目及加權..."
        # 這裡用一個防呆機制，找出包含 "採計" 的欄位
        col_name = [col for col in df.columns if "採計" in col][0]

        df[col_name] = df[col_name].apply(clean_past_years_subjects)

        # 直接覆蓋原本的檔案 (或者你可以存成新的名字)
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"✅ {file_name} 資料清洗完成！")

    except FileNotFoundError:
        print(f"⚠️ 找不到檔案：{file_name}，請確認檔名是否正確。")
    except IndexError:
        print(f"⚠️ 在 {file_name} 中找不到包含『採計』的欄位。")