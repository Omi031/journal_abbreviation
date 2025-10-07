# Journal Abbreviation Formatter (HTML版)

学術文献の引用フォーマットを自動的に整形するWebアプリケーションです。RIS形式の文献データを入力として、適切にフォーマットされた引用文を生成します。

## 特徴

- **RIS形式対応**: 標準的なRIS形式の文献データを解析・処理
- **多様な設定**: フォーマット形式、著者表示、会議論文の処理方法をカスタマイズ可能
- **CSV辞書管理**: 雑誌略語、削除語、月略語、固有名詞の辞書をCSVファイルで管理
- **タイトルケース変換**: 固有名詞を保持しながら適切な大文字小文字に変換
- **レスポンシブデザイン**: デスクトップ・タブレット・スマートフォンに対応
- **設定の保存**: ブラウザのローカルストレージに設定を自動保存

## ファイル構成

```
journal-abbreviation-html/
├── index.html              # メインページ
├── css/
│   └── style.css          # スタイルシート
├── js/
│   ├── app.js             # メインアプリケーション
│   ├── formatter.js       # 文献フォーマット処理
│   ├── settings.js        # 設定管理
│   └── csv-parser.js      # CSV解析ユーティリティ
├── data/
│   ├── settings.json      # デフォルト設定
│   ├── jo_abb.csv        # 雑誌略語辞書
│   ├── jo_del.csv        # 削除語リスト
│   ├── mo_abb.csv        # 月略語辞書
│   └── proper_nouns.csv   # 固有名詞辞書
└── README.md              # このファイル
```

## 使用方法

### 1. 起動方法

1. `index.html` をWebブラウザで開く
2. ローカルサーバー経由でアクセス（CORS制約回避のため推奨）:
   ```bash
   # Python 3の場合
   python -m http.server 8000
   
   # Node.js (npx)の場合
   npx http-server
   
   # PHP（インストール済みの場合）
   php -S localhost:8000
   ```
3. ブラウザで `http://localhost:8000` にアクセス

### 2. 基本的な使用手順

1. **設定の確認**: 左側パネルで出力フォーマット（TeX/Plain）などを設定
2. **RISデータの入力**: 右側の入力エリアにRIS形式の文献データを貼り付け
3. **フォーマット実行**: "フォーマット実行"ボタンをクリック
4. **結果の確認**: 出力エリアに整形された引用文が表示されます
5. **コピー**: "コピー"ボタンで結果をクリップボードにコピー

### 3. RIS形式の例

```
TY  - JOUR
AU  - Smith, J.
AU  - Johnson, A.
TI  - A Study on Machine Learning Applications
JO  - IEEE Transactions on Neural Networks and Learning Systems
VL  - 30
IS  - 5
SP  - 1234
EP  - 1245
Y1  - 2023/05/
DO  - 10.1109/example.2023.1234567
ER  -
```

### 4. 設定オプション

#### 基本設定
- **出力フォーマット**: TeX形式またはプレーンテキスト
- **Et al.閾値**: 著者数がこの値以上の場合に"et al."を使用
- **タイトルケース変換**: タイトルの大文字小文字を適切に調整

#### 会議論文設定
- **"Proc."を付加**: 会議論文タイトルに"Proc."を自動追加
- **"in"を付加**: 会議論文に"in"を自動追加  
- **年を含める**: 会議名に年を含める

#### 固有名詞処理
- **固有名詞の自動判定**: アルゴリズムによる固有名詞の自動検出
- **固有名詞辞書**: CSVファイルによる固有名詞の管理

### 5. CSV辞書のカスタマイズ

#### 雑誌略語 (jo_abb.csv)
```csv
original,abbreviation
Transactions,Trans
Applications,Appl
Conference,Conf
```

#### 削除語 (jo_del.csv)
```csv
original
and
in
of
on
```

#### 月略語 (mo_abb.csv)
```csv
original,abbreviation
January,Jan
February,Feb
March,Mar
```

#### 固有名詞 (proper_nouns.csv)
```csv
original
WiFi
IoT
AI
5G
```

### 6. キーボードショートカット

- **Ctrl + Enter**: フォーマット実行
- **Ctrl + K**: 入力・出力をクリア
- **Ctrl + Shift + C**: 結果をクリップボードにコピー

## 対応ブラウザ

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 機能詳細

### サポートしている文献タイプ

- **JOUR**: 学術雑誌論文
- **CONF**: 会議論文

### 出力例

**TeX形式**:
```
J. Smith and A. Johnson, ``A Study on Machine Learning Applications,'' \textit{IEEE Trans. Neural Networks Learn. Syst.}, vol. 30, no. 5, pp. 1234--1245, May 2023.
```

**プレーンテキスト形式**:
```
J. Smith and A. Johnson, "A Study on Machine Learning Applications," IEEE Trans. Neural Networks Learn. Syst., vol. 30, no. 5, pp. 1234-1245, May 2023.
```

## トラブルシューティング

### よくある問題

1. **CSVファイルが読み込まれない**
   - ブラウザのCORS制約により、ファイルプロトコル（file://）では動作しません
   - ローカルサーバーを使用してください

2. **文献がフォーマットされない**
   - RIS形式が正しいか確認してください
   - 必須フィールド（TY、ER）が含まれているか確認してください

3. **固有名詞が正しく処理されない**
   - 固有名詞辞書（proper_nouns.csv）に追加してください
   - 自動判定機能を有効にしてください

### デバッグ

ブラウザの開発者ツール（F12）のコンソールでエラーメッセージを確認できます。

## ライセンス

このプロジェクトは元のPythonアプリケーションと同じライセンスに従います。

## 元プロジェクトとの比較

| 機能 | Python版 | HTML版 |
|------|----------|--------|
| RIS解析 | ✓ | ✓ |
| TeX/Plain出力 | ✓ | ✓ |
| CSV辞書 | ✓ | ✓ |
| 設定保存 | ファイル | ブラウザ |
| GUI | PyQt5 | Web |
| 実行環境 | Python | ブラウザ |
| 配布 | 実行ファイル | Webページ |

## 今後の拡張予定

- [ ] BibTeX形式の対応
- [ ] 書籍・特許の対応
- [ ] カスタムフォーマットテンプレート
- [ ] バッチ処理機能
- [ ] 多言語対応