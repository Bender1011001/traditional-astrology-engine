import os

source_file = r"e:\code.projects\astrology\Binder1.txt"
output_dir = r"e:\code.projects\astrology\binder_chunks"
chunk_size = 750

def split_file():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # Fallback for other encodings if utf-8 fails, though unlikely for modern text files
        with open(source_file, 'r', encoding='latin-1') as f:
            lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines: {total_lines}")

    for i in range(0, total_lines, chunk_size):
        chunk_lines = lines[i:i + chunk_size]
        chunk_num = (i // chunk_size) + 1
        output_filename = os.path.join(output_dir, f"Binder1_part_{chunk_num:03d}.txt")
        
        with open(output_filename, 'w', encoding='utf-8') as chunk_file:
            chunk_file.writelines(chunk_lines)
        
        print(f"Wrote {len(chunk_lines)} lines to {output_filename}")

if __name__ == "__main__":
    split_file()
