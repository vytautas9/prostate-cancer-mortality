"""
This script read the data from .sas7bdat format, selects relevant columns, renames them, 
replaces some NA values, sets correct data types, create death from other causes column,
created patient index column and saves as picke file.
"""

from pickle import dump
from pandas import read_sas
from sklearn.model_selection import train_test_split


def read_prepare_initial_data(path):
    print(f'\nReading data from: {path} ........')
    
    # Read, prepare, anonimize the initial data
    df = read_sas(path)

    print(f'Finished reading, loaded dataset shape: {df.shape}')
    print(f'Read column names: {df.columns}')

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
    print(f'Removing rows with NA values.......')
    df.dropna(thresh=df.shape[1], inplace=True)
    print(f'Dataset shape after removing NA values: {df.shape}')

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

    print(f'Returing dataset of shape: {df.shape}')
    print(f'and such column names: {df.columns}')

    return df


def trainTestSplit(x_columns_to_drop, y_columns, stratify_column, test_size):
    # Train - test split

    print('\n80/20% Train - Test split .......')
    # 80/20 split and stratify based on 'overall_mortality'
    data_train, data_test, y_train, y_test = train_test_split(
        data.drop(x_columns_to_drop, axis=1),
        data[y_columns], test_size=test_size, random_state=1, 
        stratify=data[[stratify_column]])

    data_train[y_columns] = y_train
    data_test[y_columns] = y_test

    print('Shape of train: ', data_train.shape, '\n')
    print('Shape of test: ', data_test.shape, '\n')

    return data_train, data_test


if __name__ == '__main__':
    # Read the original data
    data_path = 'data/data_original.sas7bdat'
    data = read_prepare_initial_data(data_path)

    # save the dataset
    print(f'Saving cleaned dataset.....')
    with open('data/data_clean.pkl', 'wb') as f:
        dump(data, f)
    print('Finished saving clean dataset')

    # train - test split
    # column names which will be dropped from X's (feature dataset)
    x_columns_to_drop = ['bcr', 'mts', 'overall_mortality', 'cancer_specific_mortality', 
                        'death_from_other_causes']

    # columns names of Y's (response)
    y_columns = ['bcr', 'mts', 'death_from_other_causes', 'cancer_specific_mortality']

    train, test = trainTestSplit(x_columns_to_drop, y_columns, 'overall_mortality', 0.20)

    # save train/test datasets
    print(f'Saving train and test datasets.......')
    with open('data/data_train.pkl', 'wb') as f:
        dump(train, f)
    with open('data/data_test.pkl', 'wb') as f:
        dump(test, f)
    print('Finished saving train and test datasets','\n')