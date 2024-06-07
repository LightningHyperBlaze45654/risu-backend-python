import struct
import base64
import json
import os

def extract_and_save_png_chunks(file_path, output_dir):
    with open(file_path, 'rb') as f:
        # Skip the 8-byte PNG file signature
        png_signature = f.read(8)
        
        character_data = None
        character_name = None
        pending_pngs = []
        
        while True:
            # Read the length of the chunk (4 bytes, big-endian)
            length_bytes = f.read(4)
            if len(length_bytes) == 0:
                break  # End of file
            
            length = struct.unpack('>I', length_bytes)[0]
            
            # Read the chunk type (4 bytes)
            chunk_type = f.read(4).decode('ascii')
            
            # Read the chunk data
            chunk_data = f.read(length)
            
            # Read the CRC (4 bytes)
            crc = f.read(4)
            
            if chunk_type == 'tEXt':
                # Split the chunk data into keyword and text
                keyword_data, text_data = chunk_data.split(b'\x00', 1)
                keyword = keyword_data.decode('ascii')
                
                if keyword == 'chara':
                    # This is the base64 encoded JSON data for character
                    try:
                        # Decode the base64 encoded text data
                        chara_json_data = base64.b64decode(text_data).decode('utf-8')
                        character_data = json.loads(chara_json_data)
                        character_name = character_data["data"]["name"]
                    except (json.JSONDecodeError, base64.binascii.Error) as e:
                        print(f"Failed to decode JSON data for keyword 'chara': {e}")
                else:
                    try:
                        # Decode the base64 text data to binary
                        png_data = base64.b64decode(text_data)
                        pending_pngs.append((keyword, png_data))
                    except (base64.binascii.Error, UnicodeDecodeError) as e:
                        print(f"Failed to decode base64 data for keyword '{keyword}': {e}")

        # After processing all chunks, save the character JSON data and pending PNGs if available
        if character_data and character_name:
            chara_dir = os.path.join(output_dir, character_name)
            os.makedirs(chara_dir, exist_ok=True)
            
            # Save the JSON data
            json_file_path = os.path.join(chara_dir, f"{character_name}.json")
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(character_data, json_file, ensure_ascii=False, indent=4)
            
            print(f"Extracted JSON for character '{character_name}' saved as {json_file_path}")
            
            # Save the pending PNG files in the character's directory
            for keyword, png_data in pending_pngs:
                output_file_path = os.path.join(chara_dir, f"{keyword}.png")
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(png_data)
                print(f"Extracted PNG for keyword '{keyword}' saved as {output_file_path}")
    
    print("Finished extracting and saving PNG and JSON chunks.")

# Usage example
file_path = './cherry.png'
output_dir = './character_cards'
extract_and_save_png_chunks(file_path, output_dir)
