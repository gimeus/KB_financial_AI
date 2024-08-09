# -*- coding: utf-8 -*-
"""0808multilang.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GnpGCAtuD-dd7sLXlH-sIDRnExm2Rrta
"""

# 필요한 라이브러리 설치
# pip install transformers datasets torchaudio huggingface_hub

import torch
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from datasets import DatasetDict, Dataset, Audio
from huggingface_hub import notebook_login

# Hugging Face에 로그인
notebook_login()

# 모델 및 프로세서 로드
model_name = "openai/whisper-small"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# # 특수 토큰 추가 및 임베딩 초기화
# special_tokens_dict = {'additional_special_tokens': ['<special1>', '<special2>']}
# num_added_toks = processor.tokenizer.add_special_tokens(special_tokens_dict)
# model.resize_token_embeddings(len(processor.tokenizer))

# # 새로운 특수 토큰에 대한 임베딩을 초기화
# model.get_input_embeddings().weight.data[-num_added_toks:] = model.get_input_embeddings().weight.data.mean(dim=0)

# 오디오 파일 경로 및 트랜스크립션 (다국어 지원)
audio_paths_train = ["/content/sample_data/speech_english.mp3", "/content/sample_data/speech_chinese.mp3"]  # 실제 훈련 오디오 파일 경로
audio_paths_test = ["/content/sample_data/speech_english.mp3", "/content/sample_data/speech_chinese.mp3"]  # 실제 테스트 오디오 파일 경로

# 실제 트랜스크립션 입력 (다국어)
transcriptions_train = ["What kind of supplies do foreigners need to open an account?", "外国人开户需要哪些物资？"]
transcriptions_test = ["What kind of supplies do foreigners need to open an account?", "外国人开户需要哪些物资？"]

# 오디오 파일을 데이터셋으로 변환
def create_dataset(audio_paths, transcriptions):
    dataset = Dataset.from_dict({
        "audio": audio_paths,
        "transcription": transcriptions
    })
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
    return dataset

# 데이터셋 로드
train_dataset = create_dataset(audio_paths_train, transcriptions_train)
test_dataset = create_dataset(audio_paths_test, transcriptions_test)

# 데이터셋 병합
common_voice = DatasetDict({
    "train": train_dataset,
    "test": test_dataset
})

# 오디오 리샘플링 함수 추가
def resample_audio(audio, target_sampling_rate=16000):
    waveform, original_sampling_rate = audio
    if original_sampling_rate != target_sampling_rate:
        transform = torchaudio.transforms.Resample(orig_freq=original_sampling_rate, new_freq=target_sampling_rate)
        waveform = transform(waveform)
    return waveform

# 데이터셋 전처리
def preprocess_function(examples):
    audio = examples["audio"]
    audio["array"] = resample_audio((audio["array"], audio["sampling_rate"]))
    inputs = processor(audio["array"], sampling_rate=16000, return_tensors="pt")
    labels = processor.tokenizer(examples["transcription"], return_tensors="pt").input_ids

    # 여기에서 attention_mask를 추가로 생성합니다.
    attention_mask = processor.tokenizer(examples["transcription"], return_tensors="pt").attention_mask

    return {
        "input_features": inputs.input_features.squeeze(0),
        "labels": labels.squeeze(0),

        # attention_mask 반환
        "attention_mask": attention_mask.squeeze(0)
    }

# 전처리된 데이터셋 생성
common_voice = common_voice.map(preprocess_function, remove_columns=["audio", "transcription"])

# 데이터 로더 설정
def collate_fn(batch):
    input_features = torch.stack([torch.tensor(item["input_features"], dtype=torch.float32) for item in batch])
    labels = torch.nn.utils.rnn.pad_sequence([torch.tensor(item["labels"], dtype=torch.long) for item in batch], batch_first=True, padding_value=-100)

    # 여기에서 attention_mask를 추가로 패딩합니다.
    attention_masks = torch.nn.utils.rnn.pad_sequence([torch.tensor(item["attention_mask"], dtype=torch.long) for item in batch], batch_first=True, padding_value=0)

    return {
        "input_features": input_features,
        "labels": labels,

        # attention_mask 반환
        "attention_mask": attention_masks
    }

train_dataloader = torch.utils.data.DataLoader(common_voice["train"], batch_size=1, shuffle=True, collate_fn=collate_fn)
eval_dataloader = torch.utils.data.DataLoader(common_voice["test"], batch_size=1, collate_fn=collate_fn)

# 학습 설정
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments

training_args = Seq2SeqTrainingArguments(
    output_dir="./whisper-finetuned-multilingual",
    per_device_train_batch_size=1,
    evaluation_strategy="epoch",
    learning_rate=5e-5,
    num_train_epochs=3,
    save_steps=500,
    save_total_limit=2,
    fp16=True,
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=common_voice["train"],
    eval_dataset=common_voice["test"],
    data_collator=collate_fn,
)

# 모델 파인 튜닝
trainer.train()

# 모델 저장
model.save_pretrained("./whisper-finetuned-multilingual")
processor.save_pretrained("./whisper-finetuned-multilingual")

import torch
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration

model_path = "./whisper-finetuned-multilingual"
processor = WhisperProcessor.from_pretrained(model_path)
model = WhisperForConditionalGeneration.from_pretrained(model_path)

# 새로운 오디오 파일 경로
audio_path = "/content/sample_data/speech_where_chinese.mp3"

# 오디오 파일 로드 및 리샘플링
waveform, sample_rate = torchaudio.load(audio_path)
if sample_rate != 16000:
    waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)

# 입력 데이터 전처리
inputs = processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt")

# 모델을 사용하여 텍스트 예측
with torch.no_grad():
    generated_ids = model.generate(inputs.input_features)

# 예측된 텍스트 디코딩
transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print("Transcription:", transcription)

!pip install transformers

# from transformers import GPT2Tokenizer, GPT2LMHeadModel

# # 커스텀 GPT 모델 이름
# model_name = "finance_LAGUNHO"  # 실제 모델 이름으로 변경

# # 모델 및 토크나이저 로드
# tokenizer = GPT2Tokenizer.from_pretrained(model_name)
# model = GPT2LMHeadModel.from_pretrained(model_name)

# # 입력 텍스트 설정 (STT 결과 또는 기타 텍스트)
# input_text = "여기에 입력 텍스트를 넣으세요"

# # 텍스트를 토큰으로 변환
# inputs = tokenizer.encode(input_text, return_tensors="pt")

# # 모델을 사용하여 텍스트 예측
# outputs = model.generate(inputs, max_length=512, num_return_sequences=1)

# # 예측된 텍스트 디코딩
# predicted_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
# print("Predicted Text:", predicted_text)