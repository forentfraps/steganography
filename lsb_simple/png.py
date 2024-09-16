from PIL import Image

class LSB_steg:
    @staticmethod
    def Encode(container_png_filepath: str, data: bytes) -> bool:
        image = Image.open(container_png_filepath).convert('RGBA')
        w, h = image.size
        data_size = len(data)

        # Check if data fits in the image
        if data_size > (w * h) - 4:
            return False

        print(f"size is {h * w}")
        pixels = image.load()
        size_bytes = data_size.to_bytes(4, 'big')
        for i in range(4):
            pixels[i, 0] = LSB_steg.BitSwapper(pixels[i, 0], size_bytes[i])

        # Encode the actual data
        for y in range(h):
            for x in range(w):
                if y == 0 and x < 4:
                    continue  # Skip the first 4 pixels where size is stored
                data_index = (y * w + x) - 4
                if data_index < data_size:
                    pixels[x, y] = LSB_steg.BitSwapper(pixels[x, y], data[data_index])
                else:
                    break

        image.save("output.png")
        return True

    @staticmethod
    def BitSwapper(tuple_dest, source):
        dest = list(tuple_dest)

        # Insert 2 bits of source into each channel
        for i in range(4):
            # Mask the least 2 bits of the current channel and set the 2 LSB from source
            masked_channel = dest[i] & 0b11111100
            shifted_back_byte_part = (source >> (i * 2)) & 0b11
            dest[i] = masked_channel | shifted_back_byte_part
        return tuple(dest)


    @staticmethod
    def Decode(encoded_container_png_filepath) -> bytes:
        image = Image.open(encoded_container_png_filepath).convert('RGBA')
        w, h = image.size
        pixels = image.load()

        # Decode the size of the data (first 4 pixels)
        size_bytes = bytearray()
        for i in range(4):
            r, g, b, a = pixels[i, 0]
            size_bytes.append(((r & 0b11) | ((g & 0b11) << 2) | ((b & 0b11) << 4) | ((a & 0b11) << 6)))

        data_size = int.from_bytes(size_bytes, 'big')
        print(f"data size {data_size:x}")
        result = bytearray()

        # Decode the actual data
        for y in range(h):
            for x in range(w):
                if y == 0 and x < 4:
                    continue  # Skip the first 4 pixels where size is stored
                data_index = (y * w + x) - 4
                if data_index < data_size:
                    r, g, b, a = pixels[x, y]
                    byte = (r & 0b11) | ((g & 0b11) << 2) | ((b & 0b11) << 4) | ((a & 0b11) << 6)
                    result.append(byte )

        return bytes(result)


if __name__ == "__main__":
    test_str = b"Test string!" *1000
    LSB_steg.Encode("sample.png", test_str)
    s = LSB_steg.Decode("output.png")
    print(s)

