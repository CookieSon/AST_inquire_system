import pandas as pd
import re

# 1. 讀取 115 年的 CSV 檔案 (請換成你實際的檔名)
file_115 = "115學年度_全台大學分科檢定與採計標準.csv"
df_115 = pd.read_csv(file_115, encoding='utf-8-sig')


def clean_115_subjects(text):
    if pd.isna(text) or str(text).strip() == "":
        return "—"

    text = str(text)
    # 步驟 1: 移除所有半形空白和全形空白(　)
    text = text.replace(" ", "").replace("　", "")

    # 步驟 2: 移除 (分科)、(學測)、(術科) 等括號及裡面的字
    text = re.sub(r'\(.*?\)', '', text)

    # 步驟 3: 科目名稱對照翻譯字典 (包含社會科與生物)
    replacements = {
        "數學甲": "數甲", "數學乙": "數乙", "數學A": "數A", "數學B": "數B",
        "自然": "自", "物理": "物", "化學": "化", "生物": "生",
        "國文": "國", "英文": "英", "歷史": "歷", "地理": "地",
        "公民與社會": "公", "社會": "社"
    }

    # 執行替換
    for old_name, new_name in replacements.items():
        text = text.replace(old_name, new_name)

    return text


# 套用清洗邏輯到採計科目欄位 (請確認欄位名稱是否正確)
col_name = "採計科目及加權(含學測、分科及術科)"
df_115[col_name] = df_115[col_name].apply(clean_115_subjects)

# 儲存成新的乾淨 CSV 檔案
output_115 = "乾淨版_115錄取分數.csv"
df_115.to_csv(output_115, index=False, encoding='utf-8-sig')
print(f"✅ 115 年資料清洗完成！已存為 {output_115}")