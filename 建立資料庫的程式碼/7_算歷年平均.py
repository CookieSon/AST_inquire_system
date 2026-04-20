import pandas as pd
import re
import numpy as np



files_to_process = [
    "乾淨版_114錄取分數2.csv",
    "乾淨版_113錄取分數2.csv",
    "乾淨版_112錄取分數2.csv"
]

def get_ave(subject_str,score):
    try:
        score = float(score)
    except (ValueError, TypeError):
        return score


    #1.算加權
    weight_str = re.sub(r"[^\d\.、]", "", str(subject_str)) #處理採計科目這列，只留下數字、小數點、頓號
    weight_np = np.array(weight_str.split('、'), dtype=float) #將上一行的字串換成nparray並將元素換成float
    weight = weight_np.sum() #加權總合

    #2.算平均
    ave = f"{score / weight:.2f}"

    return ave

for file in files_to_process:
    try:
        df = pd.read_csv(file)

        df['平均'] = df.apply(
        lambda row: get_ave(row['採計科目及加權(含學測、分科及術科)'], row['錄取分數']),
        axis = 1
        )

        df.to_csv(file, index=False, encoding='utf-8-sig')

    except FileNotFoundError:
        print(f"⚠️ 找不到檔案：{file}，請確認檔案是否跟這支程式放在同一個資料夾。")
    except Exception as e:
        print(f"❌ 處理 {file} 時發生錯誤：{e}")

print("HAHA,OK")




