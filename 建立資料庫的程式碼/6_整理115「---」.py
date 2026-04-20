import pandas as pd

# 這裡設定你要修改的 115 年檔案名稱
file_115 = "乾淨版_115錄取分數.csv"  # 如果你的檔名是原始的，請改成 "115學年度_全台大學分科檢定與採計標準.csv"

try:
    # 讀取 CSV 檔案
    df = pd.read_csv(file_115, encoding='utf-8-sig')

    # 自動找出包含「檢定」或「標準」的欄位名稱
    col_candidates = [col for col in df.columns if "檢定" in col or "標準" in col]

    if not col_candidates:
        print(f"⚠️ 在 {file_115} 中找不到檢定標準的欄位，請檢查檔案！")
    else:
        col_name = col_candidates[0]

        # 1. 將所有空值 (NaN) 直接補上 '—'
        df[col_name] = df[col_name].fillna('——')

        # 2. 將文字轉成字串後，把 '—' 替換成 '—'
        df[col_name] = df[col_name].astype(str).replace('—', '——')

        # 直接覆蓋原本的檔案存檔
        df.to_csv(file_115, index=False, encoding='utf-8-sig')
        print(f"✅ {file_115} 的檢定標準符號已經全部統一為『——』並儲存成功！")

except FileNotFoundError:
    print(f"⚠️ 找不到檔案：{file_115}，請確認檔案是否跟這支程式放在同一個資料夾。")
except Exception as e:
    print(f"❌ 發生未知的錯誤：{e}")