import gspread

gc = gspread.service_account()

# Open a sheet from a spreadsheet in one go
wks = gc.open("1-Cg_VSO5erkBg9YbtATX1uBfzwTiNpDi93UyD25uZkE").Names

