import pandas as pd

# Example DataFrame
df = pd.DataFrame({
    'ColumnName': [1, 2, 3, 4, 5],
    'OtherColumn': ['a', 'b', 'c', 'd', 'e']
})

# Iterating over the rows of the column 'ColumnName'
for value in df['ColumnName']:
    print(value)
