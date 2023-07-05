import os
from time import sleep


def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        print(f"== Success: New folder {path} == ")
        return True
    else:
        print(f"== Failed: Folder {path} already exists ==")
        return False


def generate_test(conf):
    func_file = conf["func_file"]  # 被测函数所在文件
    func_name = conf["func_name"]  # 被测函数名称
    test_time = conf["test_time"]
    func_type = conf[
        "func_type"]  # 被测函数的参数类型：1.参数为 (double) ；2. 参数为 (double, double) ；3. 参数为 (double, *double)；4. 解决 __ieee754_rem_pio2 数组越界的特殊方法
    save_path = conf["save_path"]  # 存放测试单元的路径

    fdlibm_path = conf["fdlibm_path"]  # 被测静态库的路径，没有编译
    klee_path = conf["klee_path"]

    unit_path = save_path + "/" + f"{func_file}:{func_name}"

    if mkdir(unit_path):

        # copy file
        files = os.listdir(fdlibm_path)
        for file in files:
            if file.endswith(".c") or file.endswith(".h"):
                os.system(f"cp {fdlibm_path}/{file} {unit_path}/{file}")

        # write main.c
        main_file = open(f"{unit_path}/main.c", 'w')

        if func_type == 1:
            main_str = f"#include \"fdlibm.h\"\n\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tdouble x = 0;\n\tklee_make_symbolic(&x, sizeof(x), \"x\");\n\t{func_name}(x);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        elif func_type == 2:
            main_str = f"#include \"fdlibm.h\"\n\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tdouble x = 0;\n\tdouble y = 0;\n\tklee_make_symbolic(&x, sizeof(x), \"x\");\n\tklee_make_symbolic(&y, sizeof(y), \"y\");\n\t{func_name}(x,y);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        elif func_type == 3:
            main_str = f"#include \"fdlibm.h\"\n\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tdouble x = 0;\n\tdouble y = 0;\n\tklee_make_symbolic(&x, sizeof(x), \"x\");\n\tklee_make_symbolic(&y, sizeof(y), \"y\");\n\t{func_name}(x,&y);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        elif func_type == 4:
            main_str = f"#include \"fdlibm.h\"\n\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tdouble x = 0;\n\tdouble y = 0;\n\tdouble z = 0;\n\tklee_make_symbolic(&x, sizeof(x), \"x\");\n\tklee_make_symbolic(&y, sizeof(y), \"y\");\n\tklee_make_symbolic(&z, sizeof(z), \"z\");\n\tdouble array[2] = {{y, z}};\n\t{func_name}(x,array);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        else:
            main_str = ""

        main_file.write(main_str)
        print(f"== Success: Main file {unit_path}/main.c == ")

        # write run.sh
        run_str = f"export PATH={klee_path}:$PATH\n" \
                  f"clang -emit-llvm -c *.c\n" \
                  f"llvm-link *.bc -o app.bc\n" \
                  f"timeout {test_time} /usr/bin/time -f \"real time: %E\" -o time.txt klee --only-output-states-covering-new --libc=uclibc app.bc\n" \
                  f"ktest-tool klee-last/*.ktest > testcases\n"

    run_file = open(unit_path + "/run.sh", 'w')
    run_file.write(run_str)
    print(f"== Success: New file {unit_path + '/run.sh'} ==")


def do_test(conf):
    func_file = conf["func_file"]  # 被测函数所在文件
    func_name = conf["func_name"]  # 被测函数名称

    save_path = conf["save_path"]  # 存放测试单元的路径

    unit_path = save_path + "/" + f"{func_file}:{func_name}"

    os.system(f"cd {unit_path} && chmod +x run.sh && ./run.sh")


def run_many(csv_path, save_path, fdlibm_path, klee_path):
    file = open(csv_path, "r")
    for line in file.readlines():
        strl = line.split(",")
        conf = {
            "func_file": strl[0],
            "func_name": strl[1],
            "func_type": int(strl[2]),
            "test_time": float(strl[3]),
            "save_path": save_path,
            "fdlibm_path": fdlibm_path,
            "klee_path": klee_path,
        }
        generate_test(conf)
        do_test(conf)


# start
run_many("./afl_func_time_new.csv", "/home/ppy/klee-float_test/klee-float_unit",
         "/home/ppy/klee-float_test/fdlibm", "/home/ppy/klee-float/build/bin")
