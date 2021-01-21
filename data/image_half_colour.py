from PIL import Image
from pygame import image, Surface, surfarray, transform


class OCSimpleImage:
    def __init__(self, image=None):

        if isinstance(image, Surface):
            image = Image.fromarray(surfarray.pixels3d(transform.flip(transform.rotate(image, 90), False, True)), mode="RGB")

        self.image = image.convert(mode="RGBA") if image else None


    @staticmethod
    def _byte_encode(byte):
        # uses "!" (33) to "~" (126)
        return chr(int(ord('!')+byte*(94/255)))

    @staticmethod
    def _byte_decode(byte):
        return int((ord(byte) - ord('!')) * 255 / 94)

    def serialize(self):
        data_blob = ''.join(f"{OCSimpleImage._byte_encode(r)}{OCSimpleImage._byte_encode(g)}{OCSimpleImage._byte_encode(b)}" for r,g,b,a in self.image.getdata())
        return f"{self.image.width} {data_blob}"

    def deserialize(self, str, scale=1):
        image_width_s, data_blob = str.split()
        image_width = int(image_width_s)
        image_height = (len(data_blob)//3)//image_width

        out_image = Image.new("RGB", (image_width, image_height))

        for pixel_index in range(0, len(data_blob), 3):
            pixel_data = data_blob[pixel_index:pixel_index+3]
            r = OCSimpleImage._byte_decode(pixel_data[:1])
            g = OCSimpleImage._byte_decode(pixel_data[1:2])
            b = OCSimpleImage._byte_decode(pixel_data[2:3])
            pixel_pos = ((pixel_index//3) % image_width, pixel_index//3//image_width)
            out_image.putpixel(pixel_pos, (r,g,b))
        self.image = out_image.resize((out_image.width * scale, out_image.height * scale), resample=Image.NEAREST)
        return self
    def show(self):
        self.image.show()

    def get_surface(self) -> Surface:
        return image.frombuffer(self.image.tobytes(), (self.image.width, self.image.height), "RGB")

if __name__ == '__main__':
    import gzip
    fullsize_image = Image.open(r"../shamwow.png")
    scaled_image = fullsize_image.resize((int(fullsize_image.width/fullsize_image.height * 100), 100))
    print(scaled_image.size)
    x = OCSimpleImage(scaled_image)
    serialized = x.serialize()
    y = OCSimpleImage().deserialize(serialized)
    x.show()
    y.show()
    with open('../out.txt', 'w') as f:
        f.write(serialized)
    with open('../out_c.txt', 'wb') as f:
        f.write(gzip.compress(serialized.encode("ascii")))

    with open("../out_c.txt", 'rb') as f:
        serialized = gzip.decompress(f.read())
        y = OCSimpleImage().deserialize(serialized)
        y.show()