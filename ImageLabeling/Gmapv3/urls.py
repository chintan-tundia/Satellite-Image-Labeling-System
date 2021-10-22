from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),	
    url(r'^labeldataset$', views.labelDataset, name='labelDataset'),
    url(r'^displayimagesdataset$', views.displayImagesDataset, name='displayImagesDataset'),
    url(r'^showmarkersdataset$', views.show_all_markers_dataset, name='show_all_markers_dataset'),
    url(r'^ajax/get_annotations$', views.get_annotations, name='get_annotations'),
    url(r'^ajax/get_image_list_dataset$', views.getImageListDataset, name='getImageListDataset'),
    url(r'^editannotsdataset$', views.editAnnotsDataset, name='editAnnotsDataset'),
    url(r'^ajax/save_edited_image_dataset$', views.save_edited_image_dataset, name='save_edited_image_dataset'),
    url(r'^downloaddataset$', views.downloadDataset, name='downloadDataset'),
    url(r'^ajax/approve_image$', views.approveImage, name='approveImage'),    
   
]


