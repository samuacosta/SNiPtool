import requests
import sys
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from rest_framework import viewsets
from .models import TestModel
from .serializers import TestModelSerializer
from .forms import VEPInputForm


def home(request):
    if request.method == 'POST':
        form = VEPInputForm(request.POST)
        data = request.POST.copy()
        querydata = data.get('querydata')
        querydata_separated = "\"" + querydata.replace("\r\n", "\", \"") + "\""
        final_data = "{ \"hgvs_notations\" : [ " + \
            querydata_separated + " ] }"
        server = "http://rest.ensembl.org"
        ext = "/vep/human/hgvs"
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}
        response = requests.post(server+ext, headers=headers, data=final_data)
        json_content = response.json()
        missense_list = []
        for item in json_content:
            tc = item['transcript_consequences']
            for consequence in tc:
                ct = consequence['consequence_terms']
                if 'missense' in ct[0]:
                    missense_list.append(
                        "SIFT score: " + str(consequence['sift_score']) + "; SIFT prediction: " + consequence['sift_prediction'])
                    missense_list.append(
                        "PolyPhen score: " + str(consequence['polyphen_score']) + "; PolyPhen prediction: " + consequence['polyphen_prediction'])
        results = missense_list

    else:
        form = VEPInputForm()
        results = ['Please submit query']
    return render(request, 'main/home.html', {'form': form, 'results': results})


def about(request):
    context = {
        'test': "hello"
    }
    return render(request, 'main/about.html', context)


class TestModelView(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer
