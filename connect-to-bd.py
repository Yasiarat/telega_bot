from openpyxl import load_workbook

bd = load_workbook('EXEL.xlsx')
for sheet in bd:
    print(sheet.title)
stickers_page = bd['stickers']
for row in range(1, stickers_page.max_row + 1):
    for column in range(1, stickers_page.max_column + 1):
        if stickers_page.cell(row=row, column=column).value == 'привет':
            print(stickers_page.cell(row=row, column=column + 1).value)

