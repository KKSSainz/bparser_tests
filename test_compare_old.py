import csv
import string

import subprocess
import os

import pandas as pd
import numpy as np
import plotly.express as px

def ratio(g):
    ratio = list(g['Time'])[0]/list(g['Time'])[1]
    return ratio



if __name__ == "__main__":

    run_tests_switch = True
    n_repeats = 500
    path = os.getcwd()
    path_parent = os.path.dirname(os.getcwd())

    num_of_test_runs = 2

    files = []

    simd_sizes = [1, 2, 4, 8]

    base_path = "/home/vic/Documents/"
    current_path = base_path + "bparser/"
    old_path = base_path + "bparser_preVCL/"

    results_path = base_path + "bparser_tests/"
    
    if (not os.path.isdir(results_path)):
        os.mkdir(results_path)

    if run_tests_switch:
        for i in range(num_of_test_runs):
            for simd_size in simd_sizes:
                #BParser with
                cprocess = subprocess.run(["./test_speed_parser_bin", f"test_parser{i}_simd{simd_size}.csv", str(simd_size)], cwd=os.path.join(current_path, "build"), )  # dokáže zavolat gcc nebo mělo by i make
                os.replace(os.path.join(current_path, "build", f"test_parser{i}_simd{simd_size}.csv"), os.path.join(results_path, f"test_parser{i}_simd{simd_size}.csv"))

                files.append(os.path.join(results_path, f"test_parser{i}_simd{simd_size}.csv"))

            # BParser old
            cprocess = subprocess.run(["./test_speed_parser_bin", f"test_parser_old{i}.csv"],
                                      cwd=os.path.join(old_path,
                                                       "build"), )  # dokáže zavolat gcc nebo mělo by i make
            os.replace(os.path.join(old_path, "build", f"test_parser_old{i}.csv"),
                           os.path.join(results_path,  f"test_parser_old{i}.csv"))

            files.append(os.path.join(results_path, f"test_parser_old{i}.csv"))

            #C++
            cprocess = subprocess.run(["./test_speed_cpp_bin", f"test_cpp{i}.csv"], cwd=os.path.join(current_path, "build"), )  # dokáže zavolat gcc nebo mělo by i make
            os.replace(os.path.join(current_path, "build", f"test_cpp{i}.csv"), os.path.join(results_path, f"test_cpp{i}.csv"))

            files.append(os.path.join(results_path,  f"test_cpp{i}.csv"))


    if not files:
        for file in os.listdir(results_path):
            if file.endswith(".csv"):
                files.append(file)

    list_of_dataframes = []
    for f in files:
        with open(f, newline='') as csvfile:
            df = pd.read_csv(f, sep=';')
            list_of_dataframes.append(df)
    data = pd.concat(list_of_dataframes)

    #data_sort_by_expressions = data.sort_values(by=['Expression'])
    #data_sort_by_expressions_and_executor = data.sort_values(by=['Expression', 'Executor'])

    data_med = data.groupby(['Executor', 'ID', 'Expression'], as_index=False)['Time'].median()
    ratio_df = pd.DataFrame(data_med).groupby(['ID', 'Expression']).apply(ratio)
    ratio_df = pd.concat([ratio_df] * 2, ignore_index=True)
    data_med['Ratio'] = ratio_df
    data_med['Time'] = data_med['Time'] * 1000 # převod na ms
    data_med = data_med.sort_values(by=['Ratio'], ignore_index=True)
    hover_d = "Ratio"
    title_string = "Rychlost vyhodnocení výrazů"

    for i in range(64):
        data_med["Expression"].loc[i] = data_med["Expression"].loc[i] + " [" + str(32-(i//2)) + "]"

    #Figure
    fig = px.scatter(data_med, x="Time", y="Expression", color="Executor",
                    hover_data=["Ratio"],
                    labels={"Time":"Čas (ms)","Expression":"",  "Executor":""}, # customize axis label
                    log_x=True
                )

    #fig.update_xaxes(range=[0, 550.4])
    fig.update_yaxes(range=[-0.5, 31.5])
    fig.update_layout(
        height=700,
        legend=dict(
            yanchor="bottom",
            x=0.99,
            xanchor="right",
            y=0.01
        ),
        font=dict(
            size=12
        ),
        margin=dict(l=0, r=0, t=0, b=0, pad=0),
        paper_bgcolor="White",
    )


    fig.show()
    #fig.write_html("test_speed_table_results.html")
    fig.write_image("figure.pdf", engine="kaleido")



    #expresions = [x[0][1] for x in list_by_experesions]
    #time_p = [float(x[0][5]) for x in newlist]
    #time_c = [float(x[1][5]) for x in newlist]

