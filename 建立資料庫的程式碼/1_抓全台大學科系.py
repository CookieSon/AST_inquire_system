import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from io import StringIO
import time
import re

# 隱藏 SSL 警告並設定顯示完整欄位
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

session = requests.Session()

submit_url = "https://uac2.ncku.edu.tw/cross_search/index.php?c=search&m=result_school"
index_url = "https://uac2.ncku.edu.tw/cross_search/index.php?c=search&m=index"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": index_url
}

# 先去首頁領 Cookie
session.get(index_url, headers=headers, verify=False)

# 你提供的全台大學字串
school_text = "(001)國立臺灣大學(002)國立臺灣師範大學(003)國立中興大學(004)國立成功大學(005)東吳大學(006)國立政治大學(007)高雄醫學大學(008)中原大學(009)東海大學(011)國立清華大學(012)中國醫藥大學(013)國立陽明交通大學(014)淡江大學(015)逢甲大學(016)國立中央大學(017)中國文化大學(018)靜宜大學(019)大同大學(020)輔仁大學(021)國立臺灣海洋大學(022)國立高雄師範大學(023)國立彰化師範大學(026)中山醫學大學(027)國立中山大學(028)國立臺北藝術大學(030)長庚大學(031)國立臺中教育大學(032)國立臺北教育大學(033)國立臺南大學(034)國立東華大學(035)臺北市立大學(036)國立屏東大學(038)國立臺東大學(039)國立體育大學(040)元智大學(041)國立中正大學(042)大葉大學(044)華梵大學(045)義守大學(046)銘傳大學(047)世新大學(050)實踐大學(051)長榮大學(056)國立臺灣藝術大學(058)國立暨南國際大學(059)南華大學(060)國立臺灣體育運動大學(063)國立臺南藝術大學(065)玄奘大學(079)真理大學(099)國立臺北大學(100)國立嘉義大學(101)國立高雄大學(108)慈濟大學(109)臺北醫學大學(110)開南大學(112)康寧大學(113)中信金融管理學院(130)佛光大學(134)亞洲大學(150)國立宜蘭大學(151)國立聯合大學(152)馬偕醫學大學(153)國立金門大學"

# 用正規表達式自動拆解成 List，格式如：[('001', '國立臺灣大學'), ('002', '國立臺灣師範大學')...]
schools = re.findall(r'\((\d{3})\)([^()]+)', school_text)

all_departments_data = []

print(f"🚀 準備開始抓取 {len(schools)} 所大學的資料...")

# 外層迴圈：切換學校
for school_code, school_name in schools:
    print(f"\n=========================================")
    print(f"🏫 正在切換至：{school_name} (代碼: {school_code})")
    print(f"=========================================")

    # 內層迴圈：切換該校的科系 (1 到 99)
    for i in range(1, 100):
        dept_code = f"{school_code}{i:02d}"

        payload = {
            "D1": "0",
            "D2": "0",
            "school_name": school_code,
            "department_cnam": dept_code,
            "my_search": "校系查詢"
        }

        try:
            # 送出查詢
            response = session.post(submit_url, headers=headers, data=payload, verify=False, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            # 判斷這個代碼是不是真的有科系
            if len(tables) > 0:
                html_string = str(tables[0])
                df = pd.read_html(StringIO(html_string))[0]

                # 欄位名稱清理
                df.columns = df.columns.str.replace(' ', '').str.replace('\n', '').str.replace('\r', '')

                col_name = '學系名稱'
                col_criteria = '學科能力測驗及英語聽力測驗檢定標準'
                col_subject = '採計科目及加權(含學測、分科及術科)'

                if set([col_name, col_criteria, col_subject]).issubset(df.columns):
                    dept_name = df.iloc[0][col_name]
                    df_clean = df[[col_name, col_criteria, col_subject]].copy()
                    df_clean = df_clean[df_clean[col_subject] != '--']

                    if not df_clean.empty:
                        # 濃縮資料
                        df_final = df_clean.groupby([col_name, col_criteria])[col_subject].apply('、'.join).reset_index()

                        # 💡 魔法發生在這裡：把「校名」強制插在第 0 欄 (最前面)
                        df_final.insert(0, '校名', school_name)

                        all_departments_data.append(df_final)
                        print(f"✅ 抓取成功：{school_name} - {dept_name}")

        except Exception as e:
            # 加上 try-except 是為了防止網路突然斷線或伺服器卡住導致整個程式崩潰
            print(f"❌ 發生錯誤 (代碼 {dept_code})：{e}")

        # 🕵️ 爬蟲禮儀：稍微縮短一點時間到 0.2 秒，加速整體進度
        time.sleep(0.2)

print("\n🎉 全台大學資料抓取完畢！正在進行最後合併...")

if len(all_departments_data) > 0:
    final_big_table = pd.concat(all_departments_data, ignore_index=True)

    csv_filename = "115學年度_全台大學分科檢定與採計標準.csv"

    # 存成你要的 4 個欄位格式，並使用 utf-8-sig 防止 Excel 亂碼
    final_big_table.to_csv(csv_filename, index=False, encoding='utf-8-sig')

    print(f"💾 存檔大成功！共收集了 {len(final_big_table)} 筆科系資料！")
    print(f"請在資料夾尋找：{csv_filename}")
else:
    print("😭 好像什麼都沒抓到，請確認網路連線是否正常。")