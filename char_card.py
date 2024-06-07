import struct
import base64

def extract_and_save_png_chunks(file_path, output_dir):
    with open(file_path, 'rb') as f:
        # Skip the 8-byte PNG file signature
        png_signature = f.read(8)
        
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
                
                if keyword != 'chara':
                    try:
                        # Decode the base64 text data to binary
                        png_data = base64.b64decode(text_data)
                        
                        # Save the binary data as a PNG file
                        output_file_path = f"{output_dir}/{keyword}.png"
                        with open(output_file_path, 'wb') as output_file:
                            output_file.write(png_data)
                        
                        print(f"Extracted PNG for keyword '{keyword}' saved as {output_file_path}")
                    except (base64.binascii.Error, UnicodeDecodeError) as e:
                        print(f"Failed to decode base64 data for keyword '{keyword}': {e}")
    
    print("Finished extracting and saving PNG chunks.")

# Usage example
file_path = './test.png'
output_dir = './test_assets'
extract_and_save_png_chunks(file_path, output_dir)
