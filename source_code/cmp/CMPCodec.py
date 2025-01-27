"""------------CODEC's nao destrutivos para imagens monocromaticas------------
Universidade de Coimbra
Licenciatura em Engenharia Informatica
Teoria da Informacao
Segundo ano, primeiro semestre

Authors:
João Afonso Vieira de Sousa, 2019224599, uc2019224599@student.uc.pt
José Domingos da Silva, 2018296125, uc2018296125@student.uc.pt
Sancho Amaral Simões, 2019217590, uc2019217590@student.uc.pt
Tiago Filipe Santa Ventura, 2019243695, uc2019243695@student.uc.pt

19/12/2020
---------------------------------------------------------------------------"""
from source_code.cmp.modules.compression.huffmancodec import HuffmanCodec, _EndOfFileSymbol
from source_code.cmp.modules.compression import lzw as lzw, rle as rle, lzma as lzma
from source_code.cmp.modules.filters import subup as sub, paeth as paeth
from source_code.cmp.modules.transforms import mtf as mtf
import source_code.cmp.modules.util.file_rw as frw
import matplotlib.image as img
from PIL import Image
import numpy as np
import time
import os


class InvalidFileExtensionError(Exception):
    """
    Exception raised when trying to compress an image without .bmp extension.
    """
    pass


class CMPBenchmarker():
    """
       Base class for CMP compression benchmarking/logging utilities.
    """

    #region Constructors

    def __init__(self, input_file_path, output_file_path, benchmark, log_data):
        self._input_file_path = input_file_path
        self._output_file_path = output_file_path
        self._file_name = self._input_file_path.split('/')[::-1][0]
        self._benchmark = benchmark
        self._log_data = log_data
        self._total_time = int()
        self._successful = False
        self._log_file_text = str()
        self._log_file_suffix = '_log.txt'


    #endregion Constructors

    #region Public Functions

    def output_log(self):
        """
        Function that writes the compression/decompression log information into a .txt file if the compression/decompression has successfully occurred.
        :return:
        """
        if self._successful:
            with open(self._output_file_path + self._file_name.split('.')[0] + self._log_file_suffix, 'w') as log_file:
                log_file.write(self._log_file_text)

    def toggle_benchmark(self):
        """
        Function that allows toggling the exhibition of compression/decompression step durations.
        :return:
        """
        self._benchmark = not self._benchmark

    def toggle_log_data(self):
        """
        Function that allows toggling the data's exhibition in each step.
        :return:
        """
        self._log_data = not self._log_data

    #endregion Public Functions


class CMPCompressor(CMPBenchmarker):

    """
    Class that encapsulates the information and functionalities of a custom .bmp compressor. The functions applied can be interchangeable
    in order to test different combinations of compression algorithms.
    """

    #region Constants

    INITIAL_ALPHABET_LENGTH = 256
    ESCAPE_CHARACTER = -256
    EOF_SYMBOL = _EndOfFileSymbol()
    FILE_EXTENSION = '.cmp'
    ALPHABET = [i for i in range(256)]

    #endregion Constants

    #region Constructors

    def __init__(self, input_file_path, output_file_path, benchmark=False, log_data=False):
        """
        BMPCompressor Constructor.
        :param input_file_path: the target file absolute/relative path.
        :param output_file_path: the output file absolute/relative path.
        :param benchmark: flag that toggles data exhibition about compression in each step.
        :param log_data: flag that toggles the compressed data exhibition in each step.
        """
        super(CMPCompressor, self).__init__(input_file_path, output_file_path, benchmark, log_data)

        self._log_file_suffix = '_cmp' + self._log_file_suffix

        if not input_file_path.endswith('.bmp'):
            raise InvalidFileExtensionError

        matrix_data = img.imread(input_file_path)

        if len(matrix_data.shape) == 3:
            matrix_data = matrix_data[:, :, 0]

        if log_data:
            print(matrix_data)

        self.__image_width = matrix_data.shape[0]
        self.__image_height = matrix_data.shape[1]
        self.__original_data = matrix_data
        self.__compressed_data = self.__original_data
        self.__encoding_table = None
        self.__rle = False
        self._log_file_text = '-------%s CMP COMPRESSION LOG-------\n\n'\
                            'COMPRESSION STACK: \n' % self._file_name

    #endregion Constructors

    #region Public Functions

    def apply_simple_filter(self, up=True):

        """
        Function that applies Sub Filter (Delta Encoding) or Up Filter to the target data.
        :param up: flag that allows the usage of Up Filter instead of Sub filter (both filters are performed in the same function).
        :return:
        """

        if up:
            self._log_file_text += ' -> UP FILTER\n'
        else:
            self._log_file_text += ' -> SUB FILTER\n'

        now = time.perf_counter()

        if self._benchmark:
            if up:
                print('Applying up filter...')
            else:
                print('Applying sub filter...')

        self.__compressed_data = sub.apply_simple_filter(self.__compressed_data, up=up)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            if up:
                print('Ellapsed up filtering time: %.2f sec' % diff)
            else:
                print('Ellapsed sub filtering time: %.2f sec' % diff)

        if self._log_data:
            print(self.__compressed_data)

    def apply_simplified_paeth_filter(self):

        """
        Function that applies the simplified version of Paeth filter to the target data.
        Example:
        B C         B - upper left pixel    P = A + C - B
        A X         C - above pixel         X' = X - P
                    A - previous pixel
                    X - current pixel
                    X' - filtered pixel
        :return:
        """

        self._log_file_text += ' -> SIMPLE PAETH FILTER\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying simple Paeth filter...')

        self.__compressed_data = paeth.apply_simplified_paeth_filter(self.__compressed_data, self.__image_width, self.__image_height)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed simple Paeth filtering time: %.2f sec' % diff)

        if self._log_data:
            print(self.__compressed_data)

    def apply_mtf(self):
        """
        Function that applies the Move To Front Transform (MTF) to the target data.
        Example:

        S = [1, 2, 3, 2, 3, 1]      A = [1, 2, 3]   S - target data
        S'= []                                      A - initial symbol list

        1. S' = [0]                     A = [1, 2, 3]
        2. S' = [0, 1]                  A = [2, 1, 3]
        3. S' = [0, 1, 2]               A = [3, 2, 1]
        4. S' = [0, 1, 2, 1]            A = [2, 3, 1]
        5. S' = [0, 1, 2, 1, 1]         A = [3, 2, 1]
        6. S' = [0, 1, 2, 1, 1, 2]      A = [1, 2, 3]

        :return:
        """
        self._log_file_text += ' -> MTF\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying MTF...')

        self.__compressed_data = np.array(mtf.apply_mtf(np.array(self.__compressed_data).ravel(), self.ALPHABET))

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed MTF encoding time: %.2f sec' % diff)

        if self._log_data:
            print(self.__compressed_data)

    def apply_rle(self):
        """
        Function that applies Run-Length-Encoding (RLE) to the target data.
        Example:

        S = [1, 1, 1, 1, 1, 2, 3, 2, 2, 2, 2, 2]    S - target data
        E = -1                                      E - escape character
                                                    S' - encoded data
        S' = [-1, 1, 5, 2, 3, -1, 2, 5]

        :return:
        """
        self.__rle = True

        self._log_file_text += ' -> RLE\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying RLE encoding...')

        self.__compressed_data = np.array(rle.rle_encode(np.array(self.__compressed_data).ravel(), self.ESCAPE_CHARACTER)).astype(np.int16)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed RLE encoding time: %.2f sec' % diff)

        if self._log_data:
            print(self.__compressed_data)

    def apply_lzw(self, max_size, reset_dict):
        """
        Function that applies Lempel-Ziv-Whelch (LZW) to the target data (variation of LZ dictionary compression methods).
        :return:
        """
        self._log_file_text += ' -> LZW WITH DICT MAX SIZE OF %d' % max_size

        if reset_dict:
            self._log_file_text += ' AND WITH DICT RESET\n'
        else:
            self._log_file_text += ' AND WITHOUT DICT RESET\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying LZW encoding...')

        self.__compressed_data = np.array(lzw.lzw_encode(self.__compressed_data, limit=max_size,
                                                         reset_dictionary=reset_dict))

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed LZW encoding time: %.2f sec' % diff)

        if self._log_data:
            print(self.__compressed_data)

    def apply_lzma(self):
        """
        Function that applies Lempel-Ziv-Markov (LZMA) to the target data (variation of LZ dictionary compression methods).
        :return:
        """
        self._log_file_text += ' -> LZMA\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying LZMA encoding...')

        compressor = lzma.LZMACompressor(format=lzma.FORMAT_RAW, filters=[{'id':lzma.FILTER_LZMA2}])
        self.__compressed_data = compressor.compress(bytearray(np.array(self.__compressed_data))) + compressor.flush()

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed LZMA encoding time: %.2f sec' % diff)

        if self._log_data:
            print(self.__compressed_data)

    def apply_huffman_encoding(self):
        """
        Function that applies Huffman Encoding to the target data (entropic encoder).
        :return:
        """
        self._log_file_text += ' -> HUFFMAN ENCODING\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying Huffman encoding...')

        self.__compressed_data = np.concatenate((self.__compressed_data, [self.EOF_SYMBOL]))
        self.__encoding_table = HuffmanCodec.from_data(self.__compressed_data).get_code_table()
        self.__compressed_data = frw.encode(self.__compressed_data, self.__encoding_table, eof_symbol=self.EOF_SYMBOL)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed huffman encoding time: %.2f sec' % diff)

        if self._log_data:
            print(self.__compressed_data)

    def write_in_file(self):
        """
        Function that writes the compressed image into a .cmp file and the log information into a .txt file.
        :return:
        """
        output_file_name = self._file_name.split('.')[0] + self.FILE_EXTENSION

        if self._benchmark:
            print('Total ellapsed compression time: %.2f sec' % self._total_time)
            print('Writing in file %s...' % output_file_name)

        frw.write_file(self._output_file_path + output_file_name, self.__compressed_data,
                       self.__build_cmp_header())

        initial_size, compressed_size = os.path.getsize(self._input_file_path), os.path.getsize(self._output_file_path + output_file_name)
        compression_ratio = (initial_size - compressed_size) / initial_size * 100
        self._log_file_text += '\nTOTAL ELLAPSED COMPRESSION TIME: %.2f sec.\n'\
                                'INITIAL IMAGE SIZE: %d bytes\n'\
                                'COMPRESSED IMAGE SIZE: %d bytes\n'\
                                'COMPRESSION RATIO: %.2f%%\n' % (self._total_time, initial_size, compressed_size, compression_ratio)

        self._successful = True

    #endregion Public Functions

    #region Private Functions

    def __build_cmp_header(self):
        """
        Function that builds the header (a dictionary) to be used in the compressed files (.cmp).
        :return:
        """
        header = {
                'size': self.__image_width * self.__image_height,
                'width': self.__image_width,
                'height': self.__image_height,
                'rle': self.__rle
            }
        if self.__encoding_table:
            header['encoding_table'] = self.__encoding_table
        return header

    #endregion Private Functions


class CMPDecompressor(CMPBenchmarker):
    """
    Class that encapsulates the information and functionalities of a custom .bmp decompressor. The functions applied must be in the same order as the one
    used while using BMPCompressor so the file is correctly decompressed.
    """

    #region Constants

    EOF_SYMBOL = _EndOfFileSymbol()
    ESCAPE_CHARACTER = -256
    FILE_EXTENSION = '.bmp'
    ALPHABET = [i for i in range(256)]

    #endregion Constants

    #region Constructors

    def __init__(self, input_file_path, output_file_path, benchmark=False, log_data=False):
        """
        BMPDecompressor Constructor.
        :param input_file_path: the target file absolute/relative path.
        :param output_file_path: the output file absolute/relative path.
        :param benchmark: flag that toggles compression data exhibition in each step.
        :param log_data: flag that toggles the uncompressed data exhibition in each step.
        """

        super(CMPDecompressor, self).__init__(input_file_path, output_file_path, benchmark, log_data)

        self._log_file_suffix = '_dcmp' + self._log_file_suffix

        if not input_file_path.endswith('cmp'):
            raise InvalidFileExtensionError

        self.__header, self.__compressed_data = frw.read_file(input_file_path)

        if log_data:
            print(self.__compressed_data)

        self.__original_data = self.__compressed_data

        self._log_file_text = '-------%s CMP DECOMPRESSION LOG-------\n\n'\
                                'DECOMPRESSION STACK: \n' % self._file_name

    #endregion Constructors

    #region Public Functions

    def apply_inverse_huffman_encoding(self):
        """
        Function that performs huffman decoding on the target data.
        :return:
        """
        self._log_file_text += ' -> INVERSE HUFFMAN ENCODING\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying inverse Huffman Encoding...')

        self.__original_data = frw.decode(self.__original_data, self.__header['encoding_table'], self.EOF_SYMBOL)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed huffman encoding inversion time: %.2f sec' % diff)

        if self._log_data:
            print(self.__original_data)

    def apply_inverse_rle(self):
        """
        Function that performs RLE decoding on the target data.
        :return:
        """
        self._log_file_text += ' -> INVERSE RLE\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying inverse RLE...')

        self.__original_data = np.array(rle.rle_decode(self.__original_data, self.ESCAPE_CHARACTER))

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed RLE inversion time: %.2f sec' % diff)

        if self._log_data:
            print(self.__original_data)

    def apply_inverse_lzw(self):
        """
        Function that performs LZW decoding on the target data.
        :return:
        """
        self._log_file_text += ' -> INVERSE LZW\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying inverse LZW Encoding ...')

        self.__original_data = np.array(lzw.lzw_decode(self.__original_data))

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed inverse LZW Encoding time: %.2f sec' % diff)

        if self._log_data:
            print(self.__original_data)

    def apply_inverse_lzma(self):
        """
        Function that performs LZMA decoding on the target data.
        :return:
        """
        self._log_file_text += ' -> INVERSE LZMA\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying inverse LZMA Encoding ...')

        decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[{'id':lzma.FILTER_LZMA2}])
        if self.__header['rle']:
            self.__original_data = np.frombuffer(decompressor.decompress(self.__original_data), dtype=np.int16)
        else:
            self.__original_data = np.frombuffer(decompressor.decompress(self.__original_data), dtype=np.uint8)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed inverse LZMA Encoding time: %.2f sec' % diff)

        if self._log_data:
            print(self.__original_data)

    def apply_inverse_mtf(self):
        """
        Function that performs inverse MTF on the target data.
        :return:
        """
        self._log_file_text += ' -> INVERSE MTF\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying Inverse MTF...')

        self.__original_data = np.array(mtf.invert_mtf(self.__original_data, self.ALPHABET)).astype(np.uint8)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed MTF inversion time: %.2f sec' % diff)

        if self._log_data:
            print(self.__original_data)

    def apply_inverse_simple_filter(self, up):
        """
        Function that performs the inversion of Up/Sub filter on the target data.
        :return:
        """
        if up:
            self._log_file_text += ' -> INVERSE UP FILTER\n'
        else:
            self._log_file_text += ' -> INVERSE SUB FILTER\n'

        now = time.perf_counter()

        if self._benchmark:
            print('Applying inverse simple filter...')

        self.__original_data = sub.invert_simple_filter(self.__original_data, self.__header['width'], self.__header['height'], up=up)

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed simple filter inversion time: %.2f sec' % diff)

        if self._log_data:
            print(self.__original_data)

    def apply_inverse_simplified_paeth_filter(self):
        """
        Function that performs the inversion of Paeth filter on the target data.
        :return:
        """
        self._log_file_text += ' -> INVERSE SIMPLE PAETH FILTER\n'

        now = time.perf_counter()
        if self._benchmark:
            print('Applying inverse simple Paeth filter...')

        self.__original_data = paeth.invert_simplified_paeth_filter(self.__original_data, self.__header['width'], self.__header['height'])

        diff = time.perf_counter() - now
        self._total_time += diff

        if self._benchmark:
            print('Ellapsed inverse simplified Paeth filtering time: %.2f sec' % diff)

        if self._log_data:
            print(self.__original_data)

    def write_in_file(self, show_image=False):
        """
        Function that writes the uncompressed image into a .bmp file and the uncompression log information into a .txt file.
        :return:
        """
        self.__original_data = np.reshape(np.array(self.__original_data).astype(np.uint8), (self.__header['width'], self.__header['height']))
        image = Image.fromarray(self.__original_data, 'L')

        if show_image:
            Image._show(image)

        output_file_name = self._input_file_path.split('/')[::-1][0].split('.')[0] + self.FILE_EXTENSION

        self._log_file_text += '\nTOTAL ELLAPSED UNCOMPRESSION TIME: %.2f sec.\n' % self._total_time

        if self._benchmark:
            print('Writing in file %s...' % output_file_name)

        image.save(self._output_file_path + output_file_name)

        self._successful = True

    #endregion Public Functions
