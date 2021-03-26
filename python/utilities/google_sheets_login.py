def main():
    args = sys.argv[1:]
    credentials_path = args[0]
    sheet_id = args[1]
    import gspread
    manager = GoogleSheetManager(credentials_path=
                                 '/bb-2021-2b810d2e3d25.json',
                                 sheet_id='1-Cg_VSO5erkBg9YbtATX1uBfzwTiNpDi93UyD25uZkE')
    manager.start_session()
    rows = manager.get_all_rows()
    cols = manager.get_col_values(2)
    manager.close_session()
    pass




