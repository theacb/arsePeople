import os
import sys
import getopt
import random
import time
from PySide.QtGui import QMainWindow, QApplication, QFileDialog
from arsePeopleDialog import Ui_MainWindow


# get file list

def get_file_list(directory):
    file_name_list = next(os.walk(directory))[2]

    final_list = []

    for f in file_name_list:
        if f.endswith((".png", ".jpg", ".tga", ".tiff", ".jpeg")):
            x = ImageFile(f, 0)
            final_list.append(x)

    return final_list


# select order randomly and assign random length

def randomize_file_list(fl, min_length, max_length, list_length, seed):

    random.seed(seed)

    new_fl = []
    old_index = -1

    for j in range(0, list_length):
        if list_length > 2:
            i = randint_exclude_index(0, len(fl) - 1, old_index)
        else:
            i = random.randint(0, len(fl) - 1)

        cur_file = fl[i]
        cur_file.set_length(random.randint(min_length, max_length))
        new_fl.append(cur_file)
        old_index = i

    return new_fl


# Prevents the same random number from being returned twice in a row

def randint_exclude_index(min_rand, max_rand, i):
    a = random.randint(min_rand, max_rand)
    if a == i:
        return randint_exclude_index(min_rand, max_rand, i)
    else:
        return a


def comment_line_gen(user_seed):
    return ';Created: {0}, Seed: {1}\n'.format(time.strftime("%y%m%d-%H.%M.%S"), user_seed)


# write ifl file

def write_ifl_file(fl, directory, **kwargs):

    file_name = kwargs.get('file_name', False)
    seed = kwargs.get('seed', 'Not Defined')

    if file_name:
        name = "{0}.ifl".format(file_name)
    else:
        name = "{0}_{1}.ifl".format(time.strftime("%y%m%d%H%M%S"), fl[0].get_file_name())
    try:
        with open(os.path.join(directory, name), 'w') as f:

            f.write(comment_line_gen(seed))

            for i in fl:
                f.write("{}\n".format(str(i)))
    except IOError as e:
        print ("Encountered IOError while writing {0}: {1}".format(name, e))
        sys.exit(1)


def help_print():
    print ("** Help **")
    print ("  -d, --directory: The directory containing the images to randomize")
    return


def main(argv):
    directory = ''
    seed = None
    list_length = 10
    min_length = 5
    max_length = 15
    file_name = False

    if len(argv) > 0:
        try:
            opts, args = getopt.getopt(argv, "hd:s:l:n:m:f:",
                                       ["help", "directory=", "seed=", "list_length=",
                                        "min_length=", "max_length=", "file_name="])
        except getopt.GetoptError:
            print("Error! Run with option: -h for help")
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print (help_print())
            elif opt in ('-d', '--directory'):
                directory = arg
            elif opt in ('-s', '--seed'):
                seed = arg
            elif opt in ('-l', '--list_length'):
                list_length = arg
            elif opt in ('-n', '--min_length'):
                min_length = arg
            elif opt in ('-m', '--max_length'):
                max_length = arg
            elif opt in ('-f', '--file_name'):
                file_name = arg

        cmd_program_run(directory, min_length, max_length, list_length, seed, file_name)
    else:
        app = QApplication(argv)
        frame = MainWindow()
        frame.show()
        app.exec_()


def cmd_program_run(directory, min_length, max_length, list_length, seed, file_name):

    # A couple checks on the directory since we will probably be writing to a fickle server
    if len(directory) < 1:
        print("No directory defined!  A directory is required for the script to function")
        sys.exit(2)

    if not os.path.isdir(directory):
        print("Invalid Directory")
        sys.exit(2)

    if not os.access(directory, os.W_OK) or os.access(directory, os.X_OK):
        print ("Unable to write to directory")
        sys.exit(2)

    file_list = get_file_list(directory)

    # Check to see if there are any valid images
    if len(file_list) < 1:
        print("No Image Files found in Directory")
        sys.exit(0)

    random_file_list = randomize_file_list(file_list, min_length, max_length, list_length, seed)
    write_ifl_file(random_file_list, directory, seed=seed, file_name=file_name)
    sys.exit(0)


class ImageFile:
    def __init__(self, file_name, length):
        self.file_name = file_name
        self.length = length

    def __str__(self):
        return "{0} {1}".format(self.file_name, self.length)

    def get_file_name(self):
        return self.file_name

    def get_length(self):
        return self.length

    def set_file_name(self, x):
        self.file_name = x

    def set_length(self, x):
        self.length = x


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.applyButton.clicked.connect(self.apply)
        self.openButton.clicked.connect(self.select_folder)
        self.randrom_seed_button.clicked.connect(self.random_seed)

    def apply(self):
        directory = os.path.normpath(self.file_dialog_line_edit.text())
        seed = self.seed_spin_box.value()
        list_length = self.list_length_spin_box.value()
        min_length = self.min_length_spin_box.value()
        max_length = self.max_length_spin_box.value()
        file_name = self.name_line_edit.text()

        if self.check_dir(directory):
            if self.check_min_max(min_length, max_length):
                self.program_run(directory, min_length, max_length, list_length, seed, file_name)
        return

    def random_seed(self):
        random.seed(None)
        self.seed_spin_box.setValue(random.randint(0, 65535))

    def select_folder(self):
        selected_directory = QFileDialog.getExistingDirectory(self, caption="Select Directory")
        self.file_dialog_line_edit.setText(selected_directory)

    def program_run(self, directory, min_length, max_length, list_length, seed, file_name):
        self.stpr("Building Image List")
        file_list = get_file_list(directory)

        # Check to see if there are any valid images
        if len(file_list) < 1:
            self.stpr("No Image Files found in Directory!", True)
            return
        else:
            self.stpr("Randomizing Files")
            random_file_list = randomize_file_list(file_list, min_length, max_length, list_length, seed)

            self.stpr("Writing IFL File to Disk")
            try:
                write_ifl_file(random_file_list, directory, seed=seed, file_name=file_name)
            except IOError as e:
                self.stpr(e, True)

        self.stpr("Done!")

    def check_dir(self, directory):
        if len(directory) < 1:
            self.stpr("No directory defined!  A directory is required for the script to function", True)
            return False

        elif not os.path.isdir(directory):
            self.stpr("Invalid Directory", True)
            return False

        elif not os.access(directory, os.W_OK):
            print (directory)
            self.stpr("Unable to write to directory", True)
            return False
        else:
            return True

    def check_min_max(self, min_length, max_length):
        if min_length > max_length:
            self.stpr("The minimum frame count is greater than the maximum frame count", True)
            return False
        else:
            return True

    def stpr(self, text, error=False):
        if error:
            self.status_bar.setText("Status: <font color=red>{}</>".format(text))
        else:
            self.status_bar.setText("Status: {}".format(text))
        return


if __name__ == "__main__":
    main(sys.argv[1:])
