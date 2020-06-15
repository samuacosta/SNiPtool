from django import forms


class VEPInputForm(forms.Form):
    querydata = forms.CharField(max_length=2000,
                                label='Query data',
                                initial='AGT:c.803T>C\n9:g.22125504G>C',
                                widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}))
