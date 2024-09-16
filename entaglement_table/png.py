from PIL import Image
import random



def reverse_bits(n, bit_size=32):
    reversed_n = 0
    for i in range(bit_size):
        # Extract the i-th bit from the number
        bit = (n >> i) & 1
        # Shift the bit to its reversed position
        reversed_n |= (bit << (bit_size - 1 - i))
    return reversed_n
class Entangler:
    def __init__(self, steg_bit_table):
        assert(len(steg_bit_table) == 256)
        self.table = steg_bit_table

    def Encode(self, container_png_filepath: str, data: bytes) -> bool:
        image = Image.open(container_png_filepath).convert('RGBA')
        w, h = image.size
        data_size = len(data)

        # Check if data fits in the image
        if data_size  + 4> (w * h) // 8 :
            return False

        print(f"size is {data_size:x}")
        pixels = image.load()
        for i in range(32):
            pixels[i + 1, 0] = self.BitInserter(pixels[i, 0], pixels[i + 1, 0], (data_size>> i) & 0b1)

        # Encode the actual data

        array_index = 0
        bit_counter = 0
        for y in range(h):
            for x in range(w):
                if array_index == data_size:
                    break

                if (x < 32 and y == 0):
                    continue
                if (x == w - 1 and y == h - 1):
                    break
                cur_pix = pixels[x, y]
                if (x == w - 1):
                    next_pix = pixels[0, y + 1]
                else:
                    next_pix = pixels[x + 1, y]


                next_new_val = self.BitInserter(cur_pix, next_pix, (data[array_index] >> bit_counter) & 0b1)
                if (x == w - 1):
                    pixels[0, y + 1] = next_new_val
                else:
                    pixels[x + 1, y] = next_new_val

                bit_counter = (bit_counter + 1) % 8
                if bit_counter == 0:
                    array_index += 1


        image.save("output.png")
        return True


    def BitInserter(self, pix1_t, pix2_t, msg_bit):
        pix1, pix2 = list(pix1_t), list(pix2_t)
        channel_to_modify = random.randint(0, 3)
        k = pix1[0] ^ pix1[1] ^ pix1[2] ^ pix1[3] ^\
            pix2[0] ^ pix2[1] ^ pix2[2] ^ pix2[3]

        if msg_bit == self.table[k]:
            return tuple(pix2)
        k_delta = k ^ pix2[channel_to_modify]

        mn, index = 256, 0
        for i in range(256):
            if self.table[i ^ k_delta] == msg_bit:
                value_delta = abs(pix2[channel_to_modify] - i )
                if value_delta < mn:
                    index = i
                    mn = value_delta

        pix2[channel_to_modify] = index
        assert (self.table[pix1[0] ^ pix1[1] ^ pix1[2] ^ pix1[3] ^\
            pix2[0] ^ pix2[1] ^ pix2[2] ^ pix2[3]] == msg_bit)
        return tuple(pix2)

    def BitExtractor(self, pix1, pix2):
        k = pix1[0] ^ pix1[1] ^ pix1[2] ^ pix1[3] ^\
            pix2[0] ^ pix2[1] ^ pix2[2] ^ pix2[3]

        return self.table[k]







    def Decode(self, encoded_container_png_filepath) -> bytes:
        image = Image.open(encoded_container_png_filepath).convert('RGBA')
        w, h = image.size
        pixels = image.load()

        # Decode the size of the data (first 4 pixels)
        size_bytes = 0 

        for i in range(32):
            fetched = self.BitExtractor(pixels[i, 0], pixels[i + 1, 0])
            size_bytes= (size_bytes<< 1) | fetched





        data_size = reverse_bits(size_bytes, 32)
        print(f"data size {data_size:x}")
        result = bytearray()

        # Decode the actual data


        bit_counter = 0
        tmp = 0
        for y in range(h):
            for x in range(w):
                if len(result)== data_size:
                    break
                if (x < 32 and y == 0):
                    continue
                if (x == w - 1 and y == h - 1):
                    break
                cur_pix = pixels[x, y]
                if (x == w - 1):
                    next_pix = pixels[0, y + 1]
                else:
                    next_pix = pixels[x + 1, y ]


                fetched = self.BitExtractor(cur_pix, next_pix )
                tmp = (tmp << 1) | fetched


                bit_counter = (bit_counter + 1) % 8
                if bit_counter == 0:
                    result.append(reverse_bits(tmp, 8))
                    tmp = 0
        return bytes(result)


if __name__ == "__main__":
    test_str = b"Test string!" * 200
    steg_key = [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1]
    C = Entangler(steg_key)
    C.Encode("sample.png", test_str)
    s = C.Decode("output.png")
    print(s)


