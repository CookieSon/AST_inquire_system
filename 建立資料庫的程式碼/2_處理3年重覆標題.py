import pandas as pd

# 1. 讀取你從 PDF 轉過來的 Excel 檔案
# 請把這裡換成你實際的檔案名稱
input_file = "114錄取分數.xlsx"
df = pd.read_excel(input_file)

print(f"🧹 整理前，共有 {len(df)} 列資料")

# 2. 清除重複的標題列 (只要「校名」那格的值等於「校名」，就不要它)
df_clean = df[df['校名'] != '校名']

# 3. (加碼防護) 清除整列都是空白(NaN)的幽靈列
df_clean = df_clean.dropna(how='all')

# 4. 把索引值(Index)重新排好，避免因為刪除列而跳號
df_clean = df_clean.reset_index(drop=True)

print(f"✨ 整理後，剩下 {len(df_clean)} 列乾淨的資料！")

# 5. 存成一份新的、乾淨的 Excel 檔案
# 把原本檔名的 .xlsx 替換成 .csv
output_file = "乾淨版_" + input_file.replace(".xlsx", ".csv")

# 存成 CSV 檔案，記得加上 utf-8-sig 避免 Excel 打開變亂碼
df_clean.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"💾 已經幫你把乾淨的資料存成 CSV 檔：{output_file}")