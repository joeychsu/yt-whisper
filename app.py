import gradio as gr
import whisper
from pytube import YouTube
from pydub import AudioSegment
import time

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

def inference(input_format, yt_link, video_path):
    global loaded_model
    print("-----------------------------------------------------------")
    if input_format == 'YouTube link' : 
        yt = YouTube(yt_link)
        print("YouTube link = %s" %(yt_link))
        video_path = yt.streams.filter(file_extension='mp4')[0].download(filename="video.mp4")
        sound = AudioSegment.from_file(video_path,format="mp4")
    elif input_format == 'upload video' : 
        print("video path = %s" %(video_path))
        sound = AudioSegment.from_file(video_path,format="mp4")
    audio_path = "./audio.wav"
    sound.export(audio_path, format="wav")
    duration = sound.duration_seconds
    start = time.time()
    # task = [transcribe/translate] ; language = [None/english/chinese]
    results = loaded_model.transcribe(audio=audio_path, without_timestamps=False, task="transcribe", language=None)
    end = time.time()
    video_srt = "./video.srt"
    ofp = open(video_srt,'w')
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
    spend_time = end - start
    rtf = spend_time / duration
    print("time：%0.2f second" % (spend_time))
    print("RTF ：%0.2f " % (rtf))
    print("-----------------------------------------------------------")
    infos =  "time："+str(round(spend_time,2))+" second\n"
    infos += "RTF ："+str(round(rtf,2))+" \n"
    text_results = results['text']
    return_list = [text_results]
    if input_format == 'YouTube link' : 
        return_list.append(gr.Textbox().update(value=infos))
        return_list.append(gr.File().update(visible=True, value=video_path))
        return_list.append(gr.File().update(visible=True, value=video_srt))
        return_list.append(gr.Textbox().update(value="time：?? second\nRTF ：?? \n"))
        return_list.append(gr.File().update(visible=False))
        return_list.append(gr.File().update(visible=False))
    elif input_format == 'upload video' : 
        return_list.append(gr.Textbox().update(value="time：?? second\nRTF ：?? \n"))
        return_list.append(gr.File().update(visible=False))
        return_list.append(gr.File().update(visible=False))
        return_list.append(gr.Textbox().update(value=infos))
        return_list.append(gr.File().update(visible=True, value=video_path))
        return_list.append(gr.File().update(visible=True, value=video_srt))
    return return_list

def populate_metadata(link):
  yt = YouTube(link)
  # yt.title
  return yt.thumbnail_url

current_size = 'large'
loaded_model = whisper.load_model(current_size)

title="Youtube Whisperer"
description="Speech to text transcription of videos(or YouTube Link) using OpenAI's Whisper"
block = gr.Blocks()

def chage_format(input_format) : 
    if input_format == 'YouTube link' : 
        return gr.Box().update(visible=True), gr.Box().update(visible=False)
    elif input_format == 'upload video' : 
        return gr.Box().update(visible=False), gr.Box().update(visible=True)
    else : 
        exit(1)

with block:
    gr.HTML(
        """
            <div style="text-align: center; max-width: 500px; margin: 0 auto;">
              <div>
                <h1 style="font-size: 120%">Automatic Captioning</h1>
              </div>
              <p style="margin-bottom: 10px; font-size: 94%">
                Speech to text transcription of videos(or YouTube Link) using OpenAI's Whisper<br>
                Model Size : Large<br>
              </p>
            </div>
        """
    )
    with gr.Group():
        with gr.Box():
        
            input_format = gr.Dropdown(label="Input Format", choices=['YouTube link', 'upload video'], value='YouTube link')
          
            yt_link_box = gr.Box(visible=True)
            up_video_box = gr.Box(visible=False)
          
            with yt_link_box : 
                yt_link = gr.Textbox(label="YouTube Link")
                with gr.Row().style(mobile_collapse=False, equal_height=True):
                    with gr.Column():
                        yt_link_mp4_download = gr.File(visible=False)
                        yt_link_srt_download = gr.File(visible=False)
                        yt_link_results = gr.Textbox(label="info", value="time：?? second\nRTF ：?? \n")
                    img = gr.Image(label="Thumbnail")
          
            with up_video_box : 
                with gr.Row().style(mobile_collapse=False, equal_height=True):
                    with gr.Column():
                        up_video_mp4_download = gr.File(visible=False)
                        up_video_srt_download = gr.File(visible=False)
                        up_video_results = gr.Textbox(label="info", value="time：?? second\nRTF ：?? \n")
                    video = gr.Video()
          
            text = gr.Textbox(
                label="Transcription", 
                placeholder="Transcription Output",
                lines=5)
            with gr.Row().style(mobile_collapse=False, equal_height=True): 
                btn = gr.Button("Transcribe")
          
            # Events
            btn.click(inference, inputs=[input_format, yt_link, video], 
                                 outputs=[text, yt_link_results, yt_link_mp4_download, yt_link_srt_download, 
                                                up_video_results, up_video_mp4_download, up_video_srt_download])
            yt_link.change(populate_metadata, inputs=[yt_link], outputs=[img])
            input_format.change(chage_format, inputs=[input_format], outputs=[yt_link_box, up_video_box])

block.launch(debug=True, share=True, server_port=7860) # auth=("zzz", "1234")
