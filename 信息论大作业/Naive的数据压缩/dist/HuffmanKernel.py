import os


class MyHuffman:

    def __init__(self, rpath):

        rpath = rpath.replace('\\', '/')   # 路径中统一用'/'
        self.rpath = rpath
        path_name = rpath.rsplit('/', 1)

        # self.prepath是文件所在目录， self.name是文件名
        #          如: F:/           如: 信息论-小组作业.pdf
        if len(path_name) == 2:
            self.prepath, self.name = rpath.rsplit('/', 1)
        else:
            self.prepath = ""
            self.name = path_name[0]

        # self.wpath是路径+去除后缀的文件名， 如F:/信息论-小组作业
        self.wpath = rpath.rsplit('.', 1)[0]

        '''print(self.path)
        print(self.name)
        print(self.wfile)'''

    class TreeNodes:

        def __init__(self, value=None, left=None, right=None, parent=None):
            self.value = value
            self.left = left
            self.right = right
            self.parent = parent
            self.codes = b''

    def do_encoding(self):

        rfile = open(self.rpath, 'rb')
        rfile.seek(0, 2)
        b_width = 1
        count = rfile.tell()
        count = int(count)
        # print(count)

        rfile.seek(0)
        a_bytes = b''
        all_bytes = []
        count_dict = {}

        for i in range(int(count)):
            a_bytes = rfile.read(1)
            # print(a_bytes)
            all_bytes.append(a_bytes)
            if count_dict.get(a_bytes, -1) == -1:
                count_dict[a_bytes] = 0
            count_dict[a_bytes] = count_dict[a_bytes] + 1

        rfile.close()
        print("Reading finished")
        # print(len(count_dict), len(all_bytes))

        count_list = sorted(count_dict.items(), key=lambda item: item[1], reverse=True)
        # print(count_list)
        nodes_list = []
        nodes_dict = {}

        for i in count_list:
            nodes_dict[i[0]] = self.TreeNodes(i[1])
            nodes_list.append(nodes_dict[i[0]])

        # print(nodes_dict)
        # print(nodes_list)
        head_node = self.__build_tree(nodes_list)

        '''for i in nodes_dict.keys():
            print(i, nodes_dict[i].parent.value)'''

        self.__get_code(head_node)
        '''for i in nodes_dict:
            print(i, nodes_dict[i].codes)'''

        max_num = count_list[0][1]
        b_width = 1
        if max_num > 16777215:
            b_width = 4
        elif max_num > 65535:
            b_width = 3
        elif max_num > 255:
            b_width = 2

        self.__write_encoding(count_dict, b_width, nodes_dict, all_bytes)
        print("Encode successfully")
        return self.wpath + '.huffman'

    def do_decoding(self):

        rfile = open(self.rpath, 'rb')
        rfile.seek(-1, 2)
        count = rfile.tell()
        count = int(count)
        move = int.from_bytes(rfile.read(1), byteorder='big')
        # print("move", move)
        rfile.seek(0)

        wname = rfile.readline().decode(encoding='utf8').strip('\n')
        if self.prepath == "":
            self.wpath = os.getcwd().replace('\\', '/') + '/' + wname
        else:
            self.wpath = self.prepath + '/' + wname
        # print("self.wpath: ", self.wpath)
        wfile = open(self.wpath, 'wb')

        nodes_count = int.from_bytes(rfile.read(2), byteorder='big')
        b_width = int.from_bytes(rfile.read(1), byteorder='big')
        # print(nodes_count, b_width)

        count_dict = {}
        for i in range(0, nodes_count):
            key = rfile.read(1)
            value = int.from_bytes(rfile.read(b_width), byteorder='big')
            # print("key, value: ", key, value)
            count_dict[key] = value

        count_list = sorted(count_dict.items(), key=lambda item: item[1], reverse=True)
        # print(count_list)
        nodes_list = []
        nodes_dict = {}

        for i in count_list:
            nodes_dict[i[0]] = self.TreeNodes(i[1])
            nodes_list.append(nodes_dict[i[0]])

        # print(nodes_dict)
        # print(nodes_list)
        head_node = self.__build_tree(nodes_list)

        self.__get_code(head_node)

        codes_dict = {}
        for i in nodes_dict:
            code = nodes_dict[i].codes
            codes_dict[code] = i
            # print(i, nodes_dict[i].codes)

        # print(codes_dict)

        i = rfile.tell()
        a_code = b''

        print("Start decoding...")
        while i < count - 1:  # 开始解压数据
            eight_bits = int.from_bytes(rfile.read(1), byteorder='big')
            i = i + 1
            j = 8
            while j > 0:

                if (eight_bits >> (j - 1)) & 1 == 1:
                    a_code = a_code + b'1'
                    eight_bits = eight_bits & (~(1 << (j - 1)))
                else:
                    a_code = a_code + b'0'
                    eight_bits = eight_bits & (~(1 << (j - 1)))

                if codes_dict.get(a_code, -1) != -1:
                    wfile.write(codes_dict[a_code])
                    wfile.flush()
                    # print(a_code)
                    a_code = b''
                j = j - 1

        # print("move", move)
        j = 8
        k = 8 - move
        eight_bits = int.from_bytes(rfile.read(1), byteorder='big')

        while k > 0:

            if (eight_bits >> (j - 1)) & 1 == 1:
                a_code = a_code + b'1'
                eight_bits = eight_bits & (~(1 << (j - 1)))
            else:
                a_code = a_code + b'0'
                eight_bits = eight_bits & (~(1 << (j - 1)))

            if codes_dict.get(a_code, -1) != -1:
                wfile.write(codes_dict[a_code])
                wfile.flush()
                a_code = b''
            j = j - 1
            k = k - 1

        wfile.close()
        rfile.close()
        print("Decode successfully")
        return self.wpath

    def __build_tree(self, nodes_list):

        sorted_nodes = nodes_list
        '''for i in sorted_nodes:
            print(i.value)'''
        while len(sorted_nodes) > 1:
            sorted_nodes = sorted(sorted_nodes, key=lambda anode: anode.value, reverse=False)
            lnode = sorted_nodes[0]
            rnode = sorted_nodes[1]
            new_node = self.TreeNodes(lnode.value + rnode.value, lnode, rnode)
            lnode.parent = new_node
            rnode.parent = new_node
            sorted_nodes.pop(0)
            sorted_nodes.pop(0)
            sorted_nodes.append(new_node)

        # for i in sorted_nodes:
            # print("maxvalue:", i.parent, i.left.parent.value, i.right.parent.value)

        return sorted_nodes[0]

    def __get_code(self, node):  # getcode逻辑错了

        if node is None:
            return

        if node.parent is None:
            node.codes = b''

        elif node == node.parent.left:
            node.codes = node.parent.codes + b'0'

        elif node == node.parent.right:
            node.codes = node.parent.codes + b'1'

        self.__get_code(node.left)
        self.__get_code(node.right)

        '''for i in nodes_list:
            print(i.codes, i.parent.value)'''

    def __write_encoding(self, count_dict, b_width, nodes_dict, all_bytes):

        wfile = open(self.wpath + '.huffman', "wb")
        # print(self.name, self.wpath)
        wfile.write((self.name + '\n').encode(encoding="utf8"))
        wfile.write(int.to_bytes(len(count_dict), 2, byteorder='big'))
        wfile.write(int.to_bytes(b_width, 1, byteorder='big'))
        for i in count_dict:
            wfile.write(i)
            wfile.write(int.to_bytes(count_dict[i], b_width, byteorder='big'))

        print("Start encoding...")

        eight_bit = 0b1
        for a_char in all_bytes:
            codes = nodes_dict[a_char].codes
            # print(a_char, codes, len(codes))
            # print("codes", codes)

            for a_bit in codes:

                # print(m, a_bit - 48)

                eight_bit = eight_bit << 1

                if a_bit == 49:   # 实际上就是codes中的'1'
                    eight_bit = eight_bit | 1
                if eight_bit.bit_length() == 9:
                    eight_bit = eight_bit & (~(1 << 8))
                    # print(eight_bit.bit_length())
                    wfile.write(int.to_bytes(eight_bit, 1, byteorder='big'))
                    # print("eight_bit", bin(eight_bit))
                    wfile.flush()
                    eight_bit = 0b1

        move = 0
        if eight_bit.bit_length() > 1:
            move = 9 - eight_bit.bit_length()
            eight_bit = eight_bit << (8 - (eight_bit.bit_length() - 1))
            eight_bit = eight_bit & (~(1 << eight_bit.bit_length() - 1))
            wfile.write(int.to_bytes(eight_bit, 1, byteorder='big'))

        wfile.write(int.to_bytes(move, 1, byteorder='big'))
        wfile.close()


if __name__ == '__main__':
    path1 = r"F:\PythonLanguage\pycProject\testDataCompression\刘慈欣01.三体I：地球往事.txt"
    test1 = MyHuffman(path1)
    test1.do_encoding()
    path2 = r"F:\PythonLanguage\pycProject\testDataCompression\刘慈欣01.三体I：地球往事.huffman"
    test2 = MyHuffman(path2)
    test2.do_decoding()

