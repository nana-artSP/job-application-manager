<img width="1912" height="906" alt="image" src="https://github.com/user-attachments/assets/487b97c1-8566-4f1a-8bf2-555ff86d8914" /># 求人応募管理アプリ

転職活動中の応募企業、選考状況、面接予定、メモを管理するDjangoアプリです。

## 作成背景

未経験からエンジニア転職を目指す中で、応募企業・選考状況・面接予定・振り返りメモを一元管理したいと考えて作成しました。

## 主な機能

- ユーザー登録、ログイン、ログアウト
- 応募企業の登録、編集、削除
- 応募ステータス、選考結果の管理
- 選考中、面接予定、落ちた・辞退、合格のタブ絞り込み
- 面接予定の登録
- 直近面接のダッシュボード表示
- Googleカレンダー、Outlook、Appleカレンダー向けの予定追加
- 通常メモ、企業メモ、面接メモ、反省メモの分割管理
- URLから取得できる範囲で会社情報を自動入力

## 使用技術

- Python
- Django
- SQLite
- Bootstrap

## 工夫した点・学習したこと

本アプリではAIツール（Codex）も活用しながら開発を進めました。

ただし生成されたコードをそのまま利用するのではなく、Djangoの Model / Form / View / Template の役割やデータの流れを確認しながら、自分でコードを読み、修正・機能追加・エラー対応を行っています。

特に以下の点を意識して学習・改善を行いました。

- URLから企業情報を取得する処理の理解
- Django標準認証機能を用いたログイン実装
- ユーザーごとのデータ管理
- CRUD処理とフォーム連携
- エラー発生時の原因調査と修正

## 画面イメージ

### ログイン画面
<img width="1912" height="906" alt="image" src="https://github.com/user-attachments/assets/0c0b98f9-fbd7-4d39-9d3b-7c39df1e285b" />

### 管理画面一覧
<img width="1908" height="903" alt="image" src="https://github.com/user-attachments/assets/89f79227-63d3-45a1-a88a-9d1c617a73b2" />

### 新規登録画面
<img width="1894" height="903" alt="image" src="https://github.com/user-attachments/assets/248c02ed-adf6-4d08-bb31-c3790ba51fda" />

## セットアップ

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

ブラウザで以下を開きます。

```text
http://127.0.0.1:8000/
```

初回利用時は「ユーザー登録」からアカウントを作成してください。

## 環境変数

ローカル開発ではそのまま動きます。必要に応じて以下を設定できます。

```bash
DJANGO_SECRET_KEY=任意のシークレットキー
```

## 注意

このリポジトリにはローカルDBファイルは含めていません。利用時は `python manage.py migrate` でDBを作成してください。
