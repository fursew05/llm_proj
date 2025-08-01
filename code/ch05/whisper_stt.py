import os
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, WhisperProcessor
import pandas as pd
from pyannote.audio import Pipeline
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("HUGGING_TOKEN")
print('HuggingFace Token:', token)

# mp3 파일에 대해서 텍스트로 바꿔주는 함수
def whisper_stt(audio_file_path,stt_output_file_path):
    os.environ["PATH"] += os.pathsep + "C://PMPG//ffmpeg-2025-07-23-git-829680f96a-full_build//bin"
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, 
    use_safetensors=True, use_auth_token=token)

    model.to(device)

    processor = WhisperProcessor.from_pretrained(model_id, use_auth_token=token)

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
    df.to_csv(stt_output_file_path,index=False,encoding='utf-8')
    return result, df

# rttm 파일을 데이터프레임으로 변환하는 함수
def whisper_to_df(result):
    df_list = []
    for chunk in result["chunks"]:
        start = chunk["timestamp"][0]
        end = chunk["timestamp"][1]
        text = chunk["text"].strip()
        df_list.append([start,end,text])
    df = pd.DataFrame(df_list, columns=["start", "end", "text"])
    return df


def spk_diarization(audio_file_path:str,
                    rttm_file_path:str,
                    output_file_path:str):
    pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token=token)

    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda:0"))
        print("cuda is available")
    else:
        pipeline.to(torch.device("cpu"))
        print("cuda is not available")
    
    diarization_pipeline = pipeline(audio_file_path)

    # 화자 구분된 데이터 파일을 rttm 형식으로 저장
    with open(rttm_file_path, "w",encoding='utf-8') as rttm:
        diarization_pipeline.write_rttm(rttm)
    
    # pandas를 활용해서 데이터프레임으로 변환 및 전처리
    df_rttm = pd.read_csv(rttm_file_path,sep=' ',header=None,
    names = ["type","file_name","chnl","start","duration","C1","C2",
"speaker_id","C3","C4"])

    # 화자의 발화 마지막 시점을 나타내는 end 컬럼 만들기
    df_rttm['end'] = df_rttm['start'] + df_rttm['duration']

    # 화자별로 구간을 나누기 위해 number 컬럼 만들기
    df_rttm['number'] = None
    df_rttm.at[0,'number'] = 0

    for i in range(1,len(df_rttm)):
        if df_rttm.at[i,'speaker_id'] != df_rttm.at[i-1,'speaker_id']:
            df_rttm.at[i,'number'] += 1
        else:
            df_rttm.at[i,'number'] = df_rttm.at[i-1,'number']
    
    # number로 그룹화하여 각 화자의 발언마다 구간을 나눠서 묶기기
    df_grouped = df_rttm.groupby('number').agg(
    start = pd.NamedAgg(column='start', aggfunc='min'),
    end = pd.NamedAgg(column='end', aggfunc='max'),
    speaker_id = pd.NamedAgg(column='speaker_id', aggfunc='first')
)

    df_grouped['duration'] = df_grouped['end'] - df_grouped['start']
    df_grouped.to_csv(output_file_path,index=False,encoding='utf-8')
    return df_grouped


# STT와 diarization을 결합하는 함수
def stt_to_rttm(audio_file_path : str,
                stt_output_file_path : str,
                rttm_file_path : str,
                rttm_csv_file_path : str,
                final_output_file_path : str):
    
    result, df_stt = whisper_stt(audio_file_path = audio_file_path,
                                 stt_output_file_path = stt_output_file_path)
    
    df_rttm = spk_diarization(audio_file_path = audio_file_path, 
                              rttm_file_path = rttm_file_path, 
                              output_file_path = rttm_csv_file_path)
    
    # df_rttm에 stt된 문장을 넣을 컬럼 추가
    df_rttm['text'] = ''
    for i_stt, row_stt in df_stt.iterrows():
        overlap_dict = {}
        for i_rttm, row_rttm in df_rttm.iterrows():
            overlap = max(0,min(row_stt['end'],row_rttm['end'])-max(row_stt['start'],row_rttm['start']))
            overlap_dict[i_rttm] = overlap
        max_overlap = max(overlap_dict.values())
        max_overlap_idx = map(overlap_dict,key=overlap_dict.get)

        if max_overlap > 0 :
            df_rttm.at[max_overlap_idx,'text'] += row_stt["text"] + "\n"
    
    df_rttm.to_csv(
        final_output_file_path,
        index=False,
        sep = '|',
        encoding='utf-8'
    )
    return df_rttm

if __name__ == '__main__':

    audio_file_path = "code\ch05\음성녹음.mp3"
    stt_output_file_path = './ch05/output/audio_to_stt.csv'
    rttm_file_path = './ch05/output/audio_diarization.rttm'
    output_file_path = './ch05/output/diarization_output.csv'
    final_output_file_path = './ch05/output/final_output.csv'

    # mp3 -> STT
    result, df = whisper_stt(audio_file_path,stt_output_file_path)

    # mp3 -> diarization
    df_rttm = spk_diarization(audio_file_path = audio_file_path,
                              rttm_file_path = rttm_file_path,
                              output_file_path = output_file_path)

    print(df_rttm.head())
    
    df_rttm = stt_to_rttm(
        audio_file_path = audio_file_path,
        stt_output_file_path = stt_output_file_path,
        rttm_file_path= rttm_file_path,
        rttm_csv_file_path = output_file_path,
        final_output_file_path = final_output_file_path
    )
    print(df_rttm.head())
