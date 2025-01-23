import argparse
import re

def is_fake_subtitle(subtitle_block):
    # Check for characteristics of fake subtitles
    if 'color000000' in subtitle_block:
        return True
    if 'line:' in subtitle_block and any(f'line:{n}' in subtitle_block for n in range(100, 999)):
        return True
    if all(char in '​ \n' for char in re.sub(r'<[^>]+>', '', subtitle_block)):  # Check if only whitespace
        return True
    return False

def clean_subtitle_text(text):
    # Remove HTML tags and clean up the text
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[​]+', '', text)  # Remove zero-width spaces
    text = text.strip()
    return text

def process_vtt(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into blocks
    blocks = content.split('\n\n')
    
    # Keep header (first block)
    header = "WEBVTT\nKind: captions\nLanguage: en-US\n"
    
    # Process subtitle blocks
    processed_blocks = []
    seen_texts = set()
    
    for block in blocks[1:]:  # Skip header block
        if block.strip() and not block.startswith('Style:') and not is_fake_subtitle(block):
            # Extract timestamp and text
            lines = block.split('\n')
            if len(lines) >= 2:
                timestamp_line = lines[0]
                # Simplify timestamp line (remove positioning)
                timestamp_line = re.sub(r'\s+align:.*$', '', timestamp_line)
                timestamp_line = re.sub(r'\s+position:.*$', '', timestamp_line)
                
                subtitle_text = clean_subtitle_text('\n'.join(lines[1:]))
                
                if subtitle_text and subtitle_text not in seen_texts:
                    seen_texts.add(subtitle_text)
                    processed_blocks.append(f"{timestamp_line}\n{subtitle_text}")

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header + '\n')
        f.write('\n\n'.join(processed_blocks))
        f.write('\n\n')

def main():
    parser = argparse.ArgumentParser(description='Unobfuscate VTT files')
    parser.add_argument('-i', '--input', required=True, help='Input VTT file')
    parser.add_argument('-o', '--output', required=True, help='Output VTT file')
    
    args = parser.parse_args()
    process_vtt(args.input, args.output)

if __name__ == "__main__":
    main()