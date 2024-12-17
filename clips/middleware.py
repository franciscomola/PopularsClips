# core/middleware.py
class LogHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.headers)  # Imprime los encabezados en la consola
        return self.get_response(request)
