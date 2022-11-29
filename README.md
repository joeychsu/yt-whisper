# yt-whisper

## 環境安裝 & 執行
 - 先安裝 conda : 
```
conda create --name yt-whisper python=3.8
conda activate yt-whisper
```
 - 把需要的 python packages 裝一裝：
```
pip install -r requirements.txt
```
 - 執行服務：
```
python app.py
```
 - 成功執行後會產生時效為 72 小時的公開連結：
```
Running on public URL: https://xxxxxxxxxxxxxxxx.gradio.app
``` 

## 取得 audio / video / caption 
 - 執行完之後在同目錄下會看到 audio.mp4 / video.mp4 / video.srt 三個檔案

## 參考資料
 - 原始程式碼(https://huggingface.co/spaces/jeffistyping/Youtube-Whisperer)
 - Whisper GitHub(https://github.com/openai/whisper)
 - pytube document(https://pytube.io/en/latest/user/streams.html#filtering-for-mp4-streams)
 - python global用法(http://kaiching.org/pydoing/py/python-global.html)
 