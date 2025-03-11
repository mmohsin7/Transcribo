from deep_translator import GoogleTranslator
from gradio.themes.base import Base
import gradio as gr
import datetime
import whisper

# Create Subtitles Format
def Format_Timestamp(Seconds):
    TimeDelta = datetime.timedelta(seconds=Seconds)
    Total_Seconds = int(TimeDelta.total_seconds())
    Hours = Total_Seconds // 3600
    Minutes = (Total_Seconds % 3600) // 60
    Seconds = Total_Seconds % 60
    Milliseconds = int((TimeDelta.total_seconds() - Total_Seconds) * 1000)
    return f"{Hours:02}:{Minutes:02}:{Seconds:02},{Milliseconds:03}"

# Transcribe the Audio File
def Transcribe_Audio(Audio_File):
    model = whisper.load_model("base")
    result = model.transcribe(Audio_File)
    Text = result["text"]

    # Create SRT File
    Srt_File_Path = "TranscriboSubtitles.srt"
    Subtitles = ""
    with open(Srt_File_Path, "w", encoding="utf-8") as Srt_File:
        for i, seg in enumerate(result["segments"], start=1):
            Start_Time = Format_Timestamp(seg['start'])
            End_Time = Format_Timestamp(seg['end'])
            Srt_File.write(f"{i}\n{Start_Time} --> {End_Time}\n{seg['text']}\n\n")
            Subtitles += f"{i}\n{Start_Time} --> {End_Time}\n{seg['text']}\n\n"

    # Create TXT File
    Text_File_Path = "TranscriboTranscription.txt"
    with open(Text_File_Path, "w", encoding="utf-8") as Txt_File:
        Txt_File.write(Text)

    return Text, Subtitles, Text_File_Path, Srt_File_Path

# Translate the Transcription Text
def Translate_Text(Text, Target_Language):
    Translator = GoogleTranslator(source="auto", target=Target_Language)
    Translated_Text = Translator.translate(Text)

    # Create Translated TXT File
    Translated_File_Path = "TranscriboTranslatedTranscription.txt"
    with open(Translated_File_Path, "w") as Txt_File:
        Txt_File.write(Translated_Text)

    return Translated_Text, Translated_File_Path

# Translate the Subtitles
def Generate_Translated_Subtitles(Subtitles, Target_Language):
    Translator = GoogleTranslator(source="auto", target=Target_Language)
    Translated_Lines = []

    for Line in Subtitles.split("\n"):
        if "-->" in Line:
            Translated_Lines.append(Line)
        elif Line.strip().isdigit():
            Translated_Lines.append(Line)
        else:
            Translated_Lines.append(Translator.translate(Line))
    
    Translated_Subtitles = "\n".join(Translated_Lines)
    
    # Create Translated SRT File
    Translated_Srt_File_Path = "TranscriboTranslatedSubtitles.srt"
    with open(Translated_Srt_File_Path, "w", encoding="utf-8") as Srt_File:
        Srt_File.write(Translated_Subtitles)

    return Translated_Subtitles, Translated_Srt_File_Path

# All Available Languages in deep_translator
Languages = {
    "af": "Afrikaans", "ar": "Arabic", "bn": "Bengali", "zh": "Chinese", "cs": "Czech", "da": "Danish", "nl": "Dutch",
    "en": "English", "fi": "Finnish", "fr": "French", "de": "German", "el": "Greek", "hi": "Hindi", "hu": "Hungarian",
    "id": "Indonesian", "it": "Italian", "ja": "Japanese", "ko": "Korean", "no": "Norwegian", "fa": "Persian", "pl": "Polish",
    "pt": "Portuguese", "ru": "Russian", "es": "Spanish", "sv": "Swedish", "ta": "Tamil", "th": "Thai", "tr": "Turkish",
    "uk": "Ukrainian", "ur": "Urdu", "vi": "Vietnamese"
}

# Customize UI
class Seafoam(Base):
    pass
seafoam = Seafoam(font=gr.themes.GoogleFont("Plus Jakarta Sans"))

style ="""
    .gradio-audio {
        border-radius: 15px !important;
    }
    .gradio-primary-button {
        background: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 20px;
    }
    .gradio-primary-button:hover {
        background: #0056b3;
    }
    .gradio-dropdown {
        background: #00000000;
    }
    .gradio-secondary-button {
        background: #00000000;
        border: 1.5px solid var(--input-border-color);
        font-weight: bold;
        border-radius: 20px;
    }
    .gradio-secondary-button:hover {
        background: var(--input-border-color);
    }
    label.container.show_textbox_border.svelte-173056l textarea.svelte-173056l {
        background: #00000000;
        border-radius: 20px;
    }
    div.svelte-633qhp {
        border-radius: 15px;
        overflow-y: hidden;
    }
    span.svelte-1gfkn6j {
        padding-left: 20px,
        font-size: 16px;
        font-weight: bold;
    }
    .gradio-container.gradio-container-5-16-0 .contain span.svelte-1gfkn6j {
        padding-left: 12px;
    }
    .icon-button-wrapper.hide-top-corner.svelte-1jx2rq3 {
        border-radius: 20px;
        margin: 5px 6.09px 0px 0px;
        padding: 6px 5.5px 5px 5.5px;
    }
"""

# Gradio Interface with Better UI
with gr.Blocks(theme=seafoam, css=style) as iface:
    gr.Markdown("# Transcribo")
    with gr.Column():
        audio_input = gr.Audio(type="filepath", label="Upload Audio", elem_classes=["gradio-audio"])
        transcribe_btn = gr.Button("Transcribe", elem_classes=["gradio-primary-button"])

    with gr.Row():
        transcribed_text = gr.Textbox(label="Transcribed Text", placeholder="Transcribed Text will appear here ...")
        subtitles_text = gr.Textbox(label="Subtitles", placeholder="Subtitles will appear here ...")

    with gr.Row():
        download_text_btn = gr.DownloadButton("Download Transcription", value="TranscriboTranscription.txt", visible=False, elem_classes=["gradio-secondary-button"])
        download_srt_btn = gr.DownloadButton("Download Subtitles (.srt)", value="TranscriboSubtitles.srt", visible=False, elem_classes=["gradio-secondary-button"])

    with gr.Column():
        target_language = gr.Dropdown(label="Select Target Language", choices=list(Languages.values()), value="English", elem_classes=["gradio-dropdown"])
        translate_btn = gr.Button("Translate", elem_classes=["gradio-primary-button"])

    with gr.Row():
        translated_text = gr.Textbox(label="Translated Text", placeholder="Translated Text will appear here ...")
        translated_subtitles_text = gr.Textbox(label="Translated Subtitles", placeholder="Translated Subtitles will appear here ...")
    with gr.Row():
        download_translated_btn = gr.DownloadButton("Download Translation", value="TranscriboTranslatedTranscription.txt", visible=False, elem_classes=["gradio-secondary-button"])
        download_translated_srt_btn = gr.DownloadButton("Download Translated Subtitles (.srt)", value="TranscriboTranslatedSubtitles.srt", visible=False, elem_classes=["gradio-secondary-button"])

    def generate_download_links(audio_file):
        text, subtitles, text_file, srt_file = Transcribe_Audio(audio_file)
        return text, subtitles, gr.update(value=text_file, visible=True), gr.update(value=srt_file, visible=True)

    def generate_translation_and_subtitles(text, subtitles, target_language_label):
        target_language_code = next(code for code, name in Languages.items() if name == target_language_label)
        translated_text, translated_file = Translate_Text(text, target_language_code)
        translated_subtitles, translated_srt_file = Generate_Translated_Subtitles(subtitles, target_language_code)
        return translated_text, translated_subtitles, gr.update(value=translated_file, visible=True), gr.update(value=translated_srt_file, visible=True)

    transcribe_btn.click(generate_download_links, inputs=audio_input, outputs=[transcribed_text, subtitles_text, download_text_btn, download_srt_btn])
    translate_btn.click(generate_translation_and_subtitles, inputs=[transcribed_text, subtitles_text, target_language], outputs=[translated_text, translated_subtitles_text, download_translated_btn, download_translated_srt_btn])

#This launch the app with Gradio interface
if __name__ == "__main__":
    iface.launch(share=True, inbrowser=True)