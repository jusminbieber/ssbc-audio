import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="Web音声ダウンローダー", page_icon="🎵")

st.title("🎵 Web音声ダウンローダー")
st.write("YouTubeなどのURLを入力して、MP3形式でダウンロードできます。")

url = st.text_input("動画のURLを入力してください:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("音声を抽出・準備", type="primary"):
    if not url:
        st.warning("URLを入力してください。")
    else:
        with st.spinner("音声をダウンロード・変換中... (しばらくお待ちください)"):
            try:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    ydl_opts = {
                        'format': 'ba/ba*', # 最高品質の音声
                        'noplaylist': True,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': os.path.join(tmpdirname, '%(title)s.%(ext)s'),
                        
                        # ★ 403 Forbidden（ブロック）対策の核心設定
                        'nocheckcertificate': True,
                        'ignoreerrors': False,
                        'logtostderr': False,
                        'quiet': True,
                        'no_warnings': True,
                        'default_search': 'auto',
                        'source_address': '0.0.0.0', # IPv4通信を強制（IPv6ブロック対策）
                        
                        # クライアントの偽装（IOS/TV等）
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['ios', 'android', 'web_creator'],
                                'player_skip': ['webpage', 'configs']
                            }
                        },
                        'http_headers': {
                            'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 11; US) gzip',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                        }
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get('title', 'audio')
                        
                        file_path = None
                        for file in os.listdir(tmpdirname):
                            if file.endswith('.mp3'):
                                file_path = os.path.join(tmpdirname, file)
                                break

                        if file_path and os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                audio_bytes = f.read()

                            st.success("準備が完了しました！")
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