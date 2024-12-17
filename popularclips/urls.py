from django.contrib import admin
from django.urls import path, include  # Asegúrate de que 'include' esté importado
from clips.views import ClipListView  # Importa tu vista clip_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clips/', include('clips.urls')),  # Incluir las URLs de la aplicación clips
    path('accounts/', include('django.contrib.auth.urls')),  # Agrega las rutas de login/logout
    path('', ClipListView.as_view(), name='home'),  # Página de inicio configurada a clip_list

]
