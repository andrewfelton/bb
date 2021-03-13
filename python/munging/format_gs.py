#format_gs_all(league, ls, type='Pitching')

def format_gs_all(league, ls, type):
    import gspread
    import gspread_formatting as gsfmt

    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 " + league)
    if type.lower() in ['hitter', 'hitters', 'hitting', 'batting']:
        sh_proj = bb2021.worksheet('Hitter Projections')
    elif type.lower() in ['pitcher', 'pitchers', 'pitching']:
        sh_proj = bb2021.worksheet('Pitcher Projections')

    rate2 = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.00'))
    rate3 = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.000'))
    cardinal = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0'))
    value = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.0'))

    headers = sh_proj.row_values(1)
    for header in headers:
        column = chr(65 + headers.index(header))
        #print(header + ' is column ' + column)
        if header in ls.hitting_counting_stats or header in ls.pitching_counting_stats or header in ['pa', 'ip', 'g', 'gs']:
            gsfmt.format_cell_range(sh_proj, column+':'+column, cardinal)
        elif header in ls.hitting_rate_stats:
            gsfmt.format_cell_range(sh_proj, column + ':' + column, rate3)
        elif header in ls.pitching_rate_stats:
            gsfmt.format_cell_range(sh_proj, column + ':' + column, rate2)
        elif header in ['zar', 'value']:
            gsfmt.format_cell_range(sh_proj, column+':'+column, value)


def format_gs_hitting(league, ls):
    import gspread
    import gspread_formatting as gsfmt

    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 " + league)
    hitter_proj = bb2021.worksheet('Hitter Projections')

    rate = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.000'))
    cardinal = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0'))
    value = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.0'))

    headers = hitter_proj.row_values(1)
    for header in headers:
        column = chr(65 + headers.index(header))
        print(header + ' is column ' + column)
        if header in ls.hitting_counting_stats:
            gsfmt.format_cell_range(hitter_proj, column+':'+column, cardinal)
        elif header in ls.hitting_rate_stats:
            gsfmt.format_cell_range(hitter_proj, column+':'+column, rate)
        elif header in ['zar', 'value']:
            gsfmt.format_cell_range(hitter_proj, column+':'+column, value)

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

