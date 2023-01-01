import csv
import string

import subprocess
import os

import pandas as pd

if __name__ == "__main__":
    
    run_tests_switch = True
    num_of_test_runs = 10
    files = []
    simd_sizes = [1, 2, 4, 8]

    #index (ID) of categories (inclusive)
    category_sep_indexes = [6, 15, 38, 999] # => 0-5, 6-14, 15-37, 36-end(44)

    final_path = "charon/"
    base_path = "/home/vic/Documents/"
    current_path = base_path + "bparser/"
    old_path = base_path + "bparser_preVCL/"
    t_path = base_path + "bparser_tests/tests/"
    tests_path = t_path + final_path
    res_path = base_path + "bparser_tests/results/"
    results_path = res_path + final_path
    if (not os.path.isdir(t_path)):
           os.mkdir(t_path)
    if (not os.path.isdir(tests_path)):
        os.mkdir(tests_path)
    if (not os.path.isdir(res_path)):
           os.mkdir(res_path)
    if (not os.path.isdir(results_path)):
           os.mkdir(results_path)


    if run_tests_switch:
        for i in range(num_of_test_runs):
            for simd_size in simd_sizes:
                #BParser with
                cprocess = subprocess.run(["./test_speed_parser_bin", f"test_parser{i}_simd{simd_size}.csv", str(simd_size)], cwd=os.path.join(current_path, "build"), )  # dokáže zavolat gcc nebo mělo by i make
                os.replace(os.path.join(current_path, "build", f"test_parser{i}_simd{simd_size}.csv"), os.path.join(tests_path, f"test_parser{i}_simd{simd_size}.csv"))

                files.append(os.path.join(tests_path, f"test_parser{i}_simd{simd_size}.csv"))

            # BParser old
            cprocess = subprocess.run(["./test_speed_parser_bin", f"test_parser_old{i}.csv"],
                                      cwd=os.path.join(old_path,
                                                       "build"), )  # dokáže zavolat gcc nebo mělo by i make
            os.replace(os.path.join(old_path, "build", f"test_parser_old{i}.csv"),
                           os.path.join(tests_path,  f"test_parser_old{i}.csv"))

            files.append(os.path.join(tests_path, f"test_parser_old{i}.csv"))

            #C++
            cprocess = subprocess.run(["./test_speed_cpp_bin", f"test_cpp{i}.csv"], cwd=os.path.join(current_path, "build"), )  # dokáže zavolat gcc nebo mělo by i make
            os.replace(os.path.join(current_path, "build", f"test_cpp{i}.csv"), os.path.join(tests_path, f"test_cpp{i}.csv"))

            files.append(os.path.join(tests_path,  f"test_cpp{i}.csv"))


    if not files:
        for file in os.listdir(tests_path):
            if file.endswith(".csv"):
                files.append(file)
