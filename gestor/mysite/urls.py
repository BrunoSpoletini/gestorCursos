from django.urls import include, path
from cursos import views
from django.contrib import admin
from cursos.views import CustomTokenObtainPairView  # Import your custom view

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/', include('cursos.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]