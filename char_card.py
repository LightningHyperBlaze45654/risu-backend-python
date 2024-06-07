import struct
import base64

def extract_all_text_chunks(file_path):
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
                
                # Decode the base64 text data to utf-8
                try:
                    decoded_text = base64.b64decode(text_data).decode('utf-8')
                except (base64.binascii.Error, UnicodeDecodeError):
                    decoded_text = text_data.decode('latin-1')
                
                print(f"Keyword: {keyword}")
                print(f"Text: {decoded_text}")
                print('---')
    
    print("Finished reading all tEXt chunks.")

# Usage example
file_path = './test.png'
extract_all_text_chunks(file_path)
