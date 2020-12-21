import numpy as np


def lzw_encode(data, limit=4096, reset_dictionary=False):
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
    dict_size = 256
    entries = {i: (i,) for i in range(dict_size)}
    decoded = list()
    current = (encoded_data[0], )
    encoded_data = np.delete(encoded_data, 0)
    decoded.append(entries[current[0]][0])
    for symbol in encoded_data:
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
    return decoded