import os
import re

# TODO


IN_DIR = f"/root/afl_test/afl_epp_path/test_epp_path"

OUT_FILE = f"/root/afl_test/afl_epp_path/cov_rst.csv"

gcov_test_dirs = os.listdir(IN_DIR)
for gcov_test_dir in gcov_test_dirs:
    if os.path.isdir(IN_DIR + "/" + gcov_test_dir):
        os.system(f"cd {IN_DIR + '/' + gcov_test_dir} && chmod +x ./run.sh")
