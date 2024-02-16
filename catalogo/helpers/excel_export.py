import xlsxwriter
from django.http import HttpResponse
from rest_framework.views import APIView
from datetime import datetime

from ..candidates.models import CandidatesTrees
from ..candidates.serializers import CandidateTreesSerializer

class ExportCandidateTrees(APIView):
    def get(self, request, *args, **kwargs):
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"Reporte_total_candidatos_especies_forestales_{current_date}.xlsx"
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        candidates = CandidatesTrees.objects.exclude(numero_placa__isnull=True)
        candidate_data = CandidateTreesSerializer(candidates, many=True).data

        # Formato para encabezados en negrita y con borde
        bold_format = workbook.add_format({'bold': True, 'border': 1})

        # Encabezados de columna
        headers = ['PLACA', 'CÓDIGO EXPEDIENTE', 'CÓDIGO ESPECIE', 'FECHA EVALUACIÓN', 'USUARIO EVALUADOR', 'DEPARTAMENTO', 'MUNICIPIO', 'NOMBRE DEL PREDIO', 'NOMBRE DEL PROPIETARIO', 'CORREGIMIENTO', 'VEREDA', 'CORREO', 'CELULAR', 'ALTITUD', 'LATITUD', 'GRADOS', 'MINUTOS', 'SEGUNDOS', 'LONGITUD', 'GRADOS', 'MINUTOS', 'SEGUNDOS', 'COORDENADAS GPS', 'COORDENADAS MÓVIL', 'ALTURA TOTAL', 'ALTURA FUSTE', 'CAP', 'COBERTURA', 'OTRA COBERTURA', 'DOMINANCIA', 'FORMA FUSTE', 'DOMINANCIA EJE', 'BIFURCACIÓN', 'ESTADO COPA', 'POSICIÓN COPA', 'ESTADO FITOSANITARIO', 'PRESENCIA PARACITAS', 'RESULTADO', 'EVALUACIÓN', 'OBSERVACIONES', 'FECHA ACTUALIZACIÓN']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, bold_format)

        # Escribir los datos en el archivo Excel
        row_num = 1
        for candidate in candidate_data:
            worksheet.write(row_num, 0, candidate['numero_placa'])
            worksheet.write(row_num, 1, candidate['cod_expediente'])
            worksheet.write(row_num, 2, candidate['cod_especie'])
            worksheet.write(row_num, 3, candidate['fecha_evaluacion'])
            worksheet.write(row_num, 4, candidate['usuario_evaluador'])
            worksheet.write(row_num, 5, candidate['departamento'])
            worksheet.write(row_num, 6, candidate['municipio'])
            worksheet.write(row_num, 7, candidate['nombre_del_predio'])
            worksheet.write(row_num, 8, candidate['nombre_propietario'])
            worksheet.write(row_num, 9, candidate['corregimiento'])
            worksheet.write(row_num, 10, candidate['vereda'])
            worksheet.write(row_num, 11, candidate['correo'])
            worksheet.write(row_num, 12, candidate['celular'])
            worksheet.write(row_num, 13, candidate['altitud'])
            worksheet.write(row_num, 14, candidate['latitud'])
            worksheet.write(row_num, 15, candidate['g_lat'])
            worksheet.write(row_num, 16, candidate['m_lat'])
            worksheet.write(row_num, 17, candidate['s_lat'])
            worksheet.write(row_num, 18, candidate['longitud'])
            worksheet.write(row_num, 19, candidate['g_long'])
            worksheet.write(row_num, 20, candidate['m_long'])
            worksheet.write(row_num, 21, candidate['s_long'])
            worksheet.write(row_num, 22, candidate['coordenadas_decimales'])
            worksheet.write(row_num, 23, candidate['abcisa_xy'])
            worksheet.write(row_num, 24, candidate['altura_total'])
            worksheet.write(row_num, 25, candidate['altura_fuste'])
            worksheet.write(row_num, 26, candidate['cap'])
            worksheet.write(row_num, 27, candidate['cobertura'])
            worksheet.write(row_num, 28, candidate['cober_otro'])
            worksheet.write(row_num, 29, candidate['dominancia_if'])
            worksheet.write(row_num, 30, candidate['forma_fuste'])
            worksheet.write(row_num, 31, candidate['dominancia'])
            worksheet.write(row_num, 32, candidate['alt_bifurcacion'])
            worksheet.write(row_num, 33, candidate['estado_copa'])
            worksheet.write(row_num, 34, candidate['posicion_copa'])
            worksheet.write(row_num, 35, candidate['fitosanitario'])
            worksheet.write(row_num, 36, candidate['presencia'])
            worksheet.write(row_num, 37, candidate['resultado'])
            worksheet.write(row_num, 38, candidate['evaluacion'])
            worksheet.write(row_num, 39, candidate['observaciones'])
            worksheet.write(row_num, 40, candidate['updated'])
            row_num += 1

        workbook.close()
        return response