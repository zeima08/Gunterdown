Gunterdown — ターミナル用 Markdown エディター

表示言語：ツール > 表示言語（Alt+U）。選択は保存されます。
補完言語：Alt+L、または --lang en/ja/zh/ko/fr。
表示言語と補完言語は別々に選択できます。
起動時の表示言語：--ui-lang ja（en / zh / ko / fr も使用可能）。

入力中に候補が表示されます。英字は3文字、日本語・韓国語は2文字、
中国語は1文字から補完します。
↑/↓ または Shift+Tab で選択し、Tab で確定、Esc で閉じます。
Enter は改行です。Ctrl+Space で候補を手動表示します。
別の言語の候補には言語コードが表示されます。
日本語・中国語は、空白のない文章の途中でも補完できます。
かな・漢字・ハングルの入力には OS の IME を使用してください。
ローマ字・拼音からの変換機能は内蔵していません。

Ctrl+S：保存、Ctrl+X：終了、F2：メニュー、F9：ツリー表示。
Shift+←/→：選択、Ctrl+U：元に戻す、Ctrl+Y：やり直す。
Alt+B：文書切り替え。候補がなければ Tab でツリーと編集を切り替えます。
未保存の文書には * が付き、閉じる際に確認します。
復元用コピーは30秒ごとに GUNTERDOWN_HOME/recover/ に保存します。
補完処理はすべてオフラインです。英語・フランス語の修正は単語候補で、
文法チェックではありません。CJK は入力済み文字の接頭辞で補完します。

ショートカット一覧（Esc で編集に戻る）：

ファイル
  Ctrl+N       新規
  Ctrl+O       開く…
  Ctrl+R       最近のファイル
  Ctrl+S       保存
  Alt+E        名前を付けて保存…
  —            すべて保存
  Alt+X        閉じる
  —            インポート
  Ctrl+E       エクスポート
  Ctrl+P       印刷
  Ctrl+X       終了
編集
  Ctrl+U       元に戻す
  Ctrl+Y       やり直す
  Ctrl+K       切り取り
  Ctrl+C       コピー
  Ctrl+V       貼り付け
  Ctrl+A       すべて選択
  —            インデント
  —            インデントを解除
  Alt+/        コメント切り替え
  F5           日付を挿入
  Ctrl+L       リンクを挿入
  Alt+I        画像を挿入
検索
  Ctrl+W       検索
  Ctrl+D       次へ
  Ctrl+B       前へ
  Ctrl+\       置換
  Ctrl+G       行へ移動
  F3           見出しへ移動
  —            ファイル内を検索
記事
  Alt+T        テンプレート
  Alt+F        メタデータ
  Alt+S        目次
  Alt+N        見出し番号を更新
  Alt+2        見出し H2
  Alt+3        見出し H3
  Alt+C        コード
  Alt+Q        引用
  Alt+M        表
  Alt+P        画像の説明
  Alt+V        Markdown を確認
ツール
  F6           HTML プレビュー
  F7           統計
  F8           スペルチェック
  Alt+L        補完言語
  Alt+U        表示言語
  Alt+D        自動補完
  Alt+Z        集中モード
  Alt+W        折り返し
  Alt+#        行番号
  F9           ファイルツリー
  —            フォルダーを変更
  —            設定
ヘルプ
  F1           マニュアル
  Alt+H        ショートカット
  F12          このアプリについて
  —            診断

テーマ：Alt+Y または ツール > テーマ。↑/↓ でプレビュー、Enter で保存、Esc でキャンセル。
配色：dark, light, solarized, nord, dracula, ocean, contrast。
起動時は --theme nord。独自テーマ：GUNTERDOWN_HOME/themes/*.json。
