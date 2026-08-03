import streamlit as st
import yt_dlp
import os
import tempfile

# ページの基本設定
st.set_page_config(page_title="Web音声ダウンローダー", page_icon="🎵")

st.title("🎵 Web音声ダウンローダー")
st.write("YouTubeなどのURLを入力して、MP3形式でダウンロードできます。")

# URL入力欄
url = st.text_input("動画のURLを入力してください:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("音声を抽出・準備", type="primary"):
    if not url:
        st.warning("URLを入力してください。")
    else:
        with st.spinner("音声をダウンロード・変換中... (しばらくお待ちください)"):
            try:
                # 一時フォルダを作成して処理
                with tempfile.TemporaryDirectory() as tmpdirname:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'noplaylist': True,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': os.path.join(tmpdirname, '%(title)s.%(ext)s'),
                        
                        # ★ HTTP Error 403 (ブロック) を回避するための設定
                        'quiet': True,
                        'no_warnings': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        },
                        # YouTube側のプレイヤー偽装
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['android', 'web']
                            }
                        }
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get('title', 'audio')
                        
                        # 変換後のファイル（.mp3）を探す
                        file_path = None
                        for file in os.listdir(tmpdirname):
                            if file.endswith('.mp3'):
                                file_path = os.path.join(tmpdirname, file)
                                break

                        if file_path and os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                audio_bytes = f.read()

                            st.success("準備が完了しました！")
                            # ブラウザ側で直接ダウンロードさせるボタンを表示
                            st.download_button(
                                label="💾 MP3ファイルを保存",
                                data=audio_bytes,
                                file_name=f"{title}.mp3",
                                mime="audio/mpeg"
                            )
                        else:
                            st.error("変換後のファイルが見つかりませんでした。")

            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")