import pandas as pd
from datetime import datetime, time

df = pd.read_csv('datasets/dataset-3.csv')
def calculate_distance_matrix(df)->pd.DataFrame():
    distance_matrix = pd.pivot_table(df, values='distance', index='id_start', columns='id_end', fill_value=0)
    distance_matrix = distance_matrix + distance_matrix.T
    distance_matrix.values[[range(len(distance_matrix))]*2] = 0
    for i in distance_matrix.index:
        for j in distance_matrix.columns:
            if distance_matrix.loc[i, j] == 0 and i != j:
                possible_routes = df[(df['id_start'] == i) & (df['id_end'] != i) & (df['id_end'] == j)]
                for _, route in possible_routes.iterrows():
                    distance_matrix.loc[i, j] += route['distance']
    return distance_matrix



def unroll_distance_matrix(df)->pd.DataFrame():
    unrolled_data = []

    for _, row in df.iterrows():
        id_start = row['id_start']
        for col, distance in row.items():
            if col != 'id_start' and distance != 0:
                unrolled_data.append({'id_start': id_start, 'id_end': col, 'distance': distance})
    unrolled_df = pd.DataFrame(unrolled_data)
    unrolled_df = unrolled_df.sort_values(by=['id_start', 'id_end']).reset_index(drop=True)
    return unrolled_df



def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    reference_rows = df[df['id_start'] == reference_id]
    reference_avg_distance = reference_rows['distance'].mean()
    lower_threshold = reference_avg_distance - (reference_avg_distance * 0.1)
    upper_threshold = reference_avg_distance + (reference_avg_distance * 0.1)
    result_df = df[(df['distance'] >= lower_threshold) & (df['distance'] <= upper_threshold)]
    result_ids = sorted(result_df['id_start'].unique())
    return result_ids

def calculate_toll_rate(df)->pd.DataFrame():
    rate_coefficients = {
        'moto': 0.8,
        'car': 1.2,
        'rv': 1.5,
        'bus': 2.2,
        'truck': 3.6
    }
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate_coefficient
    return df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    time_ranges = {
        'morning_weekdays': (time(0, 0, 0), time(10, 0, 0)),
        'afternoon_weekdays': (time(10, 0, 0), time(18, 0, 0)),
        'evening_weekdays': (time(18, 0, 0), time(23, 59, 59)),
        'weekends': (time(0, 0, 0), time(23, 59, 59)),
    }

    discount_factors = {
        'morning_weekdays': 0.8,
        'afternoon_weekdays': 1.2,
        'evening_weekdays': 0.8,
        'weekends': 0.7,
    }

    for _, row in df.iterrows():
        start_time = datetime.strptime(row['startTime'], '%H:%M:%S').time()
        end_time = datetime.strptime(row['endTime'], '%H:%M:%S').time()

        time_range = None
        for key, (start, end) in time_ranges.items():
            if start_time >= start and end_time <= end:
                time_range = key
                break

        if time_range:
            discount_factor = discount_factors[time_range]
            for vehicle_type in ['moto', 'car', 'rv', 'bus', 'truck']:
                df.at[_, vehicle_type] *= discount_factor

    df['start_day'] = df['startDay'].apply(lambda x: x.capitalize())
    df['end_day'] = df['endDay'].apply(lambda x: x.capitalize())
    df['start_time'] = pd.to_datetime(df['startTime'], format='%H:%M:%S').dt.time
    df['end_time'] = pd.to_datetime(df['endTime'], format='%H:%M:%S').dt.time

    return df