from django.contrib import admin
from django.urls import path

from .views import home
from .views import TestResultUpDateView,GenerateReportView,about,PatientCreateView,PatientUpdateView, PatientDeleteView, DocumentCreateView,DocumentUploadView, PatientProfileView,DisplayResponseView, SearchPageView, TestResultUpdateView

urlpatterns = [
   path('', home, name='home'),
   path('about/', about, name='about'),
   path('create/', PatientCreateView.as_view(), name='patient_create'),
   path('update/<int:pk>', PatientUpdateView.as_view(), name='patient_update'),
   path('delete/<int:pk>', PatientDeleteView.as_view(), name='patient_delete'),
   path('detail/<int:pk>', PatientProfileView.as_view(), name='patient_profile'),
   path('upload/<int:pk>', DocumentUploadView.as_view(), name='document_upload'),
   path('response/<int:patient_id>/<int:document_id>', DisplayResponseView.as_view(), name='response'),
   path('search/', SearchPageView.as_view(), name='search'),
   path('generatedreport/<int:pk>', GenerateReportView.as_view(), name='generated_report'),
   path('testresultupdate/<int:pk>',TestResultUpDateView.as_view(), name='testresult_update')
   # path('testresult_update/<int:pk>',TestResultUpdateView.as_view(), name='patient_update')


]
