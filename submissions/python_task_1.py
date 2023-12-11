import pandas as pd
import numpy as np

def generate_car_matrix(df)->pd.DataFrame:
    car_pivot = df.pivot_table(values='car', index='id_1', columns='id_2', fill_value=0)
    np.fill_diagonal(car_pivot.values, 0)
    return car_pivot

def get_type_count(df)->dict:
    conditions = [
        (df['car'] <= 15),
        (df['car'] > 15) & (df['car'] <= 25),
        (df['car'] > 25)
    ]
    choices = ['low', 'medium', 'high']
    df['car_type'] = pd.Series(np.select(conditions, choices), dtype='category')
    type_counts = df['car_type'].value_counts().to_dict()
    sorted_type_counts = dict(sorted(type_counts.items()))
    return sorted_type_counts

def get_bus_indexes(df)->list:
    mean_bus = df['bus'].mean()
    bus_indexes = df[df['bus'] > 2 * mean_bus].index.tolist()
    sorted_bus_indexes = sorted(bus_indexes)
    return sorted_bus_indexes

def filter_routes(df)->list:
    avg_truck_by_route = df.groupby('route')['truck'].mean()
    selected_routes = avg_truck_by_route[avg_truck_by_route > 7].index.tolist()
    sorted_routes = sorted(selected_routes)
    return sorted_routes

def multiply_matrix(matrix)->pd.DataFrame:
    modified_df = matrix.copy()
    modified_df = modified_df.map(lambda x: x * 0.75 if x > 20 else x * 1.25)
    modified_df = modified_df.round(1)
    return modified_df

def time_check(df)->pd.Series:
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['startDay'] = pd.Categorical(df['startDay'], categories=days_order, ordered=True)
    df['endDay'] = pd.Categorical(df['endDay'], categories=days_order, ordered=True)
    df['startTime'] = pd.to_datetime(df['startTime'], format='%H:%M:%S').dt.time
    df['endTime'] = pd.to_datetime(df['endTime'], format='%H:%M:%S').dt.time
    mask = (
        (df['startDay'] == df['endDay']) & (df['startTime'] > df['endTime']) |
        (df['startDay'] > df['endDay'])
    )
    boolean_series = df.loc[mask, ['id', 'id_2']].set_index(['id', 'id_2']).any(axis=1)
    return boolean_series