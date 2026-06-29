import os
import sys
import warnings

# Suppress dependency warnings before importing libraries that use requests.
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")
warnings.filterwarnings("ignore", message=".*RequestsDependencyWarning.*")



def parse_srt_blocks(lines):
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.isdigit() or "-->" in line:
            blocks.append({"type": "meta", "text": lines[i]})
            i += 1
        elif line == "":
            blocks.append({"type": "empty", "text": "\n"})
            i += 1
        else:
            original_text_block = []
            while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().isdigit():
                original_text_block.append(lines[i].strip())
                i += 1

            original_text = " ".join(original_text_block)
            blocks.append({"type": "text", "original": original_text})
    return blocks


def translate_srt(input_path=None, mode="2", api_key=None, target_lang="JA", batch_size=50):
    api_key = api_key or os.getenv("DEEPL_API_KEY")
    if not api_key:
        print("Error: 'DEEPL_API_KEY' environment variable not found.")
        return None

    if input_path is None:
        input_path = input("Enter the full path of the .srt file: ")

    input_path = input_path.strip().strip('"').strip("'")

    if not os.path.isfile(input_path):
        print(f"Error: File not found at '{input_path}'")
        return None

    if not input_path.lower().endswith(".srt"):
        print(f"Error: '{input_path}' is not an .srt file.")
        return None

    if mode not in {"1", "2"}:
        print("Error: mode must be '1' for Japanese only or '2' for bilingual output.")
        return None

    import deepl

    translator = deepl.Translator(api_key)
    file_name = os.path.basename(input_path)
    target_dir = os.path.dirname(input_path)
    print(f"Processing: {file_name}...")

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    blocks = parse_srt_blocks(lines)
    text_to_translate = [b["original"] for b in blocks if b["type"] == "text"]

    print(f"Translating {len(text_to_translate)} blocks using DeepL...")

    translations = []
    try:
        for i in range(0, len(text_to_translate), batch_size):
            batch = text_to_translate[i : i + batch_size]
            print(f"  - Progress: {i}/{len(text_to_translate)} blocks...", end="\r")
            results = translator.translate_text(batch, target_lang=target_lang)
            translations.extend([r.text for r in results])

        print(f"  - Progress: {len(text_to_translate)}/{len(text_to_translate)} blocks... Done!")
    except Exception as e:
        print(f"\nError during translation: {e}")
        return None

    translated_lines = []
    trans_idx = 0
    for block in blocks:
        if block["type"] in {"meta", "empty"}:
            translated_lines.append(block["text"])
        elif block["type"] == "text":
            translated_text = translations[trans_idx]
            original_text = block["original"]

            if mode == "1":
                translated_lines.append(f"{translated_text}\n")
            else:
                translated_lines.append(f"{original_text}\n{translated_text}\n")
            trans_idx += 1

    suffix = "_JP" if mode == "1" else "_Bilingual"
    output_name = os.path.splitext(file_name)[0] + f"{suffix}.srt"
    output_path = os.path.join(target_dir, output_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)

    print(f"Saved: {output_name}")
    print("\nAll tasks completed.")
    return output_path


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    input_path = " ".join(argv) if argv else None
    translate_srt(input_path=input_path, mode="2")
    return 0


if __name__ == "__main__":
    sys.exit(main())