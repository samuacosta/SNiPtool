from django.db import models
from django.urls import reverse

'''
Database models
'''


class MutationBatch(models.Model):
    name = models.CharField(max_length=50)
    genes = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    creation_datetime = models.DateTimeField()
    comment = models.TextField()

    def __eq__(self, other):
        return self.id == other.id


class Mutation(models.Model):
    hgvs = models.CharField(max_length=50)
    gene_symbol = models.CharField(max_length=20)
    ensembl_id = models.CharField(max_length=20)
    amino_acid_from = models.CharField(max_length=5)
    amino_acid_to = models.CharField(max_length=5)

    sift_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    polyphen_score = models.DecimalField(
        max_digits=4, decimal_places=2, null=True)

    lrt_score = models.CharField(max_length=200, null=True)
    mutationtaster_score = models.CharField(max_length=200, null=True)
    mutationassessor_score = models.CharField(max_length=200, null=True)
    fathmm_score = models.CharField(max_length=200, null=True)
    mutpred_score = models.CharField(max_length=200, null=True)
    cadd_raw = models.CharField(max_length=200, null=True)
    metasvm_score = models.CharField(max_length=200, null=True)
    provean_score = models.CharField(max_length=200, null=True)
    vest4_score = models.CharField(max_length=200, null=True)

    sift_prediction = models.CharField(max_length=200, null=True)
    polyphen_prediction = models.CharField(max_length=200, null=True)
    lrt_pred = models.CharField(max_length=200, null=True)
    mutationtaster_pred = models.CharField(max_length=200, null=True)
    mutationassessor_pred = models.CharField(max_length=200, null=True)
    fathmm_pred = models.CharField(max_length=200, null=True)
    metasvm_pred = models.CharField(max_length=200, null=True)
    provean_pred = models.CharField(max_length=200, null=True)

    consequence_terms = models.CharField(max_length=300, null=True)
    unified_score = models.DecimalField(
        max_digits=4, decimal_places=2, null=True)
    grantham_distance = models.IntegerField(null=True)
    batch = models.ForeignKey(MutationBatch, on_delete=models.CASCADE)
    modification_datetime = models.DateTimeField(null=True)

    def __eq__(self, other):
        return self.id == other.id


class TestModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


'''
Other
'''


class EnsemblIdsRequest(object):
    def __init__(self, ids):
        self.ids = ids


class EnsemblVepRequest(object):
    def __init__(self, hgvs_notations):
        self.hgvs_notations = hgvs_notations
