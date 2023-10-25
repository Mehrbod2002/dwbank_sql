from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
   openapi.Info(
      title="DW APIS",
      default_version='v1',
      #description="Qbar Document",
      #terms_of_service="https://www.google.com/policies/terms/",
      #contact=openapi.Contact(email="contact@snippets.local"),
      #license=openapi.License(name="BSD License"),
      
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
   generator_class=BothHttpAndHttpsSchemaGenerator
)
