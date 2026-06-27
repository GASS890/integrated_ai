# Voice Training Workspace

## Purpose

This workspace prepares reusable voice training data.

Flow:

raw_voice
-> cleaned_voice
-> transcripts
-> stylebert_dataset
-> teacher_audio
-> piper_dataset
-> exports

## Roles

- raw_voice: original recordings
- cleaned_voice: cleaned and normalized voice samples
- transcripts: text scripts
- stylebert_dataset: Style-Bert-VITS2 training dataset
- teacher_audio: high-quality generated teacher voice
- piper_dataset: Piper Plus training dataset
- exports: trained models and exported packages
- configs: training configuration

## Current Policy

- Do not train directly from unchecked audio.
- Keep original recordings.
- Use Style-Bert-VITS2 as teacher TTS.
- Use Piper Plus as lightweight student TTS.
