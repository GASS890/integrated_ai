# Voice Migration Plan

## 方針

Piperへ移行する。

Piperが使用可能になった段階で、独自音声学習を優先する。

## 学習方針

1. Style-Bert-VITS2で高品質な音声を生成する
2. 生成音声を品質チェックする
3. Piper学習用データセットへ変換する
4. Piper系軽量TTSを学習する
5. スピーカー・スマホ向けに軽量運用する

## 分散構成

### スピーカー
- マイク入力
- ウェイクワード検出
- Piper Plus / Piper TTS
- 音声再生

### スマホ
- 脳
- 人格
- 短期記憶
- UI
- TTSバックエンド選択

### PC
- 長期記憶DB
- Embedding検索
- 記憶整理
- Style-Bert-VITS2生成
- Piper学習
- 重いLLM処理

### クラウド
- バックアップ
- 同期
- 復元用データ保存

## ディレクトリ

datasets/voice/style_bert_vits2_generated/
- Style-Bert-VITS2で生成した高品質wavを置く

datasets/voice/piper_training/
- Piper学習用に整形したデータを置く

## 注意

合成音声だけでPiperを学習すると、元TTSの癖やノイズも学習する。
可能なら少量の独自音声を混ぜる。
