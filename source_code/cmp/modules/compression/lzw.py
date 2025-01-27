"""------------CODEC's nao destrutivos para imagens monocromaticas------------
Universidade de Coimbra
Licenciatura em Engenharia Informatica
Teoria da Informacao
Segundo ano, primeiro semestre

Origin: https://rosettacode.org/wiki/LZW_compression#Python

Couthors (edited):
João Afonso Vieira de Sousa, 2019224599, uc2019224599@student.uc.pt
José Domingos da Silva, 2018296125, uc2018296125@student.uc.pt
Sancho Amaral Simões, 2019217590, uc2019217590@student.uc.pt
Tiago Filipe Santa Ventura, 2019243695, uc2019243695@student.uc.pt

19/12/2020
---------------------------------------------------------------------------"""

from source_code.cmp.modules.filters import util
import numpy as np

#region Public Functions


def lzw_encode(data, limit=4096, reset_dictionary=False):
    """
    Function that applies LZW encoding to a certain piece of data.
    :param data: the target data.
    :param limit: the maximum number of entries in the explicit dictionary.
    :param reset_dictionary: flag that specifies if the dictionary must be resetted when the defined maximum number of entries in it is surpassed.
    :return: the LZW encoded data.
    """
    if type(data) == np.ndarray:
        data = data.ravel()
    dict_size = 256
    alphabet = {(i,): i for i in range(dict_size)}
    entries = alphabet.copy()
    current = tuple()
    encoded = list()
    counter = int()
    for symbol in data:
        #util.show_progress(counter, len(data))
        concat = current + (symbol, )
        if concat in entries:
            current += (symbol, )
        else:
            encoded.append(entries[current])
            if dict_size < limit:
                entries[concat] = dict_size
                dict_size += 1
            elif reset_dictionary:
                entries = alphabet
            current = (symbol, )
        counter += 1
    if current:
        encoded.append(entries[current])
    return encoded


def lzw_decode(encoded_data):
    """
    Function that applies LZW encoding to a certain piece of data.
    :return: the LZW decoded data.
    """
    dict_size = 256
    entries = {i: (i,) for i in range(dict_size)}
    decoded = list()
    current = (encoded_data[0], )
    encoded_data = np.delete(encoded_data, 0)
    decoded.append(entries[current[0]][0])
    counter = int()
    for symbol in encoded_data:
        # util.show_progress(counter, len(data))
        if entries.get(symbol):
            entry = entries[symbol]
        elif symbol == dict_size:
            entry = current + (current[0], )
        else:
            raise ValueError('Bad LZW compressed: %s!' % symbol)
        for decoded_symbol in entry:
            decoded.append(decoded_symbol)
        entries[dict_size] = current + (entry[0], )
        dict_size += 1
        current = entry
        counter += 1
    return decoded


#endregion Public Functions