from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Clase de paginación personalizada que permite al cliente
    controlar el tamaño de página mediante el parámetro page_size.
    """
    page_size = 10  # Tamaño por defecto
    page_size_query_param = 'page_size'  # Permite al cliente especificar el tamaño
    max_page_size = 10000  # Límite máximo para evitar abusos

