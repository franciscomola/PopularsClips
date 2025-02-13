from django.contrib import admin
from django.urls import path, include  # Asegúrate de que 'include' esté importado
from clips.views import ClipListView  # Importa tu vista clip_list
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('clips/', include('clips.urls')),  # Incluir las URLs de la aplicación clips
    path('accounts/', include('django.contrib.auth.urls')),  # Agrega las rutas de login/logout
    path('', ClipListView.as_view(), name='home'),  # Página de inicio configurada a clip_list
    path('cms/admin/', include(wagtailadmin_urls)),  # Panel de administración de Wagtail
    path('cms/', include(wagtail_urls)),  # Wagtail estará accesible en /cms/
]
