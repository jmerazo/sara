import xlsxwriter

def generate_excel(file_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    
    worksheet.write('A1', 'Ejemplo de Archivo Excel')
    worksheet.write('A2', 'Datos:')
    worksheet.write('B2', 123)
    worksheet.write('C2', 456)
    
    workbook.close()

generate_excel("ejemplo.xlsx")