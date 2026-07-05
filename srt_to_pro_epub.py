import os
import sys
import re
from bs4 import BeautifulSoup
from ebooklib import epub

def clean_srt_content(srt_path):
    """Remove timestamps from SRT files and generate clean HTML paragraphs"""
    if not os.path.exists(srt_path):
        return ""

    # Regular expression to exclude timestamps and index numbers
    pattern = re.compile(r"^\d+$|^\d\d:\d\d:\d\d[,\.]\d\d\d -->.*$")
    paragraphs = []

    with open(srt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines, timestamp lines, or index lines
            if not line or pattern.match(line):
                continue

            paragraphs.append(f"<p>{line}</p>")

    return "\n".join(paragraphs)

def create_pro_epub_from_file(srt_path, output_epub_path, author="Python Books", vertical=False):
    """Generate high-quality EPUB optimized for Kindle from a single SRT file"""
    title = os.path.splitext(os.path.basename(srt_path))[0]

    book = epub.EpubBook()
    book.set_identifier(f"custom_srt_book_{hash(title)}")
    book.set_title(title)
    book.set_language("ja")
    book.add_author(author)

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
            text-indent: 1em;
        }
        """
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
            margin-bottom: 0.5em;
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

    body_text = clean_srt_content(srt_path)
    soup = BeautifulSoup(body_text, "html.parser")
    cleaned_body = soup.encode(formatter="html").decode("utf-8")

    chapter = epub.EpubHtml(
        title=title,
        file_name="chap_01.xhtml",
        lang="ja"
    )
    chapter.content = f"<h1>{title}</h1>\n{cleaned_body}"
    chapter.add_item(style_item)

    book.add_item(chapter)
    book.toc = (chapter,)
    book.spine.extend([chapter])
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(output_epub_path, book, {})
    print(f"Output professional-grade EPUB: {output_epub_path}")

def convert(srt_path, vertical=False):
    """外部から呼び出すためのメインエントリポイント関数"""
    if not srt_path.endswith('.srt') or not os.path.exists(srt_path):
        print(f"Error: Valid SRT file not found. Input path: {srt_path}")
        return False

    output_epub = os.path.splitext(srt_path)[0] + ".epub"
    create_pro_epub_from_file(srt_path, output_epub, vertical=vertical)
    return True

# ─── When run directly from the command line ───
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python srt_to_pro_epub.py [SRT file path]")
        sys.exit(1)

    convert(sys.argv[1])
