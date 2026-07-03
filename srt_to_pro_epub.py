import os
import re
from bs4 import BeautifulSoup
from ebooklib import epub

def clean_srt_content(srt_path):
    """SRTファイルからタイムスタンプを除去し、きれいなHTML段落を生成する"""
    if not os.path.exists(srt_path):
        return ""
    
    # タイムスタンプとインデックス番号を弾く正規表現
    pattern = re.compile(r"^\d+$|^\d\d:\d\d:\d\d[,\.]\d\d\d -->.*$")
    paragraphs = []
    
    with open(srt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not pattern.match(line):
                # 重複した字幕の微調整や、好みに応じた文字置換をここで行えます
                paragraphs.append(f"<p>{line}</p>")
                
    return "\n".join(paragraphs)

def create_pro_epub(srt_dir, output_epub_path, title="プロ仕様字幕集", author="Python書房", vertical=True):
    """ebooklibを使用して、Kindleに最適化された高品質なEPUBを生成する"""
    
    # 1. ブックオブジェクトの初期化と基本メタデータ設定
    book = epub.EpubBook()
    book.set_identifier(f"custom_srt_book_{title}")
    book.set_title(title)
    book.set_language("ja")
    book.add_author(author)
    
    # 2. スタイルシート（CSS）の設定
    # 外部ライブラリを使うことで、メディアクエリなど高度なCSSも安全にカプセル化できます
    if vertical:
        css_content = """
        @page { margin: 5%; }
        body {
            writing-mode: vertical-rl;
            -webkit-writing-mode: vertical-rl;
            -epub-writing-mode: vertical-rl;
            font-family: "serif", "Hiragino Mincho ProN", serif;
            line-height: 1.8;
            letter-spacing: 0.06em;
        }
        h1 {
            font-family: "sans-serif", "Hiragino Kaku Gothic ProN", sans-serif;
            font-size: 1.6em;
            margin-left: 2em;
            border-left: 3px solid #1e3799;
            padding-left: 0.5em;
        }
        p {
            text-align: justify;
            margin-top: 0;
            margin-bottom: 0;
            text-indent: 1em; /* 行頭1文字下げ */
        }
        """
        # Kindleに「右開き（縦書き用）」であることを明示するメタデータ
        book.spine.append('page-progression-direction="rtl"')
    else:
        css_content = """
        @page { margin: 5%; }
        body {
            font-family: "sans-serif", sans-serif;
            line-height: 1.6;
            color: #222;
        }
        h1 {
            font-size: 1.5em;
            border-bottom: 3px solid #1e3799;
            padding-bottom: 0.3em;
            margin-bottom: 1em;
        }
        p {
            margin-top: 0;
            margin-bottom: 0.8em;
            text-align: justify;
        }
        """
    
    style_item = epub.EpubItem(
        uid="style_nav",
        file_name="style/style.css",
        media_type="text/css",
        content=css_content
    )
    book.add_item(style_item)
    
    # 3. SRTファイルの読み込みと各章の生成
    srt_files = sorted([f for f in os.listdir(srt_dir) if f.endswith('.srt')])
    if not srt_files:
        print(f"エラー: '{srt_dir}' 内に .srt ファイルがありません。")
        return
        
    chapters = []
    
    for i, filename in enumerate(srt_files, start=1):
        ch_title = os.path.splitext(filename)[0]
        body_text = clean_srt_content(os.path.join(srt_dir, filename))
        
        # BeautifulSoupを使ってHTML構造をきれいに整形
        html_content = f"""
        <?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
        <head>
            <title>{ch_title}</title>
            <link rel="stylesheet" href="style/style.css" type="text/css" />
        </head>
        <body>
            <h1>{ch_title}</h1>
            {body_text}
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 章のオブジェクトを作成
        chapter = epub.EpubHtml(
            title=ch_title,
            file_name=f"chap_{i:02d}.xhtml",
            lang="ja"
        )
        chapter.content = str(soup)
        chapter.add_item(style_item)
        
        book.add_item(chapter)
        chapters.append(chapter)
        
    # 4. 目次（TOC）とナビゲーションの設定
    # これにより、Kindle端末の「移動」メニューに表示されるシステム目次が自動生成されます
    book.toc = tuple(chapters)
    
    # 本の背表紙（読み込み順序）の設定
    book.spine.extend(chapters)
    
    # NCXとNav（EPUB3標準の目次ファイル）を追加
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 5. ファイルの書き出し
    epub.write_epub(output_epub_path, book, {})
    print(f"プロ仕様のEPUBを出力しました: {output_epub_path}")

# ─── 実行部分 ───
if __name__ == "__main__":
    # 使用する際は、スクリプトと同じ場所に「srt_folder」を作成し、.srtを入れてください
    create_pro_epub(
        srt_dir="/mnt/d/Youtube/Movie_Pool",
        output_epub_path="/mnt/d/Youtube/Movie_Pool.epub",
        title="Movie_Pool",
        #author="マイ・ライブラリ",
        vertical=False # Trueで綺麗な縦書き、Falseで横書き
    )
