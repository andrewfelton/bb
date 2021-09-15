#format_gs_all(league, ls, type='Pitching')

def format_gs_all(league, ls, type):
    import gspread
    import gspread_formatting as gsfmt

    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    #bb2021 = gc.open("BB 2021 " + league)
    bb2021 = gc.open("BB 2021 InSeason")
    if type.lower() in ['hitter', 'hitters', 'hitting', 'batting']:
        sh_proj = bb2021.worksheet('Hitter Projections - ' + ls.league_name)
    elif type.lower() in ['pitcher', 'pitchers', 'pitching']:
        sh_proj = bb2021.worksheet('Pitcher Projections - ' + ls.league_name)

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


def format_gsheet(sheet):
    import gspread
    import gspread_formatting as gsfmt

    headers = sheet.row_values(1)

    hitting_rate_stats = ['avg','obp','ops','slg']
    hitting_rate_format = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.000'))
    pitching_rate_stats = ['era','whip','DRA','xxxFIP','gmli','wpa','kwera','xfip']
    pitching_rate_format = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.00'))
    counting_stats = ['hr','r','rbi','sb','pa','ab','qs','w','so','sv','hld','svhld','ip','cFIP']
    counting_format = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0'))
    value_format = gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.0'))
    for header in headers:
        colnum = chr(headers.index(header) + 97)
        if header in hitting_rate_stats:
            gsfmt.format_cell_range(sheet, colnum+':'+colnum, hitting_rate_format)
        if header in pitching_rate_stats:
            gsfmt.format_cell_range(sheet, colnum+':'+colnum, pitching_rate_format)
        if header in counting_stats:
            gsfmt.format_cell_range(sheet, colnum+':'+colnum, counting_format)
        if header[0:4]=='zar_' or header[0:6]=='value_':
            gsfmt.format_cell_range(sheet, colnum+':'+colnum, value_format)

def format_gsheet_all():
    import gspread

    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 InSeason")
    format_gsheet(bb2021.worksheet('Proj - Hitters'))
    format_gsheet(bb2021.worksheet('Proj - Pitchers'))

