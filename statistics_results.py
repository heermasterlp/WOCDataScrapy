# coding: utf-8
import pandas as pd

data1_path = "Publish_papers_statistics_all.csv"

df = pd.read_csv(data1_path)

print(df.count())

publish_years = df["Publish Year"]

years = set(publish_years)

papers_per_year = {}
for year in years:
    count = 0
    for py in publish_years:
        if py == year:
            count += 1
    papers_per_year[year] = count
print(papers_per_year)
