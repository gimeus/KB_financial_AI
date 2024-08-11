import torch
import os
import numpy as np
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from datasets import DatasetDict, Dataset, Audio
from huggingface_hub import HfApi

# Hugging Face에 로그인
api = HfApi()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"


# 모델 및 프로세서 로드
model_name = "openai/whisper-small"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# 오디오 파일 경로 및 트랜스크립션 (다국어 지원)
audio_paths_train = ["C:/Users/csh99/PycharmProjects/kbaimodel1/speech_english.mp3", "C:/Users/csh99/PycharmProjects/kbaimodel1/speech_chinese.mp3"]
audio_paths_test = ["C:/Users/csh99/PycharmProjects/kbaimodel1/speech_english.mp3", "C:/Users/csh99/PycharmProjects/kbaimodel1/speech_chinese.mp3"]

transcriptions_train = ["What kind of supplies do foreigners need to open an account?", "外国人开户需要哪些物资？"]
transcriptions_test = ["What kind of supplies do foreigners need to open an account?", "外国人开户需要哪些物资？"]

def create_dataset(audio_paths, transcriptions):
    dataset = Dataset.from_dict({
        "audio": audio_paths,
        "transcription": transcriptions
    })
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
    return dataset

train_dataset = create_dataset(audio_paths_train, transcriptions_train)
test_dataset = create_dataset(audio_paths_test, transcriptions_test)

common_voice = DatasetDict({
    "train": train_dataset,
    "test": test_dataset
})

def resample_audio(audio, target_sampling_rate=16000):
    waveform, original_sampling_rate = audio
    if original_sampling_rate != target_sampling_rate:
        transform = torchaudio.transforms.Resample(orig_freq=original_sampling_rate, new_freq=target_sampling_rate)
        waveform = transform(waveform)
    return waveform

def preprocess_function(examples):
    audio = examples["audio"]
    audio["array"] = resample_audio((audio["array"], audio["sampling_rate"]))

    inputs = processor(audio["array"], sampling_rate=16000, return_tensors="pt")
    labels = processor.tokenizer(examples["transcription"], return_tensors="pt").input_ids

    # attention_mask 생성 방법 변경: numpy 대신 torch를 직접 사용
    attention_mask = torch.ones_like(labels)

    return {
        "input_features": inputs.input_features.squeeze(0),
        "labels": labels.squeeze(0),
        "attention_mask": attention_mask.squeeze(0)
    }

common_voice = common_voice.map(preprocess_function, remove_columns=["audio", "transcription"])

def collate_fn(batch):
    input_features = torch.stack([torch.tensor(item["input_features"], dtype=torch.float32) for item in batch])
    labels = torch.nn.utils.rnn.pad_sequence([torch.tensor(item["labels"], dtype=torch.long) for item in batch], batch_first=True, padding_value=-100)
    attention_masks = torch.nn.utils.rnn.pad_sequence([torch.tensor(item["attention_mask"], dtype=torch.long) for item in batch], batch_first=True, padding_value=0)

    return {
        "input_features": input_features,
        "labels": labels,
        "attention_mask": attention_masks
    }

train_dataloader = torch.utils.data.DataLoader(common_voice["train"], batch_size=1, shuffle=True, collate_fn=collate_fn)
eval_dataloader = torch.utils.data.DataLoader(common_voice["test"], batch_size=1, collate_fn=collate_fn)

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

trainer.train()

model.save_pretrained("./whisper-finetuned-multilingual")
processor.save_pretrained("./whisper-finetuned-multilingual")
