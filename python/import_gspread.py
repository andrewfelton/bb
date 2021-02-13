import gspread
import pandas as pd

gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')

sh = gc.open("BB 2021")
names = sh.worksheet('Names').get_all_values()
headers = names.pop(0)
names = pd.DataFrame(names, columns=headers)


m = pd.merge(
    names,
    mock_long,
    how='right',
    left_on='Canonical',
    right_on='Player'
)

