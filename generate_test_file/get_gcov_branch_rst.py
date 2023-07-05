import os
import re

IN_DIR = f"/home/ppy/wk/afl_gcov_branch/test_gcov_branch"

OUT_FILE = f"/home/ppy/wk/afl_gcov_branch/cov_rst.txt"

gcov_test_dirs = os.listdir(IN_DIR)
for gcov_test_dir in gcov_test_dirs:
    if os.path.isdir(IN_DIR + "/" + gcov_test_dir):
        file = open(IN_DIR + "/" + gcov_test_dir + "/cov.txt", "r")
        file_str = file.readlines()
        branch_str = file_str[2][:-1]
        branch_str_data = re.sub("Branches executed:", "", branch_str)

        percent = branch_str_data.split(" of ")[0]
        cnt = branch_str_data.split(" of ")[1]

        total_branch_cnt = int(cnt)
        hit_branch_cnt = int((float(percent[:-1]) * total_branch_cnt / 100) + 0.5)

        print(f"{gcov_test_dir}==={branch_str}==={hit_branch_cnt}={total_branch_cnt}={percent}=")

