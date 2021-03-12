def format_gs_hitting():
    import gspread
    import gspread_formatting as gsfmt

    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 SoS")

    rate = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.000'))
    cardinal = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0'))
    value = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.0'))

    gsfmt.format_cell_range(bb2021.worksheet('Hitter Projections'), 'C:G', cardinal)
    gsfmt.format_cell_range(bb2021.worksheet('Hitter Projections'), 'H:I', rate)
    gsfmt.format_cell_range(bb2021.worksheet('Hitter Projections'), 'J:K', value)

def format_gs_pitching():
    import gspread
    import gspread_formatting as gsfmt

    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 SoS")

    rate = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.00'))
    cardinal = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0'))
    value = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.0'))

    gsfmt.format_cell_range(bb2021.worksheet('Pitcher Projections'), 'C:G', cardinal)
    gsfmt.format_cell_range(bb2021.worksheet('Pitcher Projections'), 'H:I', rate)
    gsfmt.format_cell_range(bb2021.worksheet('Pitcher Projections'), 'J:K', value)

