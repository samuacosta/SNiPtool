from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('testmodel', views.TestModelView)

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    # path('', include(router.urls)), name='index')
    path('batch-list-vep/', views.MutationBatchListVep.as_view(),
         name='batch_list_vep'),
    path('batch-list-results/', views.MutationBatchListResults.as_view(),
         name='batch_list_results'),
    path('batch/<int:batch>', views.home, name='batch_selected'),
]
