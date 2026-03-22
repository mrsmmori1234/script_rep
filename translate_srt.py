import os
import deepl

# Ensure DEEPL_API_KEY is set in your environment variables
API_KEY = os.getenv("DEEPL_API_KEY")

def translate_srt():
    if not API_KEY:
        print("Error: 'DEEPL_API_KEY' environment variable not found.")
        return

    translator = deepl.Translator(API_KEY)

    # 1. Interactive Directory Selection
    target_dir = input("Enter the full path of the directory containing .srt files: ").strip()
    
    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a valid directory.")
        return

    # Filter .srt files
    files = [f for f in os.listdir(target_dir) if f.lower().endswith('.srt')]
    
    if not files:
        print("No .srt files found in the specified directory.")
        return

    # 2. Interactive Mode Selection
    print("\n--- Choose Translation Mode ---")
    print("1: Japanese Only")
    print("2: Bilingual (English + Japanese)")
    mode = input("Select option (1 or 2): ")

    for file_name in files:
        input_path = os.path.join(target_dir, file_name)
        print(f"Processing: {file_name}...")
        
        translated_lines = []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Keep index numbers and timestamps as is
            if line.isdigit() or '-->' in line:
                translated_lines.append(lines[i])
                i += 1
            elif line == "":
                translated_lines.append("\n")
                i += 1
            else:
                # Collect all text lines until the next empty line or index
                original_text_block = []
                while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().isdigit():
                    original_text_block.append(lines[i].strip())
                    i += 1
                
                original_text = " ".join(original_text_block)
                
                try:
                    # Translate to Japanese
                    result = translator.translate_text(original_text, target_lang="JA")
                    translated_text = result.text
                    
                    if mode == "1":
                        translated_lines.append(f"{translated_text}\n")
                    else:
                        # Bilingual: Original English followed by Japanese
                        translated_lines.append(f"{original_text}\n{translated_text}\n")
                except Exception as e:
                    print(f"Skip translating block due to error: {e}")
                    translated_lines.append(f"{original_text}\n")

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