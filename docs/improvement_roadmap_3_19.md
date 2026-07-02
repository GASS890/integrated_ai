# 改善ロードマップ 3〜19

## 3. Embedding長期記憶
変更箇所:
- memory/embedding_store.py
- memory/vector_search.py
- memory/memory_reflection.py
- memory/memory_ranker.py

第1段階:
- JSON保存
- 疑似embedding
- 類似検索
- 長期記憶化判定
- 記憶ランキング

今後:
- Ollama embedding
- sentence-transformers
- OpenAI embedding
- ベクトルDB化

## 4. 改善案3案提示
案A: 安全重視の小規模変更
- メリット: 壊れにくい
- リスク: 改善速度が遅い

案B: 中規模変更
- メリット: 効果と安全性のバランス
- リスク: テスト不足時に一部破損

案C: 大規模自動改修
- メリット: 改善速度が速い
- リスク: 破壊的変更が起きやすい

## 5. 自律改善ループ
分析 → 改善案 → 実装 → 検証 → 学習

## 6. コードレビューAI
変更案を別AI視点でレビュー。
危険箇所、不足テスト、破壊的変更を指摘。

## 10. 相手の口調から学習
親密度ではなく、話し方・会話内容から調整。

## 11. 学習強度設定
例:
- 口調: 高
- 価値観: 低
- 好み: 中

## 12. キャラクター成長
経験 → 記憶 → 性格変化

## 13. Piper移行
VOICEVOX中心から Piper 対応へ拡張。

## 14. 独自音声学習
Piper / Kokoro / Style-Bert-VITS2 を比較検討。

## 15. Developer Chat強化
- 専用アイコン
- 固定最上段
- 開発状態表示

## 16. 開発ダッシュボード
- 現在バージョン
- Git状態
- LLM backend
- 変更履歴
- 未反映改善案

## 17. AI同士会話学習
OpenAI / Claude / ローカルAIで会話。

## 18. 自己人格形成
会話分析 → 人格変化。

## 19. 完全ローカル統合AI
会話・記憶・人格・音声・ファイル編集・自己改善を統合。
