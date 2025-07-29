import os
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import pandas as pd



def whisper_stt(audio_file_path):
    os.environ["PATH"] += os.pathsep + "C://PMPG//ffmpeg-2025-07-23-git-829680f96a-full_build//bin"
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, 
    use_safetensors=True
)
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    return_timestamps=True,
    chunk_length_s=5,
    stride_length_s=1,
)

    result = pipe(audio_file_path)
    df = whisper_to_df(result)
    return result, df

def whisper_to_df(result):
    df_list = []
    for chunk in result["chunks"]:
        start = chunk["timestamp"][0]
        end = chunk["timestamp"][1]
        text = chunk["text"].strip()
        df_list.append([start,end,text])
    df = pd.DataFrame(df_list, columns=["start", "end", "text"])
    return df

if __name__ == '__main__':
    audio_file_path = "C://Users//fursew//project//open_ai//code//ch05//음성녹음.mp3"
    result, df = whisper_stt(audio_file_path)
    df.to_csv("음성녹음_rttm.csv",index=False)
