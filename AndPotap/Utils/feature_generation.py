# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Notes
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
(*) This file contains all the functions needed to generate the running
    features out of the marathon splits
"""
# ===========================================================================
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Imports
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import time
import pandas as pd
# ===========================================================================
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Define the functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def format_correctly(df, verbose=False):
    """
    Properly formats the DateTime objects and introduces inplace
    the DateTime objects columns in seconds
    :param df: pd.DataFrame | the marathon pd.DataFrame
    :param verbose: bool | True prints the time the function took
    :return: pd.DataFrame | the original pd.DataFrame with the
                            extra columns
    """
    t0 = time.time()

    # Focus on the relevant columns
    split_cols = [col for col in df.columns if 'k' in col]

    # Transform variables into DateTime
    for col in split_cols:

        # Generate new column
        new_col = col + '_sec'

        # Introduce the DateTime objects
        aux = pd.DatetimeIndex(df[col])
        df[col] = aux

        # Subset for non NaTs
        mask = pd.notnull(aux)

        df.loc[mask, new_col] = (aux[mask].hour * 3600 +
                                 aux[mask].minute * 60 +
                                 aux[mask].second)
    t1 = time.time()
    if verbose:
        print('Formatting took: {:6.1f} sec'.format(t1 - t0))

    return df


def add_diffs(df, verbose=False):
    """
    Adds the features that contain the differences in seconds
    between the marathon 5 k splits
    :param df: pd.DataFrame | the marathon pd.DataFrame
    :param verbose: bool | True prints the time the function took
    :return: pd.DataFrame | the original pd.DataFrame with
                            the extra columns
    """
    t0 = time.time()
    col_diffs = ['splint_5k_sec',
                 'splint_10k_sec',
                 'splint_15k_sec',
                 'splint_20k_sec',
                 'splint_25k_sec',
                 'splint_30k_sec',
                 'splint_35k_sec',
                 'splint_40k_sec']

    df.loc[:, 'pace_total'] = df.loc[:, 'splint_40k_sec'] / len(col_diffs)

    df.loc[:, 'diff_1'] = df[col_diffs[0]]

    df.loc[:, 'pace_1'] = df[col_diffs[0]] / df['pace_total']

    df.loc[:, 'pace_index_1'] = 100

    for i in range(len(col_diffs) - 1):

        # Name new columns
        new_col_diff = 'diff_' + str(i + 2)
        new_col_pace = 'pace_' + str(i + 2)
        new_col_pace_index = 'pace_index_' + str(i + 2)

        # Introduce the new data
        df.loc[:, new_col_diff] = (df[col_diffs[i + 1]] -
                                   df[col_diffs[i]])

        df.loc[:, new_col_pace] = df[new_col_diff] / df['pace_total']

        df.loc[:, new_col_pace_index] = 100 * (df[new_col_diff] /
                                               df[col_diffs[0]])

    t1 = time.time()
    if verbose:
        print('Constructing diffs took: {:6.1f} sec'.format(t1 - t0))

    return df


def reshape_properly(df, verbose=False):
    t0 = time.time()
    df['ID'] = df.index
    aux = df.copy()
    id_vars = ['ID',
               'bib',
               'gender_age',
               'gun_place',
               'gun_time',
               'name',
               'official_time',
               'pace_per_mile',
               'percentile_age-graded',
               'place',
               'place_age-graded',
               'place_age-graded_of',
               'place_age-group',
               'place_age-group_of',
               'place_gender',
               'place_gender_of',
               'place_overall',
               'place_overall_of',
               'team',
               'time_age-graded',
               'pace_total',
               'splint_half']

    # Melt the DataFrame
    aux = pd.melt(frame=aux, id_vars=id_vars)

    aux.loc[:, 'identifier'] = 'NaN'

    mask = aux['variable'].str.contains('k')
    aux.loc[mask, 'identifier'] = 'date_time'

    mask = aux['variable'].str.contains('k_sec')
    aux.loc[mask, 'identifier'] = 'sec'

    mask = aux['variable'].str.contains('diff_')
    aux.loc[mask, 'identifier'] = 'diff'

    mask = aux['variable'].str.contains('pace_')
    aux.loc[mask, 'identifier'] = 'pace'

    mask = aux['variable'].str.contains('pace_index')
    aux.loc[mask, 'identifier'] = 'pace_index'

    id_q = aux['identifier'].unique()
    for identifier in id_q:
        tmp = aux[aux['identifier'] == identifier].copy()
        tmp = tmp[['ID', 'identifier', 'value']]
        tmp = tmp.set_index('ID')
        tmp = tmp.pivot(columns='identifier', values='value')

    # Revert back the columns

    t1 = time.time()
    if verbose:
        print('Constructing diffs took: {:6.1f} sec'.format(t1 - t0))
    return df
# ===========================================================================
