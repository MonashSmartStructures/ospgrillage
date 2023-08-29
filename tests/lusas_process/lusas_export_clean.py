# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 10:26:29 2021

LUSAS output processing

@author: mayermam
"""

import pandas as pd
import os


def process_lusas(file, folder):
    sheet_dict = pd.read_excel(lusas_filename, sheet_name=None)
    # read lusas output

    dir1 = os.path.join(os.getcwd(), output_folder)
    # set directory
    if not os.path.exists(dir1):
        os.makedirs(output_folder)
        # make a folder if not present

    # read through each tab
    for sheet, data in sheet_dict.items():
        data.columns = data.iloc[1]
        data.drop([0, 1], inplace=True)
        # save each load case as csv
        if sheet != "Model info":
            output_file = sheet.replace(" ", "_") + ".csv"
        else:  # otherwise, save as txt
            output_file = sheet.replace(" ", "_") + ".txt"
        data.to_csv(os.path.join(dir1, output_file), index=False)


if __name__ == "__main__":
    lusas_filename = "Lusas_Outputs.xlsx"  # forces
    output_folder = "28m results/28m_super_t_forces/"
    process_lusas(lusas_filename, output_folder)
    lusas_filename = "Lusas_Outputs_Disp.xlsx"  # deflections
    output_folder = "28m results/28m_super_t_displacement/"
    process_lusas(lusas_filename, output_folder)
