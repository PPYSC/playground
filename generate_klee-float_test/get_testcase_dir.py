import os
import re


def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        print(f"== Success: New folder {path} == ")
        return True
    else:
        print(f"== Failed: Folder {path} already exists ==")
        return False


IN_DIR = f"./test_in/"

gcov_test_dirs = os.listdir(IN_DIR)

for gcov_test_dir in gcov_test_dirs:
    if os.path.isdir(IN_DIR + "/" + gcov_test_dir):
        if mkdir(IN_DIR + "/" + gcov_test_dir + "/queue"):
            file = open(IN_DIR + "/" + gcov_test_dir + "/testcases", "r")
            file_str = file.read()
            testcase_list = file_str.split("()")

            for index, testcase in enumerate(testcase_list):
                testcase = testcase.strip()
                object_str_list = re.findall(r"object\s\s\s\s\d:\sdata:.*", testcase)
                object_list = [s[20:-1].encode(encoding='utf-8') for s in object_str_list]

                file = open(IN_DIR + "/" + gcov_test_dir + "/queue/" + str(index), "wb")
                for obj in object_list:
                    file.write(obj)
                    file.write(b" ")
                file.close()
