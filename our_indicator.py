import pandas as pd
from pandas_datareader import wb

# This scrapes the entries from the name and id columns of the DataFrame pertaining to the World Bank site.
# The output should reveal the ID pertaining to that indicator:
df = wb.get_indicators()[['id','name']]
df = df[df.name == 'Individuals using the Internet (% of population)']
print(df)

df = wb.get_indicators()[['id','name']]
df = df[df.name == 'Proportion of seats held by women in national parliaments (%)']
print(df)

df = wb.get_indicators()[['id','name']]
df = df[df.name == 'CO2 emissions (kt)']
print(df)
