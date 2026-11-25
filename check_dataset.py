import pandas as pd

data = pd.read_csv("dataset/accident_data.csv")

print("Dataset loaded successfully!")
print()
print("First 5 records:")
print(data.head())

print()
print("Dataset information:")
print(data.info())

print()
print("Number of rows and columns:")
print(data.shape)