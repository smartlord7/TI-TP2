from source_code.cmp.modules.compression import rle

#region Public Functions


def main():
    """
    Driver program for testing purposes - Run Length Encoding.
    """
    if __name__ == '__main__':
        string = [1, 2, 3, 1, 2, 1, 1, 1, 1, 2, 3, 2, 1, 2, 3, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4]
        encoded = rle.rle_encode(string)
        print(encoded)
        decoded = rle.rle_decode(encoded)
        print(decoded)


#endregion Public Functions

main()


