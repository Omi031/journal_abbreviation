#!/usr/bin/env python3
import sys
import os


def get_resource_path(relative_path):
    """PyInstallerパッケージ化対応のリソースパス取得"""
    if getattr(sys, "frozen", False):
        # EXEファイル実行時 - PyInstallerの一時ディレクトリから取得
        base_path = sys._MEIPASS
    else:
        # 通常のPython実行時 - スクリプトファイルからの相対パス
        base_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    return os.path.join(base_path, relative_path)


print("=== PyInstaller リソーステスト ===")
print(f"sys.frozen = {getattr(sys, 'frozen', False)}")

if getattr(sys, "frozen", False):
    print(f"sys._MEIPASS = {sys._MEIPASS}")
    print(f"_MEIPASSの内容:")
    try:
        for item in os.listdir(sys._MEIPASS):
            print(f"  - {item}")
            if item == "data":
                data_path = os.path.join(sys._MEIPASS, "data")
                print(f"    dataフォルダの内容:")
                for file in os.listdir(data_path):
                    print(f"      - {file}")
    except Exception as e:
        print(f"  エラー: {e}")

settings_path = get_resource_path("data/settings.yml")
print(f"settings_path = {settings_path}")
print(f"settings.yml exists = {os.path.exists(settings_path)}")

if os.path.exists(settings_path):
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            content = f.read()
        print("settings.yml読み込み成功!")
        print(f"内容の一部: {content[:100]}...")
    except Exception as e:
        print(f"settings.yml読み込みエラー: {e}")
else:
    print("settings.ymlが見つかりません")

print("\n何かキーを押して終了してください...")
input()
