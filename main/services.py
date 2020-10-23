import datetime
import os
import sys

import requests
from django.utils import dateformat, timezone
from rest_framework.renderers import JSONRenderer

import main.constants as const

from .models import (EnsemblIdsRequest, EnsemblVepRequest, Mutation,
                     MutationBatch)
from .serializers import EnsemblCdsSerializer, EnsemblVepSerializer


def ensembl_get_predictions(args):
    # def ensembl_get_predictions(batch_id, methods_list):

    # Get parameters
    batch_id = args[0]
    methods_list = args[1:]

    static_dir = os.path.dirname(__file__) + '/static/main/'
    mane_file = static_dir + 'MANE.GRCh38.v0.9.summary.txt'  # TODO
    mane_dict_by_symbol, mane_dict_by_enid = load_mane_transcript_ids(
        mane_file)

    batch = MutationBatch.objects.get(pk=batch_id)
    genes = batch.genes.split(", ")
    for gene_symbol in genes:
        ensembl_get_predictions_gene(
            batch_id, methods_list, mane_dict_by_symbol[gene_symbol])
    update_mutation_batch(batch_id, 'FINISHED')

    return True, None


def ensembl_get_predictions_gene(batch_id, methods_list, transcript_id):

    ext = 'vep/human/hgvs?transcript_id=' + transcript_id
    if methods_list:
        ext += '&dbNSFP=' + ','.join(methods_list)
    update_mutation_batch(batch_id, 'RUNNING_VEP')
    count = 0
    limit = 200  # Ensembl restriction
    queryset = Mutation.objects.filter(
        batch=batch_id, modification_datetime=None, ensembl_id=transcript_id)[:limit]
    while queryset:
        mutations = [item.hgvs for item in queryset]
        mutations_request = EnsemblVepRequest(mutations)
        serializer = EnsemblVepSerializer(mutations_request)
        json = JSONRenderer().render(serializer.data)
        response = requests.post(const.ENSEMBL_REST_API_URL+ext,
                                 headers=const.ENSEMBL_HEADERS, data=json)
        if not response.ok:
            print('Error with Ensembl REST service: status_code=' +
                  str(response.status_code) + ', reason=' + response.reason)
            return False, response.reason
        else:
            json_content = response.json()
            for item in json_content:
                id_ens = item['id']
                tc = item['transcript_consequences']
                for consequence in tc:
                    terms = consequence['consequence_terms']
                    transc = consequence['transcript_id']
                    queryset_upd = Mutation.objects.filter(
                        batch=batch_id, hgvs=id_ens, ensembl_id=transc)
                    if queryset_upd:

                        mutation = queryset_upd[0]

                        mutation.sift_score = consequence['sift_score'] if 'sift_score' in consequence else None
                        mutation.sift_prediction = consequence[
                            'sift_prediction'] if 'sift_prediction' in consequence else None
                        mutation.polyphen_score = consequence[
                            'polyphen_score'] if 'polyphen_score' in consequence else None
                        mutation.polyphen_prediction = consequence[
                            'polyphen_prediction'] if 'polyphen_prediction' in consequence else None
                        mutation.lrt_score = consequence['lrt_score'] if 'lrt_score' in consequence else None
                        mutation.lrt_pred = consequence['lrt_pred'] if 'lrt_pred' in consequence else None
                        mutation.mutationtaster_score = consequence[
                            'mutationtaster_score'] if 'mutationtaster_score' in consequence else None
                        mutation.mutationtaster_pred = consequence[
                            'mutationtaster_pred'] if 'mutationtaster_pred' in consequence else None
                        mutation.mutationassessor_score = consequence[
                            'mutationassessor_score'] if 'mutationassessor_score' in consequence else None
                        mutation.mutationassessor_pred = consequence[
                            'mutationassessor_pred'] if 'mutationassessor_pred' in consequence else None
                        mutation.fathmm_score = consequence[
                            'fathmm_score'] if 'fathmm_score' in consequence else None
                        mutation.fathmm_pred = consequence['fathmm_pred'] if 'fathmm_pred' in consequence else None
                        mutation.mutpred_score = consequence[
                            'mutpred_score'] if 'mutpred_score' in consequence else None
                        mutation.cadd_raw = consequence['cadd_raw'] if 'cadd_raw' in consequence else None
                        mutation.metasvm_score = consequence[
                            'metasvm_score'] if 'metasvm_score' in consequence else None
                        mutation.metasvm_pred = consequence[
                            'metasvm_pred'] if 'metasvm_pred' in consequence else None
                        mutation.provean_score = consequence[
                            'provean_score'] if 'provean_score' in consequence else None
                        mutation.provean_pred = consequence[
                            'provean_pred'] if 'provean_pred' in consequence else None
                        mutation.vest4_score = consequence['vest4_score'] if 'vest4_score' in consequence else None

                        mutation.consequence_terms = ', '.join(terms)
                        mutation.modification_datetime = timezone.now()
                        mutation.save()

            count += 200
            now_str = dateformat.format(datetime.datetime.now(), 'd/m/Y H:i:s')
            print(now_str + ' Batch ' + str(batch_id) + ', transcript ' +
                  transcript_id + ', mutations processed: ' + str(count))
            queryset = Mutation.objects.filter(
                batch=batch_id, modification_datetime=None, ensembl_id=transcript_id)[:limit]


def generate_missense_mutations(args):
    # def generate_missense_mutations(genes_list):
    genes_list = args
    missense_mutations = {}
    static_dir = os.path.dirname(__file__) + '/static/main/'
    mane_file = static_dir + 'MANE.GRCh38.v0.9.summary.txt'  # TODO
    mane_dict_by_symbol, mane_dict_by_enid = load_mane_transcript_ids(
        mane_file)
    transc_ids_ensembl = []
    for gene_symbol in genes_list:
        transc_ids_ensembl.append(mane_dict_by_symbol[gene_symbol])
    cds_dict = ensembl_get_cds(EnsemblIdsRequest(transc_ids_ensembl))

    batch = create_mutation_batch(genes_list)
    for enid in cds_dict:
        missense_mutations[enid] = get_possible_missense_mutations(
            enid, mane_dict_by_enid[enid], cds_dict[enid], batch)
    update_mutation_batch(batch.id, 'GENERATED')
    return missense_mutations


def create_mutation_batch(genes_list):
    now = timezone.now()
    now_str = now.strftime("%Y%m%d_%H%M%S")
    mutation_batch = MutationBatch(
        name='Batch_'+now_str,
        genes=', '.join(genes_list),
        status='GENERATING',
        creation_datetime=now
    )
    mutation_batch.save()
    return mutation_batch


def update_mutation_batch(batch_id, status):
    batch = MutationBatch.objects.get(pk=batch_id)
    batch.status = status
    batch.save()


def load_mane_transcript_ids(filename):
    mane_dict_by_symbol = {}
    mane_dict_by_enid = {}
    with open(filename) as file:
        file.readline()  # Ignore header
        line = file.readline()
        while line:
            gene_symbol = line.split("\t")[3]
            transc_ensembl_id = line.split("\t")[7].split(
                ".")[0]  # Mane transcript id without version
            mane_dict_by_symbol[gene_symbol] = transc_ensembl_id
            mane_dict_by_enid[transc_ensembl_id] = gene_symbol
            line = file.readline()
    return mane_dict_by_symbol, mane_dict_by_enid


def ensembl_get_cds(transc_ids_ensembl_request):
    cds_dict = {}
    ext = 'sequence/id?type=cds'
    serializer = EnsemblCdsSerializer(transc_ids_ensembl_request)
    json = JSONRenderer().render(serializer.data)
    response = requests.post(const.ENSEMBL_REST_API_URL+ext,
                             headers=const.ENSEMBL_HEADERS, data=json)
    if not response.ok:
        print('Error with Ensembl REST service: status_code=' +
              str(response.status_code) + ', reason=' + response.reason)
        return None
    else:
        json_content = response.json()
        for item in json_content:
            cds_dict[item['id']] = item['seq']
        return cds_dict


def get_possible_missense_mutations(enid, gene_symbol, cds, batch):
    name = enid + ":c."
    start_position = 1
    static_dir = os.path.dirname(__file__) + '/static/main/'
    grantham_distances_file = static_dir + 'grantham_distances.csv'  # TODO
    genetic_code = load_genetic_code(static_dir + 'standard_genetic_code.csv')
    grantham_distances = load_grantham_distances(
        static_dir + 'grantham_distances.csv')
    aa_names, aa_letters = load_aa_dictionaries(
        static_dir + 'amino_acid_names.csv')
    alphabet = ['A', 'C', 'G', 'T']
    missense_mutations = []
    is_start_codon = True
    count = 0
    for i in range(0, len(cds)-len(cds) % 3, 3):
        # if is_start_codon:
        #     is_start_codon = False
        #     continue
        original_codon = cds[i:i+3].upper()
        original_aa = get_amino_acid(original_codon, genetic_code)
        for j in range(3):
            original_nucleotide = original_codon[j]
            for new_nucleotide in alphabet:
                new_codon = replace_nucleotide(
                    original_codon, j, new_nucleotide)
                new_aa = get_amino_acid(new_codon, genetic_code)
                if new_aa is not None and "" != new_aa and new_aa != original_aa and new_aa != '*':
                    info = aa_names[original_aa] + ">" + aa_names[new_aa]
                    mutation_str = name + \
                        str(start_position+i+j) + original_nucleotide.upper() + \
                        ">" + new_nucleotide.upper()
                    missense_mutations.append(mutation_str)
                    gdistance = get_grantham_distance(
                        grantham_distances, original_aa, new_aa)
                    insert_mutation(mutation_str, gene_symbol, enid,
                                    aa_names[original_aa], aa_names[new_aa], batch, gdistance)
                    count += 1
                    if count % 1000 == 0:
                        now_str = dateformat.format(
                            datetime.datetime.now(), 'd/m/Y H:i:s')
                        print(now_str + ' Batch ' + str(batch.id) + ', gene: ' +
                              gene_symbol + ', generated mutations: ' + str(count))
    return missense_mutations


def insert_mutation(hgvs, gene_symbol, enid, amino_acid_from, amino_acid_to, batch, gdistance):
    mutation = Mutation(
        hgvs=hgvs,
        gene_symbol=gene_symbol,
        ensembl_id=enid,
        amino_acid_from=amino_acid_from,
        amino_acid_to=amino_acid_to,
        grantham_distance=gdistance,
        batch=batch)
    mutation.save()


def get_grantham_distance(grantham_distances, original_aa, new_aa):
    if original_aa == '*' or new_aa == '*':
        return None
    else:
        grantham_distance = grantham_distances[(original_aa, new_aa)]
        return grantham_distance


def load_genetic_code(genetic_code_filename):
    genetic_code = {}
    file = open(genetic_code_filename, 'r')
    for line in file.readlines():
        codon = line.split(",")[0]
        amino_acid = line.split(",")[1].strip()
        genetic_code[codon] = amino_acid
    return genetic_code


def load_aa_dictionaries(aa_names_filename):
    names_from_letters = {}
    letters_from_names = {}
    file = open(aa_names_filename, 'r')
    for line in file.readlines():
        amino_acid_letter = line.split(",")[0]
        amino_acid_name = line.split(",")[1].strip()
        names_from_letters[amino_acid_letter] = amino_acid_name
        letters_from_names[amino_acid_name] = amino_acid_letter
    return names_from_letters, letters_from_names


def get_amino_acid(codon, genetic_code):
    amino_acid = genetic_code.get(codon)
    if amino_acid is not None and "" != amino_acid:
        return amino_acid
    else:
        # print("Warning: Unknown amino acid found for codon: " + codon)
        # return "X"
        return None


def replace_nucleotide(codon, position, new_nucleotide):
    return codon[:position] + new_nucleotide + codon[position + 1:]


def load_grantham_distances(grantham_distances_filename):
    grantham_distances = {}
    file = open(grantham_distances_filename, 'r')
    for line in file.readlines():
        amino_acid_from = line.split(",")[0]
        amino_acid_to = line.split(",")[1]
        distance = line.split(",")[2].strip()
        grantham_distances[(amino_acid_from, amino_acid_to)] = distance
    return grantham_distances
