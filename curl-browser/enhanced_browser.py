#!/usr/bin/env python3
"""
Enhanced Terminal Browser with BeautifulSoup
より高機能な簡易ブラウザ（BeautifulSoup使用版）

必要なパッケージ:
pip install beautifulsoup4 requests

使用方法:
python enhanced_browser.py [URL]
"""

import subprocess
import sys
import os
import urllib.parse
from typing import Optional, List, Tuple, Dict

try:
    from bs4 import BeautifulSoup
    import requests
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("注意: beautifulsoup4とrequestsがインストールされていません。")
    print("基本機能のみで動作します。")
    print("pip install beautifulsoup4 requests でインストールできます。")

class EnhancedBrowser:
    def __init__(self):
        self.current_url = ""
        self.history = []
        self.history_index = -1
        self.bookmarks = []
        self.session = requests.Session() if ENHANCED_MODE else None
        
        if self.session:
            self.session.headers.update({
                'User-Agent': 'Enhanced-Terminal-Browser/1.0 (curl-based)'
            })
    
    def fetch_page_curl(self, url: str) -> Optional[str]:
        """curlコマンドを使ってWebページを取得（フォールバック）"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            cmd = [
                'curl', '-s', '-L',
                '-H', 'User-Agent: Enhanced-Terminal-Browser/1.0',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                '--max-time', '30',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"curl エラー: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"ページの取得に失敗しました: {e}")
            return None
    
    def fetch_page_requests(self, url: str) -> Optional[str]:
        """requestsを使ってWebページを取得"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
                
        except Exception as e:
            print(f"ページの取得に失敗しました: {e}")
            return None
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Webページを取得（requestsが利用可能ならそれを使用、そうでなければcurl）"""
        if ENHANCED_MODE:
            content = self.fetch_page_requests(url)
        else:
            content = self.fetch_page_curl(url)
        
        if content:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            self.current_url = url
            self.add_to_history(url)
        
        return content
    
    def add_to_history(self, url: str):
        """履歴に追加"""
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        if not self.history or self.history[-1] != url:
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
    
    def parse_html_enhanced(self, html: str) -> Tuple[str, List[Tuple[str, str]], Dict]:
        """BeautifulSoupを使ってHTMLを解析"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # title取得
        title = soup.title.string if soup.title else "無題"
        
        # script, styleタグを除去
        for script in soup(["script", "style"]):
            script.decompose()
        
        # テキスト内容を取得
        text_content = soup.get_text()
        
        # 複数の空白や改行を整理
        lines = (line.strip() for line in text_content.splitlines())
        text_content = '\n'.join(line for line in lines if line)
        
        # リンクを抽出
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text().strip()
            
            # 相対URLを絶対URLに変換
            href = urllib.parse.urljoin(self.current_url, href)
            
            if link_text and href.startswith(('http://', 'https://')):
                links.append((href, link_text))
        
        # メタ情報
        meta_info = {
            'title': title,
            'description': '',
            'keywords': ''
        }
        
        # メタタグから情報を取得
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_info['description'] = meta_desc.get('content', '')
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            meta_info['keywords'] = meta_keywords.get('content', '')
        
        return text_content, links, meta_info
    
    def parse_html_basic(self, html: str) -> Tuple[str, List[Tuple[str, str]], Dict]:
        """基本的なHTMLパース（正規表現使用）"""
        import re
        
        # titleを抽出
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1) if title_match else "無題"
        
        # script, styleタグを除去
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
        
        # リンクを抽出
        links = []
        pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        
        for href, link_text in matches:
            href = urllib.parse.urljoin(self.current_url, href)
            link_text = re.sub(r'<[^>]+>', '', link_text).strip()
            if link_text and href.startswith(('http://', 'https://')):
                links.append((href, link_text))
        
        meta_info = {'title': title, 'description': '', 'keywords': ''}
        
        return text.strip(), links, meta_info
    
    def display_page(self, html: str):
        """ページ内容を表示"""
        if ENHANCED_MODE:
            text_content, links, meta_info = self.parse_html_enhanced(html)
        else:
            text_content, links, meta_info = self.parse_html_basic(html)
        
        print("=" * 80)
        print(f"📄 {meta_info['title']}")
        print(f"🌐 {self.current_url}")
        if meta_info['description']:
            print(f"📝 {meta_info['description'][:100]}...")
        print("=" * 80)
        
        # テキスト内容を表示
        if text_content:
            lines = text_content.split('\n')
            display_lines = []
            
            for line in lines[:150]:  # 最大150行まで表示
                if len(line) > 120:
                    display_lines.append(line[:120] + "...")
                else:
                    display_lines.append(line)
            
            print('\n'.join(display_lines))
            
            if len(lines) > 150:
                print(f"\n... (全{len(lines)}行中{len(display_lines)}行を表示)")
        
        print("\n" + "-" * 80)
        
        # リンクを表示
        if links:
            print("🔗 リンク:")
            for i, (url, text) in enumerate(links[:25]):  # 最大25個まで表示
                print(f"  {i+1:2d}. {text[:70]}...")
                print(f"      -> {url}")
            if len(links) > 25:
                print(f"  ... 他{len(links)-25}個のリンク")
        
        print("-" * 80)
    
    def add_bookmark(self, url: str = "", title: str = ""):
        """ブックマークに追加"""
        url = url or self.current_url
        if url:
            if not title and ENHANCED_MODE:
                # ページのタイトルを取得
                html = self.fetch_page(url)
                if html:
                    _, _, meta_info = self.parse_html_enhanced(html)
                    title = meta_info['title']
            
            title = title or url
            self.bookmarks.append((url, title))
            print(f"ブックマークに追加しました: {title}")
    
    def show_bookmarks(self):
        """ブックマーク一覧を表示"""
        if not self.bookmarks:
            print("ブックマークはありません。")
            return
        
        print("📚 ブックマーク:")
        for i, (url, title) in enumerate(self.bookmarks):
            print(f"  {i+1:2d}. {title}")
            print(f"      -> {url}")
    
    def search(self, query: str):
        """Google検索を実行"""
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        html = self.fetch_page(search_url)
        if html:
            self.display_page(html)
    
    def run(self, initial_url: str = ""):
        """ブラウザを実行"""
        print("🌐 Enhanced Terminal Browser")
        if ENHANCED_MODE:
            print("✅ BeautifulSoup4, requests が利用可能です")
        else:
            print("⚠️  基本機能で動作中（curlベース）")
        
        print()
        print("コマンド:")
        print("  [URL]           - URLを開く")
        print("  [数字]          - リンク番号を開く")
        print("  back            - 戻る")
        print("  forward         - 進む")
        print("  history         - 履歴表示")
        print("  bookmark        - ブックマークに追加")
        print("  bookmarks       - ブックマーク一覧")
        print("  search [クエリ]  - Google検索")
        print("  help            - ヘルプ表示")
        print("  quit            - 終了")
        print("=" * 80)
        
        if initial_url:
            html = self.fetch_page(initial_url)
            if html:
                self.display_page(html)
        
        while True:
            try:
                command = input("\n🌐 > ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("ブラウザを終了します。")
                    break
                
                elif command.lower() == 'help':
                    print("利用可能なコマンド:")
                    print("  URL入力、back、forward、history、bookmark、bookmarks、search、quit")
                
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
                    print("📚 履歴:")
                    for i, url in enumerate(self.history):
                        marker = " 👉 " if i == self.history_index else "    "
                        print(f"{marker}{i+1}. {url}")
                
                elif command.lower() == 'bookmark':
                    self.add_bookmark()
                
                elif command.lower() == 'bookmarks':
                    self.show_bookmarks()
                
                elif command.lower().startswith('search '):
                    query = command[7:].strip()
                    if query:
                        print(f"🔍 Google検索: {query}")
                        self.search(query)
                    else:
                        print("検索クエリを入力してください。")
                
                elif command.isdigit():
                    # 数字の場合はリンク番号として処理
                    if self.current_url:
                        html_content = self.fetch_page(self.current_url)
                        if html_content:
                            if ENHANCED_MODE:
                                _, links, _ = self.parse_html_enhanced(html_content)
                            else:
                                _, links, _ = self.parse_html_basic(html_content)
                            
                            link_num = int(command) - 1
                            if 0 <= link_num < len(links):
                                url = links[link_num][0]
                                print(f"🔗 リンクを開いています: {url}")
                                html = self.fetch_page(url)
                                if html:
                                    self.display_page(html)
                            else:
                                print("無効なリンク番号です。")
                    else:
                        print("まずページを開いてください。")
                
                else:
                    # URLとして処理
                    print(f"🌐 ページを読み込み中: {command}")
                    html = self.fetch_page(command)
                    if html:
                        self.display_page(html)
                
            except KeyboardInterrupt:
                print("\n\nブラウザを終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")

def main():
    browser = EnhancedBrowser()
    
    # コマンドライン引数でURLが指定された場合
    initial_url = sys.argv[1] if len(sys.argv) > 1 else ""
    
    browser.run(initial_url)

if __name__ == "__main__":
    main()
