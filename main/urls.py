from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('testmodel', views.TestModelView)

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    # path('', include(router.urls))
]
