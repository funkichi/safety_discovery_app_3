import streamlit as st
from PIL import Image, ExifTags
from io import BytesIO
import base64
from openai import OpenAI
import os
import io
import httpx

# OpenAI APIキーの設定
OPENAI_API_KEY = st.secrets["openai_api_key"]

client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=httpx.Client(proxies=None) # プロキシをNoneに設定※そうしないとStreamlitcloudでエラーでる。
)

# 画像の回転を修正する関数
def correct_image_orientation(pil_image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = pil_image._getexif()
        if exif is not None:
            # Orientationタグの値を取得
            orientation_value = exif.get(orientation)
            
            # Orientationタグの値から画像を回転
            if orientation_value == 3:
                pil_image = pil_image.transpose(Image.ROTATE180)
            elif orientation_value == 6:
                pil_image = pil_image.transpose(Image.ROTATE270) # 反時計回りに270度 = 時計回りに90度
            elif orientation_value == 8:
                pil_image = pil_image.transpose(Image.ROTATE90)  # 反時計回りに90度 = 時計回りに270度
        
    except (AttributeError, KeyError, IndexError):
        # Exifデータがない場合やOrientationタグがない場合は何もしない
        pass
    
    return pil_image

#画像サイズを変数に代入
size_logo = (350, 350)
size_option = (180, 180)

#画像ファイルを読み込んでthumbnailでサイズを指定
image_logo = Image.open('Material/logo.png')
image_logo.thumbnail(size_logo)

#画像を保存
image_logo.save("Material/logo.png")

#画像をバイト列として読み込みbase64エンコードする(streamlitではHTMLタグで参照できないため)
def get_image_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

#base64エンコードされた文字列を取得
img_str_logo = get_image_base64(image_logo)

#HTMLで画像を表示する
st.markdown(f'<p style="text-align: center;"><img src="data:image/png;base64,{img_str_logo}"></p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png", "gif"])

if uploaded_file is not None:
    # アップロードされたファイルをPIL Imageとして開く
    image = Image.open(uploaded_file)

    # ここで画像の向きを修正
    image = correct_image_orientation(image)

    st.image(image, caption="アップロードされた画像", use_column_width=True)
    st.write("画像を解析しています。しばらくお待ちください...")

    # 画像をBase64エンコードする関数
    def encode_image_to_base64(pil_image):
        buffered = BytesIO()
        # 画像のフォーマットがPNGの場合、RGBAモードで保存
        if pil_image.mode == 'RGBA' and pil_image.format == 'PNG':
            pil_image.save(buffered, format="PNG")
        elif pil_image.mode == 'RGBA' and pil_image.format is None:
             pil_image.save(buffered, format="PNG")
        else: # その他の場合はJPEGとして保存
            if pil_image.mode == 'RGBA':
                # RGBAをRGBに変換してJPEGとして保存
                pil_image = pil_image.convert('RGB')
            pil_image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 画像をBase64形式に変換
    base64_image = encode_image_to_base64(image)

    try:
        # プロンプト
        vision_prompt = """
        画像の状況を説明し、考慮すべき危険を洗い出してください。
        また、以下の"###要件"に従って回答してください。

        ###要件
        ・アウトプットの形式は以下の"アウトプットの例"と同じ形式で出力してください。
        ・質問に対する回答のみをアウトプットしてください。例えば、"他に質問はありますか？"などの文言は必要ありません。
        ・"アウトプットの例"に書いている"<改行>"の行は必ず改行してください。
        ・"■"から始まる行の文字は見出しなので、目立つように太字にしてフォントサイズも大きくしてください。
        ・考慮すべき危険が無いと判断した場合は、この場所に危険が無い事とその理由を説明してください。
        ・この質問は、始めて訪れる場所やめったに訪れない場所に行った時、災害や事故に巻き込まれるリスクを減らすことを目的としています。

        ###アウトプットの例
        ■状況説明 "<改行>"
        この画像は、フォークリフトが積荷（ラップで巻かれた大きな荷物を2段重ね）を運搬している様子を写しています。フォークリフトは、トラックの荷台近くのスロープ（プラットフォーム）上にあり、荷物の積み下ろし作業中と思われます。

        ■考慮すべき危険（リスク洗い出し） "<改行>"
        1. 視界不良による事故 "<改行>"
        ・荷物が大きく高く積まれているため、運転者の前方視界が極端に悪くなり、歩行者や障害物の発見が遅れるリスク。
        2. 荷崩れ・落下の危険 "<改行>"
        ・荷物が2段重ねで高く積まれているため、バランスを崩すと荷物が落下し、運転者や周囲の人に危害を及ぼす可能性。
        3. フォークリフトの転倒リスク "<改行>"
        ・高積み・重心が高くなることで、曲がる・傾いた際にフォークリフト自体が転倒する危険。
        4. スロープ・段差によるリスク "<改行>"
        ・フォークリフトがスロープ上にいるため、荷物の重さ・高さによっては傾斜でバランスを崩しやすい。
        5. 接触・衝突の危険 "<改行>"
        ・手すりやトラックの荷台など周囲に構造物が多く、荷物やフォークリフトが接触・衝突する恐れ。
        6. 荷物の固定不良 "<改行>"
        ・ラップで巻かれているが、固定が不十分だと運搬中に荷崩れする可能性。
        7. 周辺作業者との接触 "<改行>"
        ・プラットフォームは人の通行も多い場所であり、歩行者との接触事故も懸念される。
        8. トラックとの隙間・段差転落リスク "<改行>"
        ・トラックの荷台との隙間や段差にタイヤや荷物が落ちて、フォークリフトがバランスを崩す危険。

        ■安全対策例 "<改行>"
        ・荷物は視界確保のため可能な限り低く積む。 "<改行>"
        ・荷物の固定・ラッピングを十分に行う。 "<改行>"
        ・スロープや段差では特に速度を落として慎重に運転する。 "<改行>"
        ・周囲に人がいないことを確認しながら作業する。 "<改行>"
        ・必要に応じて誘導員を配置する。 "<改行>"
        ・フォークリフト運転者の教育・訓練を徹底する。 "<改行>"

        ■まとめ "<改行>"
        この画像は「高積み荷物の運搬時のリスク」が顕著に現れているため、特に「視界不良」「荷崩れ」「転倒」に注意が必要です。
        """

        # Vision APIを使って画像をサーチ
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt}, 
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}", # Base64エンコードされた画像データをURLとして渡す
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            max_tokens=2000,
        )
        
        vision_response_content = response.choices[0].message.content.strip()
        st.subheader("サーチ結果")
        st.write(vision_response_content)

    except Exception as e:
        st.error(f"解析ツールとの接続でエラーが発生しました: {e}")
        st.error("アプリ開発者へ問い合わせてください。")
else:
    st.write("画像をアップロードしてください。")