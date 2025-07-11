#!/usr/bin/env python3
"""
Terminal Simple Browser
curlコマンドを使った簡易ブラウザ

使用方法:
python simple_browser.py [URL]
またはスクリプト実行後にURLを入力
"""

import subprocess
import sys
import re
import urllib.parse
from typing import Optional, List, Tuple

class SimpleBrowser:
    def __init__(self):
        self.current_url = ""
        self.history = []
        self.history_index = -1
        
    def fetch_page(self, url: str) -> Optional[str]:
        """curlコマンドを使ってWebページを取得"""
        try:
            # URLの正規化
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # curlコマンドを実行
            cmd = [
                'curl', '-s', '-L',  # -s: silent, -L: follow redirects
                '-H', 'User-Agent: Simple-Terminal-Browser/1.0',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                '--max-time', '30',  # 30秒でタイムアウト
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.current_url = url
                self.add_to_history(url)
                return result.stdout
            else:
                print(f"エラー: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"ページの取得に失敗しました: {e}")
            return None
    
    def add_to_history(self, url: str):
        """履歴に追加"""
        if self.history_index < len(self.history) - 1:
            # 履歴の途中から新しいページに移動した場合、それ以降の履歴を削除
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(url)
        self.history_index = len(self.history) - 1
    
    def go_back(self) -> Optional[str]:
        """戻る"""
        if self.history_index > 0:
            self.history_index -= 1
            url = self.history[self.history_index]
            return self.fetch_page(url)
        return None
    
    def go_forward(self) -> Optional[str]:
        """進む"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            url = self.history[self.history_index]
            return self.fetch_page(url)
        return None
    
    def parse_html(self, html: str) -> str:
        """HTMLを解析して読みやすいテキストに変換"""
        if not html:
            return ""
        
        # HTMLタグを除去（簡易版）
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        
        # HTMLエンティティをデコード
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        
        # 複数の空白や改行を整理
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def extract_links(self, html: str) -> List[Tuple[str, str]]:
        """HTMLからリンクを抽出"""
        links = []
        # aタグのhref属性を抽出
        pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        
        for href, text in matches:
            # 相対URLを絶対URLに変換
            if href.startswith('/'):
                base_url = urllib.parse.urlparse(self.current_url)
                href = f"{base_url.scheme}://{base_url.netloc}{href}"
            elif not href.startswith(('http://', 'https://')):
                href = urllib.parse.urljoin(self.current_url, href)
            
            # リンクテキストからHTMLタグを除去
            link_text = re.sub(r'<[^>]+>', '', text).strip()
            if link_text:
                links.append((href, link_text))
        
        return links
    
    def display_page(self, html: str):
        """ページ内容を表示"""
        print("=" * 80)
        print(f"URL: {self.current_url}")
        print("=" * 80)
        
        # テキスト内容を表示
        text_content = self.parse_html(html)
        if text_content:
            # 長すぎる場合は先頭部分のみ表示
            lines = text_content.split('\n')
            if len(lines) > 100:
                lines = lines[:100]
                print('\n'.join(lines))
                print(f"\n... ({len(text_content.split())} 行の内容があります)")
            else:
                print(text_content)
        
        print("\n" + "-" * 80)
        
        # リンクを表示
        links = self.extract_links(html)
        if links:
            print("リンク:")
            for i, (url, text) in enumerate(links[:20]):  # 最大20個まで表示
                print(f"  {i+1:2d}. {text[:60]}... -> {url}")
            if len(links) > 20:
                print(f"  ... 他{len(links)-20}個のリンク")
        
        print("-" * 80)
    
    def run(self, initial_url: str = ""):
        """ブラウザを実行"""
        print("🌐 Simple Terminal Browser")
        print("コマンド: [URL], back, forward, links, history, quit")
        print("=" * 80)
        
        if initial_url:
            html = self.fetch_page(initial_url)
            if html:
                self.display_page(html)
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("ブラウザを終了します。")
                    break
                
                elif command.lower() == 'back':
                    html = self.go_back()
                    if html:
                        self.display_page(html)
                    else:
                        print("戻るページがありません。")
                
                elif command.lower() == 'forward':
                    html = self.go_forward()
                    if html:
                        self.display_page(html)
                    else:
                        print("進むページがありません。")
                
                elif command.lower() == 'history':
                    print("履歴:")
                    for i, url in enumerate(self.history):
                        marker = " -> " if i == self.history_index else "    "
                        print(f"{marker}{i+1}. {url}")
                
                elif command.lower() == 'links':
                    if self.current_url:
                        html = self.fetch_page(self.current_url)
                        if html:
                            links = self.extract_links(html)
                            if links:
                                print("利用可能なリンク:")
                                for i, (url, text) in enumerate(links):
                                    print(f"  {i+1:2d}. {text} -> {url}")
                            else:
                                print("リンクが見つかりませんでした。")
                    else:
                        print("まずページを開いてください。")
                
                elif command.isdigit():
                    # 数字の場合はリンク番号として処理
                    if self.current_url:
                        html_content = self.fetch_page(self.current_url)
                        if html_content:
                            links = self.extract_links(html_content)
                            link_num = int(command) - 1
                            if 0 <= link_num < len(links):
                                url = links[link_num][0]
                                html = self.fetch_page(url)
                                if html:
                                    self.display_page(html)
                            else:
                                print("無効なリンク番号です。")
                    else:
                        print("まずページを開いてください。")
                
                else:
                    # URLとして処理
                    html = self.fetch_page(command)
                    if html:
                        self.display_page(html)
                
            except KeyboardInterrupt:
                print("\n\nブラウザを終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")

def main():
    browser = SimpleBrowser()
    
    # コマンドライン引数でURLが指定された場合
    initial_url = sys.argv[1] if len(sys.argv) > 1 else ""
    
    browser.run(initial_url)

if __name__ == "__main__":
    main()
