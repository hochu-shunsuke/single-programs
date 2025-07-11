# Terminal Simple Browser

ターミナル上で動作する文字ベースの簡易ブラウザです。curlコマンドを使用してWebページを取得し、HTMLを解析して読みやすいテキスト形式で表示します。

## 特徴

- 🌐 curlコマンドベースのWebページ取得
- 📄 HTMLからテキストを抽出して表示
- 🔗 リンクの抽出と番号選択
- 📚 履歴機能（戻る/進む）
- 🔖 ブックマーク機能（enhanced版のみ）
- 🔍 Google検索機能（enhanced版のみ）
- 📱 完全にターミナル上で動作

## ファイル構成

- `simple_browser.py` - 基本版（外部依存なし、curlのみ使用）
- `enhanced_browser.py` - 高機能版（BeautifulSoup4 + requests使用）
- `requirements.txt` - 高機能版の依存関係

## インストール

### 基本版（simple_browser.py）

```bash
# curlがインストールされていることを確認
curl --version

# 実行権限を付与
chmod +x simple_browser.py
```

### 高機能版（enhanced_browser.py）

```bash
# Python依存関係をインストール
pip install -r requirements.txt

# または個別にインストール
pip install beautifulsoup4 requests

# 実行権限を付与
chmod +x enhanced_browser.py
```

## 使用方法

### 基本版

```bash
# URLを指定して起動
python simple_browser.py https://example.com

# または起動後にURLを入力
python simple_browser.py
```

### 高機能版

```bash
# URLを指定して起動
python enhanced_browser.py https://news.ycombinator.com

# または起動後にURLを入力
python enhanced_browser.py
```

## コマンド

ブラウザ起動後に使用できるコマンド：

- `[URL]` - 指定したURLのページを開く
- `[数字]` - 表示されたリンクの番号を入力してそのリンクを開く
- `back` - 前のページに戻る
- `forward` - 次のページに進む
- `history` - 閲覧履歴を表示
- `bookmark` - 現在のページをブックマークに追加（enhanced版のみ）
- `bookmarks` - ブックマーク一覧を表示（enhanced版のみ）
- `search [クエリ]` - Google検索を実行（enhanced版のみ）
- `help` - ヘルプを表示
- `quit` / `exit` / `q` - ブラウザを終了

## 使用例

```bash
$ python enhanced_browser.py

🌐 Enhanced Terminal Browser
✅ BeautifulSoup4, requests が利用可能です

コマンド:
  [URL]           - URLを開く
  [数字]          - リンク番号を開く
  back            - 戻る
  forward         - 進む
  history         - 履歴表示
  bookmark        - ブックマークに追加
  bookmarks       - ブックマーク一覧
  search [クエリ]  - Google検索
  help            - ヘルプ表示
  quit            - 終了
================================================================================

🌐 > https://news.ycombinator.com
🌐 ページを読み込み中: https://news.ycombinator.com
================================================================================
📄 Hacker News
🌐 https://news.ycombinator.com
================================================================================
Hacker News

新着   |   過去   |   コメント   |   質問   |   求人   |   投稿

...（ページ内容が表示される）...

--------------------------------------------------------------------------------
🔗 リンク:
   1. 記事タイトル1...
      -> https://example.com/article1
   2. 記事タイトル2...
      -> https://example.com/article2
...
--------------------------------------------------------------------------------

🌐 > 1
🔗 リンクを開いています: https://example.com/article1
...

🌐 > search Python tutorial
🔍 Google検索: Python tutorial
...

🌐 > quit
ブラウザを終了します。
```

## 技術的な特徴

### 基本版の特徴

- 外部Pythonライブラリに依存しない
- curlコマンドを subprocess で実行
- 正規表現によるHTML解析
- シンプルで軽量

### 高機能版の特徴

- BeautifulSoup4による高精度なHTML解析
- requestsライブラリによる高機能なHTTP通信
- メタ情報の抽出（title、description等）
- より読みやすい表示形式
- エラーハンドリングの改善

## 対応機能

- ✅ HTTP/HTTPS サポート
- ✅ リダイレクト対応
- ✅ HTMLからテキスト抽出
- ✅ リンク抽出と番号選択
- ✅ 履歴機能
- ✅ 相対URL → 絶対URL変換
- ✅ タイムアウト設定
- ✅ ユーザーエージェント設定

## 制限事項

- JavaScript は実行されません
- CSS スタイルは適用されません
- 画像や動画は表示されません
- フォームの送信はサポートされていません
- Cookieやセッション管理は基本的ではありません

## 動作環境

- Python 3.6+
- curl コマンド（システムにインストール済み）
- macOS、Linux、Windows（WSL）

## ライセンス

MIT License
