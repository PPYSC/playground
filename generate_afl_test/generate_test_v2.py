import os
from time import sleep

"""
README：

（直接写在这里了）

关于本脚本：
    1. 本脚本会在指定目标路径下生成名为 "{被测函数名称}=={测试时间（秒）}" 的文件夹，里面是对应的测试单元。
    
    2. 被测函数的参数类型：1.参数为 (double) ；2. 参数为 (double, double) ；3. 参数为 (double, *double)；4. 解决 __ieee754_rem_pio2 数组越界的特殊类型
    
    3. fuzz结果存在对应测试单元目录下的 ./fuzz-out 目录中


# 此处开始介绍使用方法示例代码，路径是我自己的环境cd ..

conf_list = []  # 配置列表

conf_example = {
    "func_name": "__ieee754_acos",  # 被测函数名称
    "func_type": 1,
    # 被测函数的参数类型：1.参数为 (double) ；2. 参数为 (double, double) ；3. 参数为 (double, *double)；4. 解决 __ieee754_rem_pio2 数组越界的特殊方法
    "test_time": 60,  # 测试时间，单位为秒
    "save_path": "/home/ppy/wk/afl/afl_test",  # 存放测试单元的路径
    "fdlibm_path": "/home/ppy/wk/afl/fdlibm",  # 被测静态库的路径，需要预先使用afl-gcc编译
    "afl_path": "/home/ppy/wk/afl/afl-2.52b",  # afl的路径
}

conf_list.append(conf_example)

for conf in conf_list:
    generate_test(conf)  # 调用 generate_test() 生成测试单元
    do_test(conf)        # 调用 do_test() 执行测试
    
  
特别注意：
    1. 在进行测试前，fdlibm 需要修改其 makefile ，使用afl-gcc进行编译，得到的 libm.a 应该默认存储在 fdlibm 的路径下
    
    2. 本脚本生成的测试单元中，所有的测试种子都是 "aaaaaa" 按情况可以在 generate_test() 中修改
    
    3. 如果同时运行多个fuzz，可能会导致cpu资源不足，进而使测试的运行时间上限失效。由于总体运行时间不长，本脚本将顺序运行单个测试而不考虑并行。


我自己简单测了下:
    1. 当参数类型为1和2时，我随便测的几个函数是没有问题的

    2. 当参数类型为3时， __ieee754_rem_pio2 出现问题，但其实类型3还只剩下 modf ，测了没问题
    
    3. 发现 __ieee754_rem_pio2 存在数组越界问题，我看了代码以后改了 main 函数，称其为类型4。
    

其他：
    1. 本来想加上tqdm

"""


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
    func_name = conf["func_name"]  # 被测函数名称
    func_type = conf[
        "func_type"]  # 被测函数的参数类型：1.参数为 (double) ；2. 参数为 (double, double) ；3. 参数为 (double, *double)；4. 解决 __ieee754_rem_pio2 数组越界的特殊方法
    test_time = conf["test_time"]  # 测试时间，单位为秒
    save_path = conf["save_path"]  # 存放测试单元的路径

    fdlibm_path = conf["fdlibm_path"]  # 被测静态库的路径，需要预先使用afl-gcc编译
    afl_path = conf["afl_path"]  # afl的路径
    cc_name = conf["cc_name"]  # 比去年一起名称

    test_path = save_path + "/" + f"{func_name}=={test_time}"

    if mkdir(test_path):
        # mkdir fuzz_in
        mkdir(test_path + "/fuzz_in")
        if func_type == 1:
            testcase_str = "0.123456"
        elif func_type == 2 or 3:
            testcase_str = "12345.06789 987.0654321"
        elif func_type == 4:
            testcase_str = "12345.06789 987.0654321 5.23467819"
        else:
            testcase_str = "0.123456"
        testcase_file = open(test_path + "/fuzz_in/testcase", 'w')
        testcase_file.write(testcase_str)
        print(f"== Success: New file {test_path + '/fuzz_in/testcase'} == ")

        # mkdir fuzz_out
        mkdir(test_path + "/fuzz_out")

        # write main.c
        if func_type == 1:
            main_str = f"#include \"{fdlibm_path + '/fdlibm.h'}\"\n\n#include <stdio.h>\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tFILE *f = fopen(argv[1], \"r\");\n\tdouble x = 0;\n\tfscanf(f, \"%lf\", &x);\n\t{func_name}(x);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        elif func_type == 2:
            main_str = f"#include \"{fdlibm_path + '/fdlibm.h'}\"\n\n#include <stdio.h>\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tFILE *f = fopen(argv[1], \"r\");\n\tdouble x = 0;\n\tdouble y = 0;\n\tfscanf(f, \"%lf %lf\", &x, &y);\n\t{func_name}(x,y);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        elif func_type == 3:
            main_str = f"#include \"{fdlibm_path + '/fdlibm.h'}\"\n\n#include <stdio.h>\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tFILE *f = fopen(argv[1], \"r\");\n\tdouble x = 0;\n\tdouble y = 0;\n\tfscanf(f, \"%lf %lf\", &x, &y);\n\t{func_name}(x,&y);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        elif func_type == 4:
            main_str = f"#include \"{fdlibm_path + '/fdlibm.h'}\"\n\n#include <stdio.h>\n// LCOV_EXCL_START\nint main(int argc, char *argv[])\n{{\n\tFILE *f = fopen(argv[1], \"r\");\n\tdouble x = 0;\n\tdouble y[2] = {{0, 0}};\n\tfscanf(f, \"%lf %lf %lf\", &x, &y[0], &y[1]);\n\t{func_name}(x,y);\n\treturn 0;\n}}\n// LCOV_EXCL_STO\n"
        else:
            main_str = ""
        main_file = open(test_path + "/main.c", 'w')
        main_file.write(main_str)
        print(f"== Success: New file {test_path + '/main.c'} == ")

        # write makefile
        makefile_str = f"CFLAGS = -D_IEEE_LIBM\n\nCC = {afl_path + '/' + cc_name}\n\nLIBM = {fdlibm_path + '/libm.a'}\n\nsrc = main.c\n\nobj = main.o\n\nall: $(obj)\n\t$(CC) -o main $(obj) $(LIBM)\n\nclean: \n\t/bin/rm -f $(obj) main\n"
        makefile_file = main_file = open(test_path + "/makefile", 'w')
        makefile_file.write(makefile_str)
        print(f"== Success: New file {test_path + '/makefile'} == ")

        # write run.sh
        run_str = f"make && timeout {test_time + 5} {afl_path}/afl-fuzz -i ./fuzz_in -o ./fuzz_out ./main @@ > log.txt &\n"  # 由于afl启动fuzz的时间为固定5s，故加上
        run_file = open(test_path + "/run.sh", 'w')
        run_file.write(run_str)
        print(f"== Success: New file {test_path + '/run.sh'} == ")


def do_test(conf):
    func_name = conf["func_name"]  # 被测函数名称

    test_time = conf["test_time"]  # 测试时间，单位为秒
    save_path = conf["save_path"]  # 存放测试单元的路径

    test_path = save_path + "/" + f"{func_name}=={test_time}"

    os.system(f"cd {test_path} && chmod +x run.sh && ./run.sh")
    sleep(test_time + 15)  # afl启动fuzz的时间为固定5s，加上为编译等操作预留时间10s


def run_many(csv_path, save_path, fdlibm_path, afl_path, cc_name):
    file = open(csv_path, "r")
    for line in file.readlines():
        strl = line.split(",")
        conf = {
            "func_name": strl[0],
            "func_type": int(strl[1]),
            "test_time": int(strl[2]),
            "save_path": save_path,
            "fdlibm_path": fdlibm_path,
            "afl_path": afl_path,
            "cc_name": cc_name,
        }
        generate_test(conf)
        do_test(conf)


def run_one(func_name, func_type, test_time, save_path, fdlibm_path, afl_path, cc_name):
    conf = {
        "func_name": func_name,
        "func_type": func_type,
        "test_time": test_time,
        "save_path": save_path,
        "fdlibm_path": fdlibm_path,
        "afl_path": afl_path,
        "cc_name": cc_name,
    }
    generate_test(conf)
    do_test(conf)


# start
run_many("../afl_func_time.csv", "/home/ppy/wk/afl/afl_gcc/afl_test", "/home/ppy/wk/afl/afl_gcc/fdlibm",
         "/home/ppy/wk/afl/afl_gcc/AFLplusplus", "afl-gcc")
