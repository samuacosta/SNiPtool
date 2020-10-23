import asyncio
import json
import sys
import time
from datetime import date

import requests
from bootstrap_modal_forms.generic import BSModalFormView
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from rest_framework import viewsets

import main.services as serv

from .forms import MutationBatchModelForm, VEPInputForm
from .models import MutationBatch, TestModel
from .serializers import TestModelSerializer

loop = asyncio.get_event_loop()


def home(request, batch=None):
    if request.method == 'POST':
        form = VEPInputForm(request.POST)
        if 'generate' in request.POST:
            data = request.POST.copy()
            querydata = data.get('querydata')
            querydata_separated = querydata.replace("\r\n", ",")
            genes_list = querydata_separated.split(',')

            # serv.generate_missense_mutations(genes_list)
            loop.run_in_executor(
                None, serv.generate_missense_mutations, genes_list)

            gen_message = "A new mutation batch is being generated, it will be available for selection shortly."
            vep_message = ""

            #mutations_list = list(mutations_dict.values())
            #results = [item for sublist in mutations_list for item in sublist]
        if 'vep' in request.POST:
            data = request.POST.copy()
            methods = data.get('methods')
            methods_separated = methods.replace("\r\n", ",")
            methods_list = methods_separated.split(',')

            # serv.ensembl_get_predictions(batch, methods_list)
            args_array = [str(batch)] + methods_list  # TODO
            loop.run_in_executor(
                None, serv.ensembl_get_predictions, args_array)

            gen_message = ""
            vep_message = "Task submitted to VEP, it will be available for visualisation shortly."

        if 'export' in request.POST:
            # TODO
            gen_message = ""
            vep_message = ""

    else:
        form = VEPInputForm()
        gen_message = ""
        vep_message = ""
    return render(request, 'main/home.html', {'form': form, 'batch': batch, 'gen_message': gen_message, 'vep_message': vep_message})


def about(request):
    context = {
        'test': "about"
    }
    return render(request, 'main/about.html', context)


class TestModelView(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer


class MutationBatchListVep(ListView):
    context_object_name = 'mutationbatches'
    template_name = 'main/batch_list_vep.html'
    form_class = MutationBatchModelForm
    success_message = 'Batch selected.'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return MutationBatch.objects.filter(status__in=['GENERATED', 'FINISHED']).order_by('-creation_datetime')

    def post(self, request):
        data = request.POST.copy()
        batch = data.get('pk')
        return redirect('batch_selected', batch=batch)


class MutationBatchListResults(ListView):
    context_object_name = 'mutationbatches'
    template_name = 'main/batch_list_results.html'
    form_class = MutationBatchModelForm
    success_message = 'Batch selected.'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return MutationBatch.objects.filter(status='FINISHED').order_by('-creation_datetime')

    def post(self, request):
        data = request.POST.copy()
        batch = data.get('pk')
        return redirect('batch_selected', batch=batch)
