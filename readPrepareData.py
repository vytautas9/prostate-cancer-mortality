"""
This script read the data from .sas7bdat format, selects relevant columns, renames them, 
replaces some NA values, sets correct data types, create death from other causes column,
created patient index column and saves as picke file.
"""

from pickle import dump
from pandas import read_sas


def read_prepare_initial_data(path):
    # Read, prepare, anonimize the initial data
    df = read_sas(path)

    # Select only relevant columns
    df = df[['Amzius', 'PSA', 'naujasCT', 'BxGleason', 'Bxkodas', 'RP_GG', 'pT',
             'LNI01', 'R', 'PSAdaugiau0_1', 'BCR', 'MTS', 'SURVIVAL', 'OS', 'CSS',
             'Rpgleson', 'TRYSgrupes', 'PLNDO1', 'BFS', 'MTS_men']]

    # Rename the column names
    df.rename(columns={'Amzius': 'age', 'PSA': 'psa', 'naujasCT': 'clinical_stage',
                       'Bxkodas': 'biopsy_gleason_gg', 'RP_GG': 'pathological_gleason_gg',
                       'pT': 'pathologic_stage', 'LNI01': 'lni', 'R': 'surgical_margin_status',
                       'PSAdaugiau0_1': 'persistent_psa', 'SURVIVAL': 'survival_months',
                       'BCR': 'bcr', 'MTS': 'mts', 'OS': 'overall_mortality',
                       'CSS': 'cancer_specific_mortality', 'BFS': 'survival_months_bcr',
                       'MTS_men': 'survival_months_mts'},
              inplace=True)

    # Fill the LNI column NA values with 'unknown' value
    df.fillna({'lni': 'unknown', 'r': 'unknown'}, inplace=True)

    # Drop rows with NA values, every row must have 0 NA values
    df.dropna(thresh=df.shape[1], inplace=True)

    # Change the data types of columns
    # Float --> Int --> String
    df[['overall_mortality']] = df[['overall_mortality']].astype(int)
    df[['cancer_specific_mortality']] = df[[
        'cancer_specific_mortality']].astype(int)
    df[['mts']] = df[['mts']].astype(int)
    df[['bcr']] = df[['bcr']].astype(int)
    df[['clinical_stage']] = df[['clinical_stage']].astype(int)
    df[['biopsy_gleason_gg']] = df[['biopsy_gleason_gg']].astype(int)
    df[['pathological_gleason_gg']] = df[[
        'pathological_gleason_gg']].astype(int)
    df[['pathologic_stage']] = df[['pathologic_stage']].astype(int)
    df[['surgical_margin_status']] = df[['surgical_margin_status']].astype(int)
    df[['persistent_psa']] = df[['persistent_psa']].astype(int)
    df[['TRYSgrupes']] = df[['TRYSgrupes']].astype(int)
    df[['PLNDO1']] = df[['PLNDO1']].astype(int)

    df = df.astype({'clinical_stage': 'str', 'biopsy_gleason_gg': 'str',
                    'pathological_gleason_gg': 'str', 'pathologic_stage': 'str',
                    'lni': 'str', 'surgical_margin_status': 'str',
                    'persistent_psa': 'str', 'bcr': 'str', 'mts': 'str',
                    'overall_mortality': 'str', 'cancer_specific_mortality': 'str',
                    'TRYSgrupes': 'str', 'PLNDO1': 'str',
                    'survival_months': 'int32', 'survival_months_bcr': 'int32',
                    'survival_months_mts': 'int32'})

    # Create death from other causes column
    df['death_from_other_causes'] = '0'
    df.loc[(df['overall_mortality'] == '1') & (
        df['cancer_specific_mortality'] == '0'), 'death_from_other_causes'] = '1'

    # Create a patient ID index
    df['patient_id'] = range(1, len(df) + 1)

    return df


if __name__ == '__main__':
    # Read the original data
    data_path = 'data/data_original.sas7bdat'
    data = read_prepare_initial_data(data_path)
    with open('data/data_clean.pkl', 'wb') as f:
        dump(data, f)
