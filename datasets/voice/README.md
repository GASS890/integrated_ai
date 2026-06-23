# Voice Dataset Plan

## Purpose

This directory is for future custom voice training.

## Flow

raw/your_voice
-> transcripts
-> Style-Bert-VITS2
-> checked
-> Piper Plus training
-> speaker/smartphone deployment

## Roles

- raw/your_voice: original recorded voice samples
- transcripts: text paired with audio
- style_bert_vits2: high-quality generated speech
- checked: human-checked usable samples
- piper_plus: Piper Plus training-ready dataset
- archive: backup and old versions
- exports: exported model/data packages

## Policy

- Do not train directly from unchecked audio.
- Prefer clean, short clips.
- Keep text and wav filenames paired.
- Use Style-Bert-VITS2 as high-quality teacher audio before Piper Plus training.
