@echo off
echo Journal Abbreviation Formatter のEXEファイルを作成中...
echo.

REM 古いビルドファイルを削除
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "JournalAbbreviationFormatter.exe" del "JournalAbbreviationFormatter.exe"

echo 前回のビルドファイルをクリアしました。
echo.

REM PyInstallerでEXEファイルを作成
pyinstaller JournalAbbreviationFormatter.spec

REM 成功した場合、EXEファイルを現在のディレクトリにコピー
if exist "dist\JournalAbbreviationFormatter.exe" (
    copy "dist\JournalAbbreviationFormatter.exe" "JournalAbbreviationFormatter.exe"
    echo.
    echo ========================================
    echo EXEファイルの作成が完了しました！
    echo ファイル: JournalAbbreviationFormatter.exe
    echo ========================================
    echo.
) else (
    echo.
    echo エラー: EXEファイルの作成に失敗しました。
    echo.
)

pause