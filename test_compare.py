import csv
import string

import subprocess
import os

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def ratio(g):
    ratio = list(g['Time'])[0]/list(g['Time'])[1]
    return ratio

def blockRatio64To256(g):
    ratio = list(g['Time'])[1]/list(g['Time'])[0]
    return ratio

def blockRatio64To1024(g):
    ratio = list(g['Time'])[2]/list(g['Time'])[0]
    return ratio


def porovnani_old_vs_avx2(data_cat):

    data_med_cat1_old_and_avx = data_cat[0].loc[data_cat[0]["Executor"].isin(["BParser AVX2", "BParser_OLD"])]
    cat1_ratio = pd.DataFrame(data_med_cat1_old_and_avx).groupby(['Expression']).apply(ratio)
    # add ratio 1 to old
    data_med_cat1_old_and_avx['Ratio'] = [cat1_ratio.values[x] if x < cat1_ratio.values.size else 1 for x in
                                          range(cat1_ratio.values.size * 2)]
    cat1_ratio_median = cat1_ratio.median()
    data_med_cat2_old_and_avx = data_cat[1].loc[data_cat[1]["Executor"].isin(["BParser AVX2", "BParser_OLD"])]
    cat2_ratio = pd.DataFrame(data_med_cat2_old_and_avx).groupby(['Expression']).apply(ratio)
    cat2_ratio_median = cat2_ratio.median()
    data_med_cat3_old_and_avx = data_cat[2].loc[data_cat[2]["Executor"].isin(["BParser AVX2", "BParser_OLD"])]
    cat3_ratio = pd.DataFrame(data_med_cat3_old_and_avx).groupby(['Expression']).apply(ratio)
    cat3_ratio_median = cat3_ratio.median()
    data_med_cat4_old_and_avx = data_cat[3].loc[data_cat[3]["Executor"].isin(["BParser AVX2", "BParser_OLD"])]
    cat4_ratio = pd.DataFrame(data_med_cat4_old_and_avx).groupby(['Expression']).apply(ratio)
    cat4_ratio_median = cat4_ratio.median()
    fig = go.Figure()
    # porovnání kategorii
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[cat1_ratio_median, cat2_ratio_median, cat3_ratio_median, cat4_ratio_median],
        name='BParser AVX2',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[1, 1, 1, 1],
        name='BParser OLD',
        marker_color='lime'
    ))
    fig.update_yaxes(title_text="Ratio", dtick=0.1)
    #fig.show()
    fig.write_image(results_path + "figure_old_vs_avx.pdf", engine="kaleido")
    
    
    # porovnání první kategorie
    fig = px.bar(data_med_cat1_old_and_avx, y="Ratio", x="Expression", color="Executor",
                 hover_data=["Ratio"],
                 labels={"Time": "Ratio", "Expression": "Expression", "Executor": "Procesor"},
                 # customize axis label
                 color_discrete_sequence=["blue", "lime"],
                 barmode='group',
                 title="BParser OLD vs BParser AVX2"
                 )
    
    fig.update_yaxes(title_text="Ratio", dtick=0.1)
    #fig.show()
    fig.write_image(results_path + "figure_old_vs_avx_first_cat.pdf", engine="kaleido")
    
def getCategory(dataFrame, category_sep_indexes):
    ret = []
    ret.append(dataFrame.loc[dataFrame["ID"].between(0, category_sep_indexes[0] - 1)])
    ret.append(dataFrame.loc[dataFrame["ID"].between(category_sep_indexes[0], category_sep_indexes[1] - 1)])
    ret.append(dataFrame.loc[dataFrame["ID"].between(category_sep_indexes[1], category_sep_indexes[2] - 1)])
    ret.append(dataFrame.loc[dataFrame["ID"].between(category_sep_indexes[2], category_sep_indexes[3] - 1)])
    return ret


def porovnaniBlockSize(categories, title):
    novec_cat1_med = categories[0].groupby("BlockSize").median()
    novec_cat2_med = categories[1].groupby("BlockSize").median()
    novec_cat3_med = categories[2].groupby("BlockSize").median()
    novec_cat4_med = categories[3].groupby("BlockSize").median()
    fig = go.Figure(layout_title_text=title)
    # porovnání kategorii
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[1, 1, 1, 1],
        name='64',
        marker_color='lightgray'
    ))
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[blockRatio64To256(novec_cat1_med), blockRatio64To256(novec_cat2_med), blockRatio64To256(novec_cat3_med),
           blockRatio64To256(novec_cat4_med)],
        name='256',
        marker_color='gray'
    ))
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[blockRatio64To1024(novec_cat1_med), blockRatio64To1024(novec_cat2_med), blockRatio64To1024(novec_cat3_med),
           blockRatio64To1024(novec_cat4_med)],
        name='1024',
        marker_color='black'
    ))

    fig.update_yaxes(title_text="Ratio", dtick=0.1)
    #fig.show()
    fig.write_image(results_path + "figure_block_size.pdf", engine="kaleido")


def porovnani_simd_size(data_med):
    # get dataframes by Executor
    grouped = data_med.groupby(data_med.Executor)
    bparser_novec = grouped.get_group("BParser no vectorization")
    bparser_sse = grouped.get_group("BParser SSE")
    bparser_avx = grouped.get_group("BParser AVX2")
    bparser_avx512 = grouped.get_group("BParser AVX512")

    bparser_novec_cat = getCategory(bparser_novec, category_sep_indexes)
    bparser_sse_cat = getCategory(bparser_sse, category_sep_indexes)
    bparser_avx_cat = getCategory(bparser_avx, category_sep_indexes)
    bparser_avx512_cat = getCategory(bparser_avx512, category_sep_indexes)

    ratio_sse_to_novec_cat1 = np.average(bparser_sse_cat[0]["Time"].values / bparser_novec_cat[0]["Time"].values)
    ratio_avx_to_novec_cat1 = np.average(bparser_avx_cat[0]["Time"].values / bparser_novec_cat[0]["Time"].values)
    ratio_avx512_to_novec_cat1 = np.average(bparser_avx512_cat[0]["Time"].values / bparser_novec_cat[0]["Time"].values)

    ratio_sse_to_novec_cat2 = np.average(bparser_sse_cat[1]["Time"].values / bparser_novec_cat[1]["Time"].values)
    ratio_avx_to_novec_cat2 = np.average(bparser_avx_cat[1]["Time"].values / bparser_novec_cat[1]["Time"].values)
    ratio_avx512_to_novec_cat2 = np.average(bparser_avx512_cat[1]["Time"].values / bparser_novec_cat[1]["Time"].values)

    ratio_sse_to_novec_cat3 = np.average(bparser_sse_cat[2]["Time"].values / bparser_novec_cat[2]["Time"].values)
    ratio_avx_to_novec_cat3 = np.average(bparser_avx_cat[2]["Time"].values / bparser_novec_cat[2]["Time"].values)
    ratio_avx512_to_novec_cat3 = np.average(bparser_avx512_cat[2]["Time"].values / bparser_novec_cat[2]["Time"].values)

    ratio_sse_to_novec_cat4 = np.average(bparser_sse_cat[3]["Time"].values / bparser_novec_cat[3]["Time"].values)
    ratio_avx_to_novec_cat4 = np.average(bparser_avx_cat[3]["Time"].values / bparser_novec_cat[3]["Time"].values)
    ratio_avx512_to_novec_cat4 = np.average(bparser_avx512_cat[3]["Time"].values / bparser_novec_cat[3]["Time"].values)

    fig = go.Figure(layout_title_text="Porovnání SIMD size")
    # porovnání kategorii
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[1, 1, 1, 1],
        name='N/A',
        marker_color='red'
    ))

    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[ratio_sse_to_novec_cat1, ratio_sse_to_novec_cat2, ratio_sse_to_novec_cat3, ratio_sse_to_novec_cat4],
        name='SSE',
        marker_color='yellow'
    ))
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[ratio_avx_to_novec_cat1, ratio_avx_to_novec_cat2, ratio_avx_to_novec_cat3, ratio_avx_to_novec_cat4],
        name='AVX2',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[ratio_avx512_to_novec_cat1, ratio_avx512_to_novec_cat2, ratio_avx512_to_novec_cat3, ratio_avx512_to_novec_cat4],
        name='AVX512',
        marker_color='green'
    ))
    
    fig.update_yaxes(title_text="Ratio", dtick=0.1)
    #fig.show()
    fig.write_image(results_path + "figure_simd_size.pdf", engine="kaleido")
    
    
def porovnani_cpp_vs_avx512(data_cat):
    
    data_med_cat1_cpp_and_avx512 = data_cat[0].loc[data_cat[0]["Executor"].isin(["BParser AVX512", "C++"])]
    cat1_ratio = pd.DataFrame(data_med_cat1_cpp_and_avx512).groupby(['Expression']).apply(ratio)
    # add ratio 1 to cpp
    data_med_cat1_cpp_and_avx512['Ratio'] = [cat1_ratio.values[x] if x < cat1_ratio.values.size else 1 for x in
                                          range(cat1_ratio.values.size * 2)]
    cat1_ratio_median = cat1_ratio.median()
    data_med_cat2_cpp_and_avx512 = data_cat[1].loc[data_cat[1]["Executor"].isin(["BParser AVX512", "C++"])]
    cat2_ratio = pd.DataFrame(data_med_cat2_cpp_and_avx512).groupby(['Expression']).apply(ratio)
    cat2_ratio_median = cat2_ratio.median()
    data_med_cat3_cpp_and_avx512 = data_cat[2].loc[data_cat[2]["Executor"].isin(["BParser AVX512", "C++"])]
    cat3_ratio = pd.DataFrame(data_med_cat3_cpp_and_avx512).groupby(['Expression']).apply(ratio)
    cat3_ratio_median = cat3_ratio.median()
    data_med_cat4_cpp_and_avx512 = data_cat[3].loc[data_cat[3]["Executor"].isin(["BParser AVX512", "C++"])]
    cat4_ratio = pd.DataFrame(data_med_cat4_cpp_and_avx512).groupby(['Expression']).apply(ratio)
    cat4_ratio_median = cat4_ratio.median()
    fig = go.Figure()
    # porovnání kategorii
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[cat1_ratio_median, cat2_ratio_median, cat3_ratio_median, cat4_ratio_median],
        name='BParser AVX512',
        marker_color='green'
    ))
    fig.add_trace(go.Bar(
        x=["Arithmetic", "Boolean", "Function", "Composed"],
        y=[1, 1, 1, 1],
        name='C++',
        marker_color='blue'
    ))
    
    fig.update_yaxes(title_text="Ratio", dtick=0.1)
    #fig.show()
    fig.write_image(results_path + "figure_cpp_vs_avx512.pdf", engine="kaleido")
    

if __name__ == "__main__":

    run_tests_switch = False
    num_of_test_runs = 5
    files = []
    simd_sizes = [1, 2, 4, 8]

    #index (ID) of categories (inclusive)
    category_sep_indexes = [6, 15, 38, 999] # => 0-5, 6-14, 15-37, 36-end(44)

    final_path = "ntb10k/"
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

    list_of_dataframes = []
    for f in files:
        with open(os.path.join(tests_path,f), newline='') as csvfile:
            df = pd.read_csv(csvfile, sep=';')
            list_of_dataframes.append(df)
    data = pd.concat(list_of_dataframes)

    #data_sort_by_expressions = data.sort_values(by=['Expression'])
    #data_sort_by_expressions_and_executor = data.sort_values(by=['Expression', 'Executor'])
    # compute median from num_of_test_runs
    data_med_blockSize = data.groupby(['Executor', 'ID', 'Expression', 'BlockSize'], as_index=False)['Time'].median()

    data_med = data.groupby(['Executor', 'ID', 'Expression'], as_index=False)['Time'].median()

    # save to csv

    with open(os.path.join(results_path,"median_results.csv"), 'w') as csvfile:
        data_med.to_csv(csvfile, index=False, sep=';')

    # get dataframes for each category
    data_med_cat = getCategory(data_med, category_sep_indexes)



    # get dataframes by BlockSize
    grouped = data_med_blockSize.groupby(data_med_blockSize.BlockSize)
    df_64BlockSize = grouped.get_group(64)
    df_256BlockSize = grouped.get_group(256)
    df_1024BlockSize = grouped.get_group(1024)

    # get dataframes by Executor
    grouped = data_med_blockSize.groupby(data_med_blockSize.Executor)
    df_bparser_novec = grouped.get_group("BParser no vectorization")
    df_bparser_sse = grouped.get_group("BParser SSE")
    df_bparser_avx = grouped.get_group("BParser AVX2")
    df_bparser_avx512 = grouped.get_group("BParser AVX512")

    # porovnani BlockSize
    df_bparser_novec_cat = getCategory(df_bparser_novec, category_sep_indexes)
    porovnaniBlockSize(df_bparser_novec_cat, "No Vectorization")

    df_bparser_sse_cat = getCategory(df_bparser_sse, category_sep_indexes)
    porovnaniBlockSize(df_bparser_sse_cat, "SSE")

    df_bparser_avx_cat = getCategory(df_bparser_avx, category_sep_indexes)
    porovnaniBlockSize(df_bparser_avx_cat, "AVX2")

    df_bparser_avx512_cat = getCategory(df_bparser_avx512, category_sep_indexes)
    porovnaniBlockSize(df_bparser_avx512_cat, "AVX512")

    # vypocet pomeru bparser_old a avx2
    porovnani_old_vs_avx2(data_med_cat)

    porovnani_simd_size(data_med)

    porovnani_cpp_vs_avx512(data_med_cat)

    #ratio_df = pd.DataFrame(data_med).groupby(['ID', 'Expression']).apply(ratio)
    #ratio_df = pd.concat([ratio_df] * 2, ignore_index=True)

    #data_med['Ratio'] = ratio_df
    #data_med['Time'] = data_med['Time'] * 1000 # převod na ms
    #data_med = data_med.sort_values(by=['Ratio'], ignore_index=True)
    #hover_d = "Ratio"
    #title_string = "Rychlost vyhodnocení výrazů"

    #for i in range(64):
    #    data_med["Expression"].loc[i] = data_med["Expression"].loc[i] + " [" + str(32-(i//2)) + "]"

    #Figure
    #fig = px.scatter(df_64BlockSize, x="Time", y="Expression", color="Executor",
    #                hover_data=["Executor"],
    #                labels={"Time":"Čas (ms)","Expression":"Výraz",  "Executor":"Procesor"}, # customize axis label
    #                log_x=True)

    """
    df_bparser_avx["BlockSize"] = df_bparser_avx["BlockSize"].astype(str)
    fig = px.scatter(df_bparser_avx, x="Time", y="Expression", color="BlockSize",
                                     hover_data=["BlockSize"],
                                     labels={"Time":"Čas (ms)","Expression":"Výraz",  "BlockSize":"Block size"}, # customize axis label
                                     log_x=True,
                     title= df_bparser_avx["Executor"][0]
                     )
    """

    #fig.update_xaxes(range=[0, 550.4])
    #fig.update_yaxes(range=[-0.5, 31.5])
    """
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
    """

    #fig.show()
    #fig.write_html("test_speed_table_results.html")
    #fig.write_image("figure.pdf", engine="kaleido")



    #expresions = [x[0][1] for x in list_by_experesions]
    #time_p = [float(x[0][5]) for x in newlist]
    #time_c = [float(x[1][5]) for x in newlist]

