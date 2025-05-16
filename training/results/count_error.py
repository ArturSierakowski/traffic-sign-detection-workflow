import pandas as pd
import yaml

df = pd.read_csv('confusion_matrix.csv', index_col=None)
df = df.drop(index=105, columns='105')

with open('../data.yaml', 'r') as f:
    data = yaml.safe_load(f)
class_names = data['names']

for col in df.columns:
    col_index = int(col)
    series = df[col].copy()
    series.iloc[col_index] = -1
    max_row_index = series.idxmax()
    max_value = series[max_row_index]

    if max_value > 0:
        true_class = class_names[col_index]
        mistaken_class = class_names[int(max_row_index)]
        with open('error_report.txt', 'w', encoding='utf-8') as out:
            for col in df.columns:
                col_index = int(col)
                series = df[col].copy()
                series.iloc[col_index] = -1
                max_row_index = series.idxmax()
                max_value = series[max_row_index]

                if max_value > 0:
                    true_class = class_names[col_index]
                    mistaken_class = class_names[int(max_row_index)]
                    out.write(f"{true_class}, most often mistaken for: {mistaken_class} (errors: {max_value})\n")