# Demo Conversation Test

## Purpose

AI応答が以下の流れで動くか確認する。

User
-> LLM応答
-> queue_assistant_reply_to_speaker
-> Piper Plus音声生成
-> Speaker Queue
-> Speaker Worker
-> 自動再生

## Test File

test_demo_conversation.py

## Check BAT

check_demo_conversation.bat

## Expected Result

- auto_enqueue_ai_response: True
- queue_size が一度 1 になる
- 数秒後 queue_size が 0 になる
- total_played が増える
- 音声が再生される

## Notes

この段階では、LLM本体へ問い合わせる代わりに、
AI応答文を直接 queue_assistant_reply_to_speaker() に渡して、
音声出力経路を確認する。
