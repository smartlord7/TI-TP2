from source_code.cmp.modules.util import entropy as ec
import matplotlib.image as img
import os


#region Constants

GROUP_SIZE = 2
FILES_DIR = '../resources/images/decompressed/original/'
TICKS_SIZE = 10

#endregion Constants

#region Public Functions


def analyse_files(files_dir):
    """
    Function for testing purposes. The files in the specified folder (.bmp images)
    will be analysed in order to retrieve their base entropy and their entropy assuming groups of two symbols.
    :param files_dir: the directory in which the .bmp images are.
    :return:
    """
    for subdir, dirs, files in os.walk(files_dir):
        for file in files:
            if file.endswith('.bmp'):
                print('%s: ' % file)
                image_data = img.imread(files_dir + file)
                image_data = image_data.ravel()
                alphabet = ec.gen_alphabet(image_data)

                histogram = ec.gen_histogram(image_data, len(alphabet))
                histogram_pairs, num_groups = ec.gen_histogram_generic(image_data, GROUP_SIZE)
                ec.plot_histogram(alphabet, histogram, file, TICKS_SIZE)

                print('Entropy (groups of one symbol): %.4f  bits\n'
                      #'Entropy (groups of two symbols) : %.4f  bits\n'
                      % (ec.entropy(histogram, len(image_data))))
                         #ec.entropy_generic(histogram_pairs, num_groups, GROUP_SIZE)))


def main():
    """
    Driver program for testing purposes - Base entropy and entropy assuming groups of two symbols.
    """
    if __name__ == '__main__':
        analyse_files(FILES_DIR)


#endregion Public Functions

main()
