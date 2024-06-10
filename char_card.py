import os
import json
import base64
import struct
import zipfile

def save_character_data(character_data, output_dir):
    character_name = character_data["data"]["name"]
    spec = character_data.get("spec", "")
    spec_version = character_data.get("spec_version", "")

    if spec == "chara_card_v2" and spec_version == "2.0":
        version_dir = "character_cards_v2"
    elif spec == "chara_card_v3" and spec_version == "3.0":
        version_dir = "character_cards_v3"
    else:
        print(f"Unsupported character card version: spec={spec}, spec_version={spec_version}")
        return

    chara_dir = os.path.join(output_dir, version_dir, character_name)
    os.makedirs(chara_dir, exist_ok=True)

    # Save the JSON data
    json_file_path = os.path.join(chara_dir, f"{character_name}.json")
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(character_data, json_file, ensure_ascii=False, indent=4)

    print(f"Extracted JSON for character '{character_name}' saved as {json_file_path}")
    return chara_dir

def extract_ccv3_from_png(file_path, output_dir):
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
                
                if keyword == 'ccv3':
                    # This is the base64 encoded JSON data for character
                    try:
                        # Decode the base64 encoded text data
                        chara_json_data = base64.b64decode(text_data).decode('utf-8')
                        character_data = json.loads(chara_json_data)
                        character_name = character_data["data"]["name"]
                    except (json.JSONDecodeError, base64.binascii.Error) as e:
                        print(f"Failed to decode JSON data for keyword 'ccv3': {e}")
                elif keyword == 'chara':
                    # This is the base64 encoded JSON data for Character Card V2
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
        if character_data:
            chara_dir = save_character_data(character_data, output_dir)
            
            if chara_dir:
                # Save the pending PNG files in the character's directory
                for keyword, png_data in pending_pngs:
                    output_file_path = os.path.join(chara_dir, f"{keyword}.png")
                    with open(output_file_path, 'wb') as output_file:
                        output_file.write(png_data)
                    print(f"Extracted PNG for keyword '{keyword}' saved as {output_file_path}")

def extract_ccv3_from_json(file_path, output_dir):
    with open(file_path, 'r', encoding='utf-8') as f:
        character_data = json.load(f)
        save_character_data(character_data, output_dir)

def extract_ccv3_from_charx(file_path, output_dir):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Extract the CharacterCardV3 JSON data
        with zip_ref.open('card.json') as json_file:
            character_data = json.load(json_file)
            chara_dir = save_character_data(character_data, output_dir)
        
        # Extract assets
        if chara_dir:
            for file_info in zip_ref.infolist():
                if file_info.filename != 'card.json':
                    extracted_path = zip_ref.extract(file_info, chara_dir)
                    print(f"Extracted asset '{file_info.filename}' saved as {extracted_path}")

def extract_ccv3(file_path, output_dir):
    if file_path.endswith(('.png', '.apng')):
        extract_ccv3_from_png(file_path, output_dir)
    elif file_path.endswith('.json'):
        extract_ccv3_from_json(file_path, output_dir)
    elif file_path.endswith('.charx'):
        extract_ccv3_from_charx(file_path, output_dir)
    else:
        print(f"Unsupported file type: {file_path}")

# Usage example
file_path = './char_card_upload/cherry.charx'  # Replace with your file path
output_dir = './character_cards'  # Replace with your output directory
extract_ccv3(file_path, output_dir)
