import os


class MyLzss:

    def __init__(self, rpath):

        rpath = rpath.replace('\\', '/')
        self.rpath = rpath
        path_name = rpath.rsplit("/", 1)
        # print(path_name)

        if len(path_name) == 2:
            self.prepath, self.name = rpath.rsplit("/", 1)
        else:
            self.prepath = ""
            self.name = path_name[0]

        self.wpath = rpath.rsplit('.', 1)[0]
        # print(self.wpath)

        self.pre_buffer_str = b''
        self.slide_windows_str = b''
        self.match_str = b''
        self.match_poi = 0

        self.match_num = 2
        self.pre_buffer_bits = 4
        self.pre_buffer_size = (1 << self.pre_buffer_bits) - 1 + self.match_num
        self.slide_windows_size = (1 << (16 - self.pre_buffer_bits)) - 1 + self.match_num
        # print(self.pre_buffer_size, self.slide_windows_size)

    def do_encoding(self):
        rfile = open(self.rpath, 'rb')
        wfile = open(self.wpath + '.lzss', 'wb')
        wfile.write((self.name + '\n').encode(encoding='utf8'))

        write_buff = b''
        sign = 0
        eight_count = 0

        print("Start encoding...")
        self.pre_buffer_str = rfile.read(self.pre_buffer_size)

        while self.pre_buffer_str != b'':

            self.match_poi = -1
            self.match_str = b''
            for i in range(self.match_num, len(self.pre_buffer_str) + 1):

                poi = self.slide_windows_str.find(self.pre_buffer_str[0: i])
                if poi != -1:
                    self.match_str = self.pre_buffer_str[0: i]
                    self.match_poi = poi
                else:
                    break

            if self.match_poi == -1:
                self.match_str = self.pre_buffer_str[: 1]
                write_buff += self.match_str
            else:
                write_buff += int.to_bytes(self.match_poi * (1 << self.pre_buffer_bits)
                                           + len(self.match_str) - self.match_num, 2, byteorder='big')
                sign += (1 << (7 - eight_count))

            eight_count += 1

            if eight_count >= 8:
                eight_items = int.to_bytes(sign, 1, byteorder='big') + write_buff
                wfile.write(eight_items)
                write_buff = b''
                sign = 0
                eight_count = 0

            self.pre_buffer_str = self.pre_buffer_str[len(self.match_str):]
            self.pre_buffer_str += rfile.read(self.pre_buffer_size - len(self.pre_buffer_str))
            self.slide_windows_str += self.match_str
            if len(self.slide_windows_str) > self.slide_windows_size:
                self.slide_windows_str = self.slide_windows_str[len(self.slide_windows_str) - self.slide_windows_size:]

        if write_buff != b'':
            eight_items = int.to_bytes(sign, 1, byteorder='big') + write_buff
            wfile.write(eight_items)

        rfile.close()
        wfile.close()
        print("Encode successfully")
        return self.wpath + '.lzss'

    def do_decoding(self):
        rfile = open(self.rpath, 'rb')
        wname = rfile.readline().decode(encoding='utf8').strip('\n')
        # print(wname)
        if self.prepath == "":
            self.wpath = os.getcwd().replace('\\', '/') + '/' + wname
        else:
            self.wpath = self.prepath + '/' + wname

        wfile = open(self.wpath, 'wb')

        self.slide_windows_str = b''
        self.pre_buffer_str = rfile.read(1)

        print("Start decoding...")
        while self.pre_buffer_str != b'':

            for i in range(8):
                if (self.pre_buffer_str[0]) & (1 << (7 - i)) == 0:
                    write_bytes = rfile.read(1)
                    self.slide_windows_str += write_bytes
                    wfile.write(write_bytes)

                else:
                    write_bytes = rfile.read(2)
                    start = (((write_bytes[0] << 8) + write_bytes[1]) // (1 << self.pre_buffer_bits))
                    end = start + write_bytes[1] % (1 << self.pre_buffer_bits) + self.match_num
                    wfile.write(self.slide_windows_str[start:end])
                    self.slide_windows_str += self.slide_windows_str[start: end]

                if len(self.slide_windows_str) > self.slide_windows_size:
                    self.slide_windows_str = \
                        self.slide_windows_str[len(self.slide_windows_str) - self.slide_windows_size:]

            self.pre_buffer_str = rfile.read(1)

        rfile.close()
        wfile.close()
        print("Decode successfully")
        return self.wpath


if __name__ == '__main__':
    path1 = r"F:\PythonLanguage\pycProject\testDataCompression\刘慈欣01.三体I：地球往事.txt"
    test1 = MyLzss(path1)
    test1.do_encoding()
    path2 = r"F:\PythonLanguage\pycProject\testDataCompression\刘慈欣01.三体I：地球往事.lzss"
    test2 = MyLzss(path2)
    test2.do_decoding()
