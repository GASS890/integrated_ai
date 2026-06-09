\# integrated\_ai Development Archive



\## 目的



ローカル環境で使用できる統合AIを作成する。

会話、記憶、人格、音声、ファイル操作、開発補助、外部API連携を段階的に実装する。



\## 現在の重要方針



\- ChatGPT APIはDeveloper Agent用途で使用する

\- Ollamaは通常会話・ローカル実行用に残す

\- OpenAI / Ollama / Claude / Gemini を将来切り替え可能にする

\- main.pyを肥大化させず、機能ごとに分離する

\- 変更は1か所ずつ行い、py\_compile確認後に次へ進む



\## 完了済み



\### v0.19



LLM backend分離を進めた。



\- llm/router.py に呼び出し集約

\- llm\_client.py を薄くした

\- main.py の call\_ollama\_chat / stream\_ollama\_chat 依存を削減

\- Developer Agent用の基礎構成を追加



## 実装中

### v0.20.1

Developer Agentの文脈強化を進める。

予定：

- git status取得
- git diff取得
- development_archive.md共有
- ChatGPT APIへ開発状況を送信

### v0.20.2

Developer Agent自動適用機能。

予定：

- safe_apply.py作成
- 変更前バックアップ
- 自動コード適用

### v0.20.3

開発補助自動化。

予定：

- py_compile一括確認
- GitHub push前チェック
- 開発レビュー自動実行



\### Developer Agent



目的：

ローカルAIがChatGPT APIに相談しながらコード変更案を生成する。



構成：



\- dev\_assistant/openai\_advisor.py

\- dev\_assistant/project\_reader.py

\- dev\_assistant/developer\_agent.py

\- dev\_assistant/dev\_mode.py

\- dev\_assistant/git\_tools.py 予定

\- app\_settings.py



現在できること：



\- ローカルAIのチャット欄からDeveloper Agentを呼び出せる

\- ⚙設定画面でDeveloper AgentのON/OFFを切り替える

\- ChatGPT APIに関連ファイルを送って変更案を取得する



\## 採用方針



\- 変更前コードは実ファイルから引用する

\- 存在しないファイルや関数を前提にしない

\- 変更は1か所ずつ提示する

\- py\_compile確認を必須にする

\- エラーを握りつぶす修正は原則避ける

\- APIキーはコードに直書きしない

\- API clientは可能なら遅延初期化する



\## 不採用にした方針



\- OpenAI API例外時に単純に return "" する

\- 実ファイルを見ずに一般論で修正案を出す

\- PowerShell上だけに結果を出してチャット欄に残さない

\- Developer Agentを常時ONにする



\## 今後の優先順位



1\. Developer Agentにgit status / git diffを渡す

2\. development\_archive.mdをAPI文脈に含める

3\. OpenAI backendのclient遅延初期化

4\. OpenAI / Ollama / Claude / Gemini切替構成

5\. safe\_apply.pyで変更前バックアップと自動適用

6\. py\_compile一括確認

7\. GitHub push前チェック


```markdown
### v0.20

Developer Agentのチャット欄からの呼び出し機能を実装し、設定画面にON/OFF切り替えを追加した。

- ローカルAIのチャット画面からDeveloper Agentを起動可能にした。
- 設定画面にDeveloper Agentの有効/無効を切り替えるトグルを追加。
- ChatGPT APIを利用して関連ファイルを送信し、コード変更案を取得する仕組みを整備。

#### 不採用にした方針

- Developer Agentを常時ONにする設定は採用しなかった。ユーザーが明示的にON/OFFを切り替えられる形を維持。

```
## 開発判断履歴

### 採用

* Developer AgentはChatGPT APIを利用する
* 通常会話はOllamaを利用する
* 開発履歴はdevelopment_archive.mdへ保存する
* アーカイブ更新は提案→承認→保存方式とする
* 変更は1か所ずつ行う

### 不採用

* アーカイブ完全自動更新
* Developer Agent常時ON
* エラーを握りつぶす修正
* 実ファイルを見ない修正提案
