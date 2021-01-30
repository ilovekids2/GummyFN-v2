"""
MIT License
Copyright (c) 2020 gomashio1596
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import traceback
import requests
import time
import json
import sys
import os


def AddNewKey(data: dict, new: dict) -> dict:
    result = data.copy()
    for key,value in new.items():
        if type(value) ==  dict:
            result[key] = AddNewKey(result.get(key, {}), value)
        result.setdefault(key, value)
    return result

def CheckUpdate(filename: str, githuburl: str, overwrite: bool = False) -> bool:
    print(f'Checking update for {filename}...')
    try:
        if "/" in filename:
            os.makedirs("/".join(filename.split("/")[:-1]), exist_ok=True)
        for count, text in enumerate(filename[::-1]):
            if text == ".":
                filename_ = filename[:len(filename)-count-1]
                extension = filename[-count-1:]
                break
        else:
            filename_ = filename
            extension = ""
        if extension in [".py", ".bat", ".txt", ".md", ".html", ".toml", ""]:
            if os.path.isfile(filename):
                with open(filename, "r", encoding='utf-8') as f:
                    current = f.read()
            else:
                github = requests.get(githuburl + filename)
                if github.status_code != 200:
                    print(f'Failed to get data for {filename}\n')
                    return None
                github.encoding = github.apparent_encoding
                github = github.text.encode(encoding='utf-8')
                with open(filename, "wb") as f:
                    f.write(github)
                with open(filename, "r", encoding='utf-8') as f:
                    current = f.read()
            github = requests.get(githuburl + filename)
            if github.status_code != 200:
                print(f'Failed to get data for {filename}\n')
                return None
            github.encoding = github.apparent_encoding
            github = github.text.encode(encoding='utf-8')
            if current.replace('\n','').replace('\r','').encode(encoding='utf-8') != github.decode().replace('\n','').replace('\r','').encode(encoding='utf-8'):
                print(f'Update found for {filename}!')
                print(f'Backuping {filename}...\n')
                if os.path.isfile(f'{filename_}_old{extension}'):
                    try:
                        os.remove(f'{filename_}_old{extension}')
                    except PermissionError:
                        print(f'Failed to remove file {filename}\n')
                        print(traceback.format_exc())
                try:
                    os.rename(filename, f'{filename_}_old{extension}')
                except PermissionError:
                    (f'Failed to backup file {filename}\n')
                    print(traceback.format_exc())
                else:
                    with open(filename, "wb") as f:
                        f.write(github)
                    (f'Update for {filename} done!\n')
                    return True
            else:
                print(f'No update for {filename}!\n')
                return False
        elif extension == ".json":
            if os.path.isfile(filename):
                with open(filename, "r", encoding='utf-8') as f:
                    current = json.load(f)
            else:
                github = requests.get(githuburl + filename)
                if github.status_code != 200:
                    print(f'Failed to get data for {filename}\n')
                    return None
                github.encoding = github.apparent_encoding
                github = github.text.encode(encoding='utf-8')
                with open(filename, "wb") as f:
                    f.write(github)
                try:
                    with open(filename, "r", encoding='utf-8') as f:
                        current = json.load(f)
                except json.decoder.JSONDecodeError:
                    with open(filename, "r", encoding='utf-8-sig') as f:
                        current = json.load(f)
            github = requests.get(githuburl + filename)
            if github.status_code != 200:
                print(f'Failed to get data for {filename}\n')
                return None
            github.encoding = github.apparent_encoding
            github = github.text
            github = json.loads(github)

            if overwrite:
                if current != github:
                    print(f'Update found for {filename}!')
                    print(f'Backuping {filename}...\n')
                    if os.path.isfile(f'{filename_}_old{extension}'):
                        try:
                            os.remove(f'{filename_}_old{extension}')
                        except PermissionError:
                            print(f'Failed to remove file {filename}\n')
                            print(traceback.format_exc())
                    try:
                        os.rename(filename, f'{filename_}_old{extension}')
                    except PermissionError:
                        print(f'{filename} ファイルをバックアップできませんでした')
                        print(f'Failed to backup file {filename}\n')
                        print(traceback.format_exc())
                    else:
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(github, f, indent=4, ensure_ascii=False)
                        print(f'{filename} の更新が完了しました!')
                        print(f'Update for {filename} done!\n')
                        return True
                else:
                    print(f'{filename} の更新はありません!')
                    print(f'No update for {filename}!\n')
                    return False
            else:
                new = AddNewKey(current, github)
                if current != new:
                    print(f'{filename} の更新を確認しました!')
                    print(f'{filename} をバックアップ中...')
                    print(f'Update found for {filename}!')
                    print(f'Backuping {filename}...\n')
                    try:
                        if os.path.isfile(f'{filename_}_old{extension}'):
                            try:
                                os.remove(f'{filename_}_old{extension}')
                            except PermissionError:
                                print(f'{filename_}_old{extension} ファイルを削除できませんでした')
                                print(f'Failed to remove file {filename_}_old{extension}')
                                print(f'{traceback.format_exc()}\n')
                        os.rename(filename, f'{filename_}_old{extension}')
                    except PermissionError:
                        print(f'{filename} ファイルをバックアップできませんでした')
                        print(f'Failed to backup file {filename}')
                        print(f'{traceback.format_exc()}\n')
                        return None
                    else:
                        with open(filename, 'w', encoding="utf-8") as f:
                            json.dump(new, f, indent=4, ensure_ascii=False)
                        print(f'{filename} の更新が完了しました!')
                        print(f'Update for {filename} done!\n')
                        return True
                else:
                    print(f'{filename} の更新はありません!')
                    print(f'No update for {filename}!\n')
                    return False
        elif extension == ".png":
            if os.path.isfile(filename):
                with open(filename, "rb") as f:
                    current = f.read()
            else:
                github = requests.get(githuburl + filename)
                if github.status_code != 200:
                    print(f'{filename} のデータを取得できませんでした')
                    print(f'Failed to get data for {filename}\n')
                    return None
                github = github.content
                with open(filename, "wb") as f:
                    f.write(github)
                with open(filename, "rb") as f:
                    current = f.read()
            github = requests.get(githuburl + filename)
            if github.status_code != 200:
                print(f'{filename} のデータを取得できませんでした')
                print(f'Failed to get data for {filename}\n')
                return None
            github = github.content
            if current != github:
                print(f'{filename} の更新を確認しました!')
                print(f'{filename} をバックアップ中...')
                print(f'Update found for {filename}!')
                print(f'Backuping {filename}...\n')
                if os.path.isfile(f'{filename_}_old{extension}'):
                    try:
                        os.remove(f'{filename_}_old{extension}')
                    except PermissionError:
                        print(f'{filename} ファイルを削除できませんでした')
                        print(f'Failed to remove file {filename}\n')
                        print(traceback.format_exc())
                try:
                    os.rename(filename, f'{filename_}_old{extension}')
                except PermissionError:
                    print(f'{filename} ファイルをバックアップできませんでした')
                    print(f'Failed to backup file {filename}\n')
                    print(traceback.format_exc())
                else:
                    with open(filename, "wb") as f:
                        f.write(github)
                    print(f'{filename} の更新が完了しました!')
                    print(f'Update for {filename} done!\n')
                    return True
            else:
                print(f'{filename} の更新はありません!')
                print(f'No update for {filename}!\n')
                return False
        else:
            print(f'拡張子 {extension} は対応していません')
            print(f'Extension {extension} not supported\n')
            return None
    except Exception:
        print("更新に失敗しました")
        print("Update failed")
        print(f'{traceback.format_exc()}\n')
        return None

if "-dev" in sys.argv:
    githuburl = "https://raw.githubusercontent.com/ilovekids2/GummyFN-v2/Dev/"
else:
    githuburl = "https://raw.githubusercontent.com/ilovekids2/GummyFN-v2/master/"

if CheckUpdate("auto.py", githuburl):
    print("auto-updater.py got updated. Run updater again...\n")
    os.chdir(os.getcwd())
    os.execv(os.sys.executable,['python', *sys.argv])

flag = False
CheckUpdate("main.py", githuburl)
if CheckUpdate("requirements.txt", githuburl):
    print("requirements.txt got updated. Run INSTALL\n")
    flag = True

CheckUpdate("Settings.json", githuburl)
CheckUpdate(".replit", githuburl)
if not os.getcwd().startswith('/app') and not os.getcwd().startswith('/home/runner'):
    CheckUpdate("poetry.lock", githuburl)
    CheckUpdate("Settings.json", githuburl)
    CheckUpdate(".replit", githuburl)
else:
    CheckUpdate("pyproject.toml", githuburl)

if CheckUpdate("README.md", githuburl):
    print("README.md was update")

print("All update finished")
if flag:
    os.chdir(os.getcwd())
    os.execv(os.sys.executable,['python3', "-m", "pip", "install", "--user", "-U", "-r", "requirements.txt"])
    sys.exit(0)
