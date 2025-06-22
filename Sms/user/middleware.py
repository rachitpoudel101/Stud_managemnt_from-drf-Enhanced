from django.utils.deprecation import MiddlewareMixin

class CustomHookMiddleware(MiddlewareMixin):

    def process_request(self, request):
        print("🔹 process_request: Request received at", request.path)

    def process_view(self, request, view_func, view_args, view_kwargs):
        print("🔹 process_view: Before view runs -", view_func.__name__)

    def process_response(self, request, response):
        print("✅ process_response: After view runs")
        return response

    def process_exception(self, request, exception):
        print(f"❌ process_exception: Exception occurred - {exception}")
        return None