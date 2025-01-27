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

import source_code.cmp.modules.filters.util as util
import numpy as np

#region Public Functions


def apply_simple_filter(data, up=False):
    """
    Function that applies Sub/Up Filter in a given piece of data.
    :param data: the data to be filtered.
    :param up: flag that indicates if the Up Filter must be used instead of the Sub Filter.
    :return: the filtered data.
    """
    data = util.to_numpy_uint8(data)
    if up:
        data = np.transpose(data)
    data = data.ravel()#.astype(np.int16)
    return np.concatenate(([data[0]], np.diff(data)))


def invert_simple_filter(data, width, height, up=False):
    """
    Function that applies Inverse Sub/Up Filter in a given piece of data.
    :param data: the data to be unfiltered.
    :param up: flag that indicates if the Up Filter was used instead of the Sub Filter.
    :return: the unfiltered data.
    """
    data = np.cumsum(data).astype(np.uint8)#.astype(np.int16)
    if up:
        return np.transpose(data.reshape((height, width)))
    return data.reshape((width, height))


#endregion Public Functions