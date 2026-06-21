import warnings

# Suppress dependency warnings before importing libraries that use requests
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")
warnings.filterwarnings("ignore", message=".*RequestsDependencyWarning.*")

import os
import deepl
import sys

# Ensure DEEPL_API_KEY is set in your environment variables
API_KEY = os.getenv("DEEPL_API_KEY")

def translate_srt():
    if not API_KEY:
        print("Error: 'DEEPL_API_KEY' environment variable not found.")
        return

    translator = deepl.Translator(API_KEY)

    # 1. Interactive File Selection
    if len(sys.argv) > 1:
        # Join all arguments to handle paths with spaces without requiring quotes
        input_path = " ".join(sys.argv[1:])
    else:
        input_path = input("Enter the full path of the .srt file: ")
    
    # Clean up the path (strip quotes if the user pasted them)
    input_path = input_path.strip().strip('"').strip("'")

    if not os.path.isfile(input_path):
        print(f"Error: File not found at '{input_path}'")
        return

    if not input_path.lower().endswith('.srt'):
        print(f"Error: '{input_path}' is not an .srt file.")
        return

    # 2. Interactive Mode Selection
    # print("\n--- Choose Translation Mode ---")
    # print("1: Japanese Only")
    # print("2: Bilingual (English + Japanese)")
    # mode = input("Select option (1 or 2): ")
    mode = "2"

    file_name = os.path.basename(input_path)
    target_dir = os.path.dirname(input_path)
    print(f"Processing: {file_name}...")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    blocks = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Keep index numbers and timestamps as is
        if line.isdigit() or '-->' in line:
            blocks.append({"type": "meta", "text": lines[i]})
            i += 1
        elif line == "":
            blocks.append({"type": "empty", "text": "\n"})
            i += 1
        else:
            # Collect all text lines until the next empty line or index
            original_text_block = []
            while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().isdigit():
                original_text_block.append(lines[i].strip())
                i += 1
            
            original_text = " ".join(original_text_block)
            blocks.append({"type": "text", "original": original_text})

    # Extract text to translate
    text_to_translate = [b["original"] for b in blocks if b["type"] == "text"]
    
    print(f"Translating {len(text_to_translate)} blocks using DeepL...")
    
    translations = []
    batch_size = 50  # Split into batches to avoid "413 Request Entity Too Large"
    
    try:
        for i in range(0, len(text_to_translate), batch_size):
            batch = text_to_translate[i : i + batch_size]
            print(f"  - Progress: {i}/{len(text_to_translate)} blocks...", end='\r')
            
            # Batch translation
            results = translator.translate_text(batch, target_lang="JA")
            translations.extend([r.text for r in results])
        
        print(f"  - Progress: {len(text_to_translate)}/{len(text_to_translate)} blocks... Done!")
    except Exception as e:
        print(f"\nError during translation: {e}")
        return

    # Reconstruct lines
    translated_lines = []
    trans_idx = 0
    for b in blocks:
        if b["type"] == "meta" or b["type"] == "empty":
            translated_lines.append(b["text"])
        elif b["type"] == "text":
            translated_text = translations[trans_idx]
            original_text = b["original"]
            
            if mode == "1":
                translated_lines.append(f"{translated_text}\n")
            else:
                # Bilingual: Original English followed by Japanese
                translated_lines.append(f"{original_text}\n{translated_text}\n")
            trans_idx += 1

    # 3. Save Output in the same directory
    suffix = "_JP" if mode == "1" else "_Bilingual"
    output_name = os.path.splitext(file_name)[0] + f"{suffix}.srt"
    output_path = os.path.join(target_dir, output_name)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    
    print(f"Saved: {output_name}")

    print("\nAll tasks completed.")

if __name__ == "__main__":
    translate_srt()