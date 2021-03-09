import gspread
import gspread_formatting as gsfmt

gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
bb2021 = gc.open("BB 2021")


fmt = gsfmt.NumberFormat(
    type='NUMBER',
    pattern='0.000'
)

gsfmt.format_cell_range(bb2021.worksheet('Hitter Projections'), 'I:J', fmt)

