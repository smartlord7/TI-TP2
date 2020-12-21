from PIL import Image

from source_code.cmp.modules.compression.huffmancodec import HuffmanCodec, _EndOfFileSymbol
from source_code.cmp.modules.filters import sub as sub, paeth as paeth
from source_code.cmp.modules.transforms import mtf as mtf
from source_code.cmp.modules.compression import lzw as lzw, rle as rle, lzma as lzma
import source_code.cmp.modules.util.encoding_file_writer as frw
import matplotlib.image as img
import numpy as np
import os
import time
import warnings


class InvalidFileExtensionError(Exception):
    pass


class InvalidColorSpaceError(Exception):
    pass


class BMPCompressor:
    INITIAL_ALPHABET_LENGTH = 256
    ESCAPE_CHARACTER = -256
    EOF_SYMBOL = _EndOfFileSymbol()
    FILE_EXTENSION = '.cmp'
    ALPHABET = [i for i in range(256)]

    def __init__(self, input_file_path, output_file_path, benchmark=False, log_data=False):
        if not input_file_path.endswith('.bmp'):
            raise InvalidFileExtensionError
        matrix_data = img.imread(input_file_path)
        l_shape = len(matrix_data.shape)
        if 2 > l_shape or l_shape > 3:
            raise InvalidColorSpaceError
        if l_shape == 3:
            matrix_data = matrix_data[:, :, 0]
        if log_data:
            print(matrix_data)
        self.rle = False
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.file_name = self.input_file_path.split('/')[::-1][0]
        self.log_file = open(self.output_file_path + self.file_name.split('.')[0] + '_cmp_log.txt', 'w')
        self.log_file.write('-------%s CMP COMPRESSION LOG-------\n\n'
                            'COMPRESSION STACK: \n' % self.file_name)
        self.benchmark = benchmark
        self.log_data = log_data
        self.image_width = matrix_data.shape[0]
        self.image_height = matrix_data.shape[1]
        self.original_data = matrix_data
        self.compressed_data = self.original_data
        self.total_time = int()
        self.encoding_table = None

    def apply_simple_filter(self, up):
        if up:
            self.log_file.write(' -> UP FILTER\n')
        else:
            self.log_file.write(' -> SUB FILTER\n')
        now = time.perf_counter()
        if self.benchmark:
            if up:
                print('Applying up filter...')
            else:
                print('Applying sub filter...')
        self.compressed_data = sub.apply_simple_filter(self.compressed_data, up=up)
        diff = time.perf_counter() - now
        self.total_time += diff
        if self.benchmark:
            if up:
                print('Ellapsed up filtering time: %.2f sec' % diff)
            else:
                print('Ellapsed sub filtering time: %.2f sec' % diff)
        if self.log_data:
            print(self.compressed_data)

    def apply_simplified_paeth_filter(self):
        self.log_file.write(' -> SIMPLE PAETH FILTER\n')
        now = time.perf_counter()
        if self.benchmark:
            print('Applying simple Paeth filter...')
        self.compressed_data = paeth.apply_simplified_paeth_filter(self.compressed_data, self.image_width, self.image_height)
        diff = time.perf_counter() - now
        self.total_time += diff
        if self.benchmark:
            print('Ellapsed simple Paeth filtering time: %.2f sec' % diff)
        if self.log_data:
            print(self.compressed_data)

    def apply_mtf(self):
        self.log_file.write(' -> MTF\n')
        now = time.perf_counter()
        if self.benchmark:
            print('Applying MTF...')
        self.compressed_data = np.array(mtf.apply_mtf(np.array(self.compressed_data).ravel(), self.ALPHABET))
        diff = time.perf_counter() - now
        self.total_time += diff
        if self.benchmark:
            print('Ellapsed MTF encoding time: %.2f sec' % diff)
        if self.log_data:
            print(self.compressed_data)

    def apply_rle(self):
        self.rle = True
        self.log_file.write(' -> RLE\n')
        now = time.perf_counter()
        if self.benchmark:
            print('Applying RLE encoding...')
        self.compressed_data = np.array(rle.rle_encode(np.array(self.compressed_data).ravel(), self.ESCAPE_CHARACTER)).astype(np.int32)
        diff = time.perf_counter() - now
        self.total_time += diff
        if self.benchmark:
            print('Ellapsed RLE encoding time: %.2f sec' % diff)
        if self.log_data:
            print(self.compressed_data)

    def apply_lzw(self, max_size, reset_dict):
        self.log_file.write(' -> LZW WITH DICT MAX SIZE OF %d' % max_size)
        if reset_dict:
            self.log_file.write(' AND WITH DICT RESET\n')
        else:
            self.log_file.write(' AND WITHOUT DICT RESET\n')
        now = time.perf_counter()
        if self.benchmark:
            print('Applying LZW encoding...')
        self.compressed_data = np.array(lzw.lzw_encode(self.compressed_data, limit=max_size, reset_dictionary=reset_dict))
        diff = time.perf_counter() - now
        self.total_time += diff
        if self.benchmark:
            print('Ellapsed LZW encoding time: %.2f sec' % diff)
        if self.log_data:
            print(self.compressed_data)

    def apply_lzma(self):
        self.log_file.write(' -> LZMA\n')
        now = time.perf_counter()
        if self.benchmark:
            print('Applying LZMA encoding...')
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_RAW, filters=[{'id':lzma.FILTER_LZMA2}])
        self.compressed_data = compressor.compress(bytearray(np.array(self.compressed_data))) + compressor.flush()
        diff = time.perf_counter() - now
        self.total_time += diff
        if self.benchmark:
            print('Ellapsed LZMA encoding time: %.2f sec' % diff)
        if self.log_data:
            print(self.compressed_data)

    def apply_huffman_encoding(self):
        self.log_file.write(' -> HUFFMAN ENCODING\n')
        now = time.perf_counter()
        if self.benchmark:
            print('Applying Huffman encoding...')
        self.compressed_data = np.concatenate((self.compressed_data, [self.EOF_SYMBOL]))
        self.encoding_table = HuffmanCodec.from_data(self.compressed_data).get_code_table()
        self.compressed_data = frw.encode(self.compressed_data, self.encoding_table, eof_symbol=self.EOF_SYMBOL)
        diff = time.perf_counter() - now
        self.total_time += diff
        if self.benchmark:
            print('Ellapsed huffman encoding time: %.2f sec' % diff)
        if self.log_data:
            print(self.compressed_data)

    def __build_cmp_header(self):
        header = {
                'size': self.image_width * self.image_height,
                'width': self.image_width,
                'height': self.image_height,
                'rle': self.rle
            }
        if self.encoding_table:
            header['encoding_table'] = self.encoding_table
        return header

    def write_in_file(self):
        output_file_name = self.file_name.split('.')[0] + self.FILE_EXTENSION
        initial_size, compressed_size = os.path.getsize(self.input_file_path), os.path.getsize(self.output_file_path + output_file_name)
        compression_ratio = (initial_size - compressed_size) / initial_size * 100
        self.log_file.write('\nTOTAL ELLAPSED COMPRESSION TIME: %.2f sec.\n'
                            'INITIAL IMAGE SIZE: %d bytes\n'
                            'COMPRESSED IMAGE SIZE: %d bytes\n'
                            'COMPRESSION RATIO: %.2f%%\n' % (self.total_time, initial_size, compressed_size, compression_ratio))
        self.log_file.close()
        if self.benchmark:
            print('Total ellapsed compression time: %.2f sec' % self.total_time)
            print('Writing in file %s...' % output_file_name)
        frw.write_file(self.output_file_path + output_file_name, self.compressed_data,
                           self.__build_cmp_header())

    def toggle_benchmark(self):
        self.benchmark = not self.benchmark

    def toggle_log_data(self):
        self.log_data = not self.log_data

    def get_original_data(self):
        return self.original_data

    def get_compressed_data(self):
        return self.compressed_data


class CMPDecompressor:
    EOF_SYMBOL = _EndOfFileSymbol()
    ESCAPE_CHARACTER = -256
    FILE_EXTENSION = '.bmp'
    ALPHABET = [i for i in range(256)]

    def __init__(self, input_file_path, output_file_path, benchmark=False, log_data=False):
        if not input_file_path.endswith('cmp'):
            raise InvalidFileExtensionError

        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.header, self.compressed_data = frw.read_file(input_file_path)
        if log_data:
            print(self.compressed_data)
        self.benchmark = benchmark
        self.log_data = log_data
        self.total_time = int()
        self.original_data = self.compressed_data

    def apply_inverse_huffman_encoding(self):
        if self.benchmark:
            now = time.perf_counter()
            print('Applying Inverse Huffman Encoding...')
        self.original_data = frw.decode(self.original_data, self.header['encoding_table'], self.EOF_SYMBOL)
        if self.benchmark:
            diff = time.perf_counter() - now
            self.total_time += diff
            print('Ellapsed huffman encoding inversion time: %.2f sec' % diff)
        if self.log_data:
            print(self.original_data)

    def apply_inverse_rle(self):
        if self.benchmark:
            now = time.perf_counter()
            print('Applying Inverse RLE...')
        self.original_data = np.array(rle.rle_decode(self.original_data, self.ESCAPE_CHARACTER))
        if self.benchmark:
            diff = time.perf_counter() - now
            self.total_time += diff
            print('Ellapsed RLE inversion time: %.2f sec' % diff)
        if self.log_data:
            print(self.original_data)

    def apply_inverse_lzw(self):
        if self.benchmark:
            now = time.perf_counter()
            print('Applying Inverse LZW Encoding ...')
        self.original_data = np.array(lzw.lzw_decode(self.original_data))
        if self.benchmark:
            diff = time.perf_counter() - now
            self.total_time += diff
            print('Ellapsed Inverse LZW Encoding time: %.2f sec' % diff)
        if self.log_data:
            print(self.original_data)

    def apply_inverse_lzma(self):
        if self.benchmark:
            now = time.perf_counter()
            print('Applying Inverse LZMA Encoding ...')
        decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[{'id':lzma.FILTER_LZMA2}])
        if self.header['rle']:
            self.original_data = np.frombuffer(decompressor.decompress(self.original_data), dtype=np.int32)
        else:
            self.original_data = np.frombuffer(decompressor.decompress(self.original_data), dtype=np.uint8)
        if self.benchmark:
            diff = time.perf_counter() - now
            self.total_time += diff
            print('Ellapsed Inverse LZMA Encoding time: %.2f sec' % diff)
        if self.log_data:
            print(self.original_data)

    def apply_inverse_mtf(self):
        if self.benchmark:
            now = time.perf_counter()
            print('Applying Inverse MTF...')
        self.original_data = np.array(mtf.invert_mtf(self.original_data, self.ALPHABET)).astype(np.uint8)
        if self.benchmark:
            diff = time.perf_counter() - now
            self.total_time += diff
            print('Ellapsed MTF inversion time: %.2f sec' % diff)
        if self.log_data:
            print(self.original_data)

    def apply_inverse_simple_filter(self, up):
        warnings.filterwarnings('ignore')
        if self.benchmark:
            now = time.perf_counter()
            print('Applying inverse simple filter...')
        self.original_data = sub.invert_simple_filter(self.original_data, self.header['width'], self.header['height'], up=up)
        if self.benchmark:
            diff = time.perf_counter() - now
            self.total_time += diff
            print('Ellapsed simple filter inversion time: %.2f sec' % diff)
        if self.log_data:
            print(self.original_data)

    def apply_inverse_simplified_paeth_filter(self):
        if self.benchmark:
            now = time.perf_counter()
            print('Applying inverse simple Paeth filter...')
        self.original_data = paeth.invert_simplified_paeth_filter(self.original_data, self.header['width'], self.header['height'])
        if self.benchmark:
            diff = time.perf_counter() - now
            self.total_time += diff
            print('Ellapsed inverse simple Paeth filtering time: %.2f sec' % diff)
        if self.log_data:
            print(self.original_data)

    def write_in_file(self, show_image=False):
        output_file_name = self.input_file_path.split('/')[::-1][0].split('.')[0] + self.FILE_EXTENSION
        self.original_data = np.reshape(np.array(self.original_data).astype(np.uint8), (self.header['width'],  self.header['height']))
        image = Image.fromarray(self.original_data, 'L')
        if show_image:
            Image._show(image)
        if self.benchmark:
            print('Writing in file %s...' % output_file_name)
        image.save(self.output_file_path + output_file_name)

    def toggle_benchmark(self):
        self.benchmark = not self.benchmark

    def toggle_log_data(self):
        self.log_data = not self.log_data

    def get_compressed_data(self):
        return self.compressed_data

    def get_original_data(self):
        return self.original_data

