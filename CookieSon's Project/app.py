import streamlit as st
import pandas as pd
import numpy as np
import re  # 正則表達式 Regular Expression (Regex)


# ===  讀取資料庫  =======================================================================================================

# [Streamlit] 使用快取，這樣 4 個巨大的 CSV 檔只要讀取一次就會記在腦海裡，搜尋會變超快！
@st.cache_data

def load_data():
    try:
        df_115 = pd.read_csv("115分發入學_new.csv", encoding='utf-8-sig')
        df_114 = pd.read_csv("114分發入學_new.csv", encoding='utf-8-sig')
        df_113 = pd.read_csv("113分發入學_new.csv", encoding='utf-8-sig')
        df_112 = pd.read_csv("112分發入學_new.csv", encoding='utf-8-sig')
        print("✅ 成功讀取資料庫！")
        return {115: df_115, 114: df_114, 113: df_113, 112: df_112}
    except FileNotFoundError:
        print("⚠️❌找不到 資料庫 檔案❌⚠️")
        st.error("⚠️ 找不到 資料庫 檔案，請聯絡我們：cookiesonworking@gmail.com")
        st.stop()  # 找不到檔案就直接停止網頁執行

df_dict = load_data() # 把資料庫打包成字典：df_dict


# ===  處理科系名稱，分離出組別  ============================================================================================
def parse_dept_name(full_name):
    """" full_name : 科系名稱 """
    match = re.search(r'(.+(?:學系|學位學程|學士班))(.*)', str(full_name))
    if match:
        base_name = match.group(1).strip()
        group_name = match.group(2).strip() or "—"
    else:
        base_name = str(full_name)
        group_name = "—"
    return base_name, group_name



# === 計算所需分數  ======================================================================================================
def cal_score(gsat1, subject1, history):
    """
    gsat1 : 使用者的學測分數
    subject1 : 該科系的分科採計科目
    history : 該科系的歷年分數
    """
    try:
        score = float(history)
    except (ValueError, TypeError):
        return ['—', '—']

    # 將使用者學測有考的科目新增至 list
    subject_all = ['國', '英', '數A', '數B', '自', '社']
    subject_list = []
    for i in subject_all:
        if gsat1.get(i,0) > 0:
            subject_list.append(i)

    # 算原始加權
    try:
        weight_str = re.sub(r"[^\d\.、]", "", str(subject1)) # 處理採計科目這列，只留下數字、小數點、頓號
        weight_np = np.array(weight_str.split('、'), dtype=float) # 將上一行的字串換成 nparray，並將元素換成 float
        weight = weight_np.sum() # 加權總合
    except Exception:
        return ['—', '—']

    # 分科會看學測分數而且有考的 dict
    subject_dict = {}
    subject1_items = str(subject1).split('、')
    for i in subject1_items:
        try:
            if i[0] in subject_list:  # 國、英、自、社
                subject_dict[i[0]] = float(i[2:])
            elif i[:2] in subject_list:  # 數A、數B
                subject_dict[i[:2]] = float(i[3:])
        except ValueError:
            continue  # 遇到轉不出來的數字格式就跳過

    # 扣掉學測有考的，算所需分數和平均
    subject_dict_keys = list(subject_dict.keys())
    for i in subject_dict_keys:  # 撈出我學測有考而且分科會看的科目
        gsat_score = float(gsat.get(i,0)) # 撈出我學測分數
        weight_now = float(subject_dict.get(i)) # 該科目加權
        score -= gsat_score * weight_now
        weight -= weight_now
    if weight <= 0:  # 如果分科採計科目只採學測，加權等於0
        return ['0', '0']
    ave = f"{score / weight:.2f}"
    score = f"{score:.2f}"

    return [score,ave]


# === 核心搜尋與整理邏輯  =================================================================================================
def search_department(keyword, school_groups, gsat):
    """
    keyword: 使用者輸入的搜尋字詞
    school_groups: List，使用者勾選的學校群組 (例如 ["台成清交政"])
    gsat: 使用者的學測成績
    """

    # 防爆機制 - 無效關鍵字
    if len(keyword) == 1:
        return "只輸入一個字是有什麼心事嗎嗎"
    if len(keyword) == 2:
        WTF = ["國立", "大學", "工程", "學系"]
        if keyword in WTF:
            return "別搞"

    # 依照「換行」把使用者的輸入切成多個獨立的關鍵字
    queries = [q.strip() for q in keyword.split('\n') if q.strip() != ""]

    if not queries:
        return "⚠️ 請輸入更明確的科系名稱！"

    all_results = []

    # 針對每一行的關鍵字 (校系)，跑迴圈分別去撈資料
    for single_query in queries:
        # 處理常見的大學簡稱
        search_kw = single_query.replace("台大", "國立臺灣大學 ").replace("臺大", "國立臺灣大學 ")
        search_kw = search_kw.replace("成大", "國立成功大學 ").replace("清大", "國立清華大學 ")
        search_kw = search_kw.replace("交大", "國立陽明交通大學 ").replace("政大", "國立政治大學 ")
        search_kw = search_kw.replace("台師大", "國立臺灣師範大學 ").replace("北大", "國立臺北大學 ")
        search_kw = search_kw.replace("台東", "國立臺東大學 ").replace("台南", "臺南")
        search_kw = search_kw.replace("台中", "臺中").replace("台","臺")
        search_kw = search_kw.replace("北醫", "臺北醫學大學 ").replace("高醫", "高雄醫學大學 ")
        search_kw = search_kw.replace("中山醫", "中山醫學大學 ").replace("中國醫", "中國醫藥大學 ")

        # 處理科系的別稱
        search_kw = search_kw.replace("醫科", "醫學系")
        search_kw = search_kw.replace("中醫", "中醫學系")
        search_kw = search_kw.replace("牙醫", "牙醫學系")
        search_kw = search_kw.replace("獸醫", "獸醫學系")
        search_kw = search_kw.replace("資工", "資訊工程")
        search_kw = search_kw.replace("資管", "資訊管理")

        # 依照空白鍵把關鍵字切開
        kws = search_kw.split()

        # 撈該科系 的 每年資料
        for year, df in df_dict.items():
            # 把資料庫中的校名和系名中間加一個「空格」黏在一起
            combined_text = df['校名'].astype(str) + " " + df['學系名稱'].astype(str)

            # 將所有校系設為 True 存進去 mask
            mask = pd.Series(True, index=df.index)

            # 快速篩選學校清單 的判斷
            if school_groups:
                target_schools = []
                if "台成清交政" in school_groups:
                    target_schools += ["國立臺灣大學", "國立成功大學", "國立清華大學", "國立陽明交通大學", "國立政治大學"]
                if "中字輩、台師大、北大" in school_groups:
                    target_schools += ["國立中山大學", "國立中正大學", "國立中興大學", "國立中央大學", "國立臺灣師範大學", "國立臺北大學"]
                # 在清單內的學校設為 True，其餘 False。。  & : 交集，只有兩邊都是 True 才會存進 mask
                mask &= df['校名'].isin(target_schools)

            # Regex 多關鍵字模糊搜尋：
            strict_words = [    #不要被 Regex 模糊搜尋的校系
                "國立臺灣大學", "國立高雄大學", "國立臺南大學",
                "國立體育大學", "國立臺灣師範大學", "國立臺北大學", "醫學系", "中醫學系"]

            for kw in kws:
                if kw in strict_words:
                    regex_pattern = kw
                else:
                    regex_pattern = '.*'.join(list(kw))  #在 kws 每個字元之間黏上'.*' : 塞任意字元、任意字數都可以

                mask &= combined_text.str.contains(regex_pattern, regex=True, na=False)  # .str.contains() : 搜尋字串

            # 排除法 - 系名 (解決醫科大亂鬥)
            if "醫學系" in search_kw:
                # 獸醫、牙醫、中醫
                dept_chars = ['獸', '牙','中']
                for char in dept_chars:
                    if char not in single_query:
                        mask &= ~df['學系名稱'].astype(str).str.contains(char, na=False)  # ~ 表 not
                # 生物醫學系
                if "生" not in single_query and "物" not in single_query:
                    mask &= ~df['學系名稱'].astype(str).str.contains("生物", na=False)
                # 運動醫學系
                if "運" not in single_query and "動" not in single_query:
                    mask &= ~df['學系名稱'].astype(str).str.contains("運動", na=False)
                # 植物醫學系
                if "植" not in single_query and "物" not in single_query:
                    mask &= ~df['學系名稱'].astype(str).str.contains("植物", na=False)

            matched_data = df[mask]  # 把 mask 過濾好，存到 matched_data

            # 建立每個科系的資料
            for _, row in matched_data.iterrows():
                base_name, group_name = parse_dept_name(row['學系名稱'])  #將科系拆成系名和組別

                # 計算使用者所需分數
                if year != 115:
                    if gsat != {'國':0, '英':0, '數A':0, '數B':0, '自':0, '社':0}:
                        cal_ans = cal_score(gsat, row.get('採計科目及加權(含學測、分科及術科)', '??'),
                                             row.get('錄取分數', '—'))
                        req_score = cal_ans[0]
                        req_ave = cal_ans[1]
                        if float(req_ave) >= 60:  # 所需平均大於60分
                            req_ave = f"~~**{req_ave}**~~"
                    else:
                        req_score = '—'
                        req_ave = '—'
                else:
                    req_score = '—'
                    req_ave = '—'

                # 整合資料格式
                result_row = {
                    '年度': year,
                    '校名': row['校名'],
                    '基底學系': base_name,
                    '組別': group_name,
                    '學測標準': row.get('學科能力測驗及英語聽力測驗檢定標準','??') if year == 115 else '<small>*0人在乎*</small>',
                    '採計科目': row.get('採計科目及加權(含學測、分科及術科)', '??'),
                    '歷年分數': row.get('錄取分數', '??') if year != 115 else '<small>*猜*</small>',
                    '平均': row.get('平均', '??') if year != 115 else '—',
                    '所需分數': req_score,
                    '所需平均': req_ave
                }
                all_results.append(result_row)

    if not all_results:
        return "😭 找不到相關科系，請換個關鍵字試試看！"

    results_df = pd.DataFrame(all_results)  # 轉成 dataframe 表格形式

    # 去重複：避免多行輸入重複的系，導致表格重複印出
    results_df = results_df.drop_duplicates(subset=['年度', '校名', '基底學系', '組別'])

    # 群組分類：依照校系分類，把原本 results_df 這個超大表格，拆分成數個以校系為分類的表格
    grouped = results_df.groupby(['校名', '基底學系'], sort=False)

    # 防爆機制：太多筆資料
    if len(grouped) > 300:
        return "⚠️ 搜尋結果過長，請輸入更精確的關鍵字！"

    # 處理要輸出的文字和表格 (markdown)
    output_text = ""
    for (school, dept), group_df in grouped:
        output_text += f"### 🏫 {school} {dept}\n"

        display_df = group_df[['年度', '組別', '學測標準', '採計科目', '歷年分數', '平均', '所需分數', '所需平均']]  # 欄位
        display_df = display_df.sort_values(by=['年度', '組別'], ascending=[False, False])  # 排序

        # 轉成 Markdown 表格
        output_text += display_df.to_markdown(index=False) + "\n---\n"


    return output_text


# ===  Streamlit 網頁介面設計  ===========================================================================================

# 設定網頁標題與寬度版面
st.set_page_config(page_title="分科校系分數查詢系統", page_icon="🎓", layout="wide")

st.title("115 學年度 分科校系分數查詢系統")
st.write("手機使用者建議開啟電腦版網站功能，更方便檢視")

# st.form 將輸入區塊包裝起來，按下開始搜尋才會執行
with st.form(key="search_form"):
    col1, col2, col3 = st.columns([2, 1,1])

    with col1:
        search_input = st.text_area(
            "🔍 搜尋科系",
            placeholder="請輸入校名或科系關鍵字  (可換行搜尋多個科系)，例如:\n成大電機\n台大\n醫學系\n",
            height=136
        )

        # 這是這個 form 的送出鍵
        search_btn = st.form_submit_button("開始搜尋", type="primary", use_container_width=True)

    with col2:
        st.write("快速篩選學校清單：  \n(勾選後，你可以只輸入你想要的科系名稱)")
        check_top = st.checkbox("台成清交政")
        check_mid = st.checkbox("中字輩、台師大、北大")

        school_group_cb = []
        if check_top:
            school_group_cb.append("台成清交政")
        if check_mid:
            school_group_cb.append("中字輩、台師大、北大")

    with col3:
        st.write("你的學測級分 (60級分制) (選填)")
        col4, col5, col6 = st.columns([1,1,1])
        with col4:
            chi = st.number_input('國文',0,60,0,1)
            eng = st.number_input('英文',0,60,0,1)
        with col5:
            matha = st.number_input('數A', 0, 60, 0, 1)
            mathb = st.number_input('數B',0,60,0,1)
        with col6:
            sci = st.number_input('自然',0,60,0,1)
            soc = st.number_input('社會', 0, 60, 0, 1)
gsat = {'國':chi, '英':eng, '數A':matha, '數B':mathb, '自':sci, '社':soc}

st.markdown("📊 搜尋結果")

# 開始搜尋時觸發
if search_btn:
    if search_input.strip() != "":
        # 呼叫搜尋函式
        result_markdown = search_department(search_input, school_group_cb, gsat)

        # 把算出來的 Markdown 結果印在網頁上
        st.markdown(result_markdown, unsafe_allow_html=True)  # unsafe_allow_html : 同意使用 Html
    else:
        st.warning("⚠️ 請先輸入要搜尋的科系！")


st.write("---")
st.write("""
有任何問題，請聯絡我們：  
cookiesonworking@gmail.com  
""")