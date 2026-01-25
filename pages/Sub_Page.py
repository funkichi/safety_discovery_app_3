import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io
import os

# ページ設定（画面の幅を広く使う）
#st.set_page_config(page_title="My Streamlit App", layout="wide")

# スタイル設定（背景色と文字色とフォントを定義）
def apply_custom_style():    
    main_bg_color = "#F5BAB1"       # メイン画面背景色
    sidebar_bg_color = "#B3F5AE"    # サイドバー背景色
    sidebar_text_color = "#000000"  # サイドバー文字色
    font_family = "MAX太丸ｺﾞｼｯｸ体"     # フォント

    st.markdown(
        f"""
        <style>
        /* メイン画面全体の背景色 */
        .stApp {{
            background-color: {main_bg_color};
        }}
        
        /* メイン画面の文字色 */
        .stApp .main h1,
        .stApp .main h2,
        .stApp .main h3,
        .stApp .main label {{
            font-family: "{font_family}" !important;
            color: #000000 !important;
        }}

        /* st.write の文字色 */
        .stApp .main [data-testid="stMarkdownContainer"] p {{
            font-family: "{font_family}" !important;
            color: #000000 !important;
        }}

        /* ボタンの文字色 */
        .stApp .main .stButton button,
        .stApp .main .stButton button p,
        .stApp .main .stButton button span,
        .stApp .main .stButton button div,
        [data-testid="baseButton-secondary"] p,
        [data-testid="baseButton-primary"] p {{
            color: #FFFFFF !important;
            font-family: "{font_family}" !important;
            -webkit-text-fill-color: #FFFFFF !important; /* ブラウザ対策 */
        }}

        /* リンクの文字色 */
        .stApp .main a {{
            color: #0000EE;
            font-family: "{font_family}";
        }}
      
        /* サイドバーの背景色 */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color};
        }}

        /* サイドバー内の文字色とフォント */
        [data-testid="stSidebar"], 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebarNav"] span,
        [data-testid="stSidebarNav"] a {{ 
            font-family: {font_family} !important;
            color: {sidebar_text_color} !important;
        }}     
        </style>
        """,
        unsafe_allow_html=True
    )

# スタイルを適用
apply_custom_style()

# 画像サイズを変数に代入
size_logo = (1200, 360)
size_area1 = (200, 200)
size_area2 = (200, 200)
size_area3 = (200, 200)
size_disaster = (200, 200)

# 画像ファイルを読み込んでthumbnailでサイズを指定
image_logo = Image.open('Material/logo.png')
image_logo.thumbnail(size_logo)
image_area1 = Image.open('Material/area1.png')
image_area1.thumbnail(size_area1)
image_area2 = Image.open('Material/area2.png')
image_area2.thumbnail(size_area2)
image_area3 = Image.open('Material/area3.png')
image_area3.thumbnail(size_area3)
image_disaster = Image.open('Material/disaster.png')
image_disaster.thumbnail(size_disaster)

# 画像をバイト列として読み込んでbase64エンコードする(streamlitでは画像をHTMLタグで参照できないため)
def get_image_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# base64エンコードされた文字列を取得
img_str_logo = get_image_base64(image_logo)

# HTMLで画像を表示する
st.markdown(f'<p style="text-align: center;"><img src="data:image/png;base64,{img_str_logo}"></p>', unsafe_allow_html=True)

# 3列改行
for i in range(3):
    st.write('\n')

# pandasでcsvファイルを読み込む
df = pd.read_csv('DataBase/避難場所.csv')

# 1. エリアのセレクトボックス
st.image(image_area1)
available_areas = list(df['エリア'].drop_duplicates())
selected_location_1 = st.selectbox("", available_areas, label_visibility="collapsed")

# 2. 都道府県のセレクトボックス
# エリアが選択されたら、そのエリアに属する都道府県のみを抽出
st.image(image_area2)
if selected_location_1: # エリアが選択されている場合
    filtered_df_by_area = df[df['エリア'] == selected_location_1]
    available_prefectures = list(filtered_df_by_area['都道府県'].drop_duplicates())
    selected_location_2 = st.selectbox("都道府県を選択してください", available_prefectures, label_visibility="collapsed")

    # 3. 市区町村のセレクトボックス
    # 都道府県が選択されたら、その都道府県に属する市区町村のみを抽出
    st.image(image_area3)
    if selected_location_2: # 都道府県が選択されている場合
        filtered_df_by_prefecture = filtered_df_by_area[filtered_df_by_area['都道府県'] == selected_location_2]
        available_cities = list(filtered_df_by_prefecture['市区町村'].drop_duplicates())
        selected_location_3 = st.selectbox("市区町村を選択してください", available_cities, label_visibility="collapsed")

        # 4. 災害のセレクトボックス
        # 市区町村が選択されたら、その市区町村に対応する災害の種類のみを抽出
        st.image(image_disaster)
        if selected_location_3: # 市区町村が選択されている場合
            filtered_df_by_area1 = filtered_df_by_prefecture[filtered_df_by_prefecture['市区町村'] == selected_location_3]
            available_disasters = list(filtered_df_by_area1['災害'].drop_duplicates())
            selected_disaster = st.selectbox("災害の種類を選択してください", available_disasters, label_visibility="collapsed")
        else:
            selected_disaster = st.selectbox("災害の種類を選択してください", [], label_visibility="collapsed")
    else:
        selected_location_3 = st.selectbox("市区町村を選択してください", [], label_visibility="collapsed") 
        selected_disaster = st.selectbox("災害の種類を選択してください", [], label_visibility="collapsed") 
else:
    selected_location_2 = st.selectbox("都道府県を選択してください", [], label_visibility="collapsed")
    selected_location_3 = st.selectbox("市区町村を選択してください", [], label_visibility="collapsed")
    selected_disaster = st.selectbox("災害の種類を選択してください", [], label_visibility="collapsed")

# 検索ボタンが押された時の動作
with st.form(key='my_form'):
    #検索ボタンが押された時
    if st.form_submit_button("検索"):
        if selected_location_1 and selected_location_2 and selected_location_3 and selected_disaster:
            selected_row = df[
                (df["エリア"] == selected_location_1) &
                (df["都道府県"] == selected_location_2) &
                (df["市区町村"] == selected_location_3) &
                (df["災害"] == selected_disaster)
            ]

            if not selected_row.empty:
                st.write("### 検索結果")
                # 検索結果のDataFrameを表示
                st.dataframe(selected_row)

                # csvファイルのMAP列からURLを取得し、リンクとして表示
                st.markdown("<h5 style='text-align: left; color: darkturquoise;'>関連マップ</h5>", unsafe_allow_html=True)
                for index, row in selected_row.iterrows():
                    map_url = row["MAP"]
                    map_name = f"{row['市区町村']} の避難場所マップを見る"
                    st.markdown(f"[{map_name}]({map_url})")
            else:
                st.write("該当する避難場所は見つかりませんでした。")
        else:
            st.write("全ての項目を選択してください。")