from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms

from .models import MutationBatch


class VEPInputForm(forms.Form):
    querydata = forms.CharField(max_length=2000,
                                label='List of genes',
                                initial=('ATM\n'
                                         'BRCA1\n'
                                         'BRCA2\n'
                                         'CHEK2\n'
                                         'TP53\n'
                                         'MLH1\n'
                                         'MRE11\n'
                                         'MSH2\n'
                                         'MSH6\n'
                                         'NBN\n'
                                         'PALB2\n'
                                         'PMS2\n'
                                         'RAD50\n'
                                         'RAD51\n'
                                         'XRCC2'),
                                widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}))


class MutationBatchModelForm(BSModalModelForm):
    class Meta:
        model = MutationBatch
        fields = ['name', 'genes', 'status', 'creation_datetime']
