import gradio as gr
import whisper
from pytube import YouTube

loaded_model = whisper.load_model("large")
current_size = 'large'

def hundred2sixty(str1) : 
  str1 = int(str1)
  second = str(str1 % 60000)
  min = int(str1 / 60000)
  hour = str(int(min / 60))
  min = str(min % 60)
  while len(second) < 5 : 
    second = "0"+str(second)
  if len(min) < 2 : 
    min = "0"+str(min)
  if len(hour) < 2 : 
    hour = "0"+str(hour)
  return str(hour), str(min), str(second)

def inference(link):
  global loaded_model
  yt = YouTube(link)
  video_path = yt.streams.filter(file_extension='mp4')[0].download(filename="video.mp4")
  audio_path = yt.streams.filter(only_audio=True)[0].download(filename="audio.mp4")
  options = whisper.DecodingOptions(without_timestamps=False)
  results = loaded_model.transcribe(audio_path)
  ofp = open("video.srt",'w')
  for seg_info in results['segments'] : 
    ofp.write(str(seg_info["id"])+"\n")
    start_time = str(int(seg_info["start"]*1000.0))
    h, m, s = hundred2sixty(start_time)
    start_time = h + ":" + m + ":" + s[0:2] + "," + s[2:]
    end_time = str(int(seg_info["end"]*1000.0))
    h, m, s = hundred2sixty(end_time)
    end_time = h + ":" + m + ":" + s[0:2] + "," + s[2:]
    ofp.write(str(start_time)+" --> "+str(end_time)+"\n")
    ofp.write(str(seg_info["text"])+"\n")
    ofp.write("\n")
  ofp.close()
  return results['text']

def change_model(size):
  global current_size, loaded_model
  if size == current_size:
    return
  loaded_model = whisper.load_model(size)
  current_size = size

def populate_metadata(link):
  yt = YouTube(link)
  return yt.thumbnail_url, yt.title

title="Youtube Whisperer"
description="Speech to text transcription of Youtube videos using OpenAI's Whisper"
block = gr.Blocks()

with block:
    gr.HTML(
        """
            <div style="text-align: center; max-width: 500px; margin: 0 auto;">
              <div>
                <h1>Youtube Whisperer</h1>
              </div>
              <p style="margin-bottom: 10px; font-size: 94%">
                Speech to text transcription of Youtube videos using OpenAI's Whisper
              </p>
            </div>
        """
    )
    with gr.Group():
        with gr.Box():
          sz = gr.Dropdown(label="Model Size", choices=['base','small', 'medium', 'large'], value='large')
          
          link = gr.Textbox(label="YouTube Link")
          
          with gr.Row().style(mobile_collapse=False, equal_height=True):
            title = gr.Label(label="Video Title", placeholder="Title")
            img = gr.Image(label="Thumbnail")
          text = gr.Textbox(
              label="Transcription", 
              placeholder="Transcription Output",
              lines=5)
          with gr.Row().style(mobile_collapse=False, equal_height=True): 
              btn = gr.Button("Transcribe")       
          
          # Events
          btn.click(inference, inputs=[link], outputs=[text])
          link.change(populate_metadata, inputs=[link], outputs=[img, title])
          sz.change(change_model, inputs=[sz], outputs=[])

block.launch(debug=True, share=True)
