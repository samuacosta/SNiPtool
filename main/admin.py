from django.contrib import admin

from .models import Mutation, MutationBatch

admin.site.register(Mutation)
admin.site.register(MutationBatch)
