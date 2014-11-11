import os, csv

from django.contrib import admin
from django import forms
from django.conf import settings
from django.http import HttpResponse

from .models import SurveyResponse
from .fields import *


#from .forms import ReaderSurveySections
# def export_survey_as_csv(modeladmin, request, queryset):
#     opts = modeladmin.model._meta

#     response = HttpResponse(mimetype='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

#     writer = csv.writer(response)

#     field_names = modeladmin.get_survey_csv_headers()
#     writer.writerow(list(field_names))

#     for obj in queryset:
#         csv_data = modeladmin.get_survey_csv_data(obj.data)
#         data = [unicode(val).encode("utf-8","replace") for val in csv_data]    
#         writer.writerow(data)
    
#     return response

# export_survey_as_csv.short_description = "Export selected responses as CSV file"




# class SurveyResponseAdmin(admin.ModelAdmin):
#     list_display = ('email', 'timestamp', 'address')
#     list_per_page = 30
#     actions = [export_survey_as_csv]


#     def get_survey_csv_headers(self):
#         column_names = []
        
#         for num, actual_field_name, actual_field, actual_form in self.csv_data:
#             column_names.append(actual_field.label or actual_field_name)
        
#         return column_names


#     def get_survey_csv_data(self, survey_data):
#         values = []

#         column_names = []
        
        
#         for num, actual_field_name, actual_field, actual_form in self.csv_data:
#             column_names.append(actual_field.label or actual_field_name)
#             key = '%s' % (num + 1)
#             if survey_data and survey_data.has_key(key):
#                 form_data = survey_data.get(key)
#                 v = form_data.get(actual_field_name)
#                 rv = actual_field.get_csv_value(v)
#                 if rv:
#                     values.append(rv)
#                 else:
#                     values.append(v)
#             else:
#                 values.append('None')
        
#         return values


#     def get_survey_field_names(self):
#         return self.survey_field_names


#     def get_survey_methods(self):
#         return self.survey_methods


#     def __init__(self, model, admin_site):
#         survey_field_names = []
#         survey_methods = []
#         csv_data = []
#         for num, form in enumerate(ReaderSurveySections):
#             for field_name, field in form.base_fields.items():

#                 def get_formatted_data(num, field_name, field, form):
#                     key = '%s' % (num + 1)
#                     actual_field_name = field_name
#                     actual_field = field
#                     actual_form = form

#                     def get_actual_data(self):
#                         if self.data and self.data.has_key(key):
#                             data = self.data.get(key)
#                             v = data.get(actual_field_name)
#                             rv = actual_field.get_formatted_value(v)
#                             if rv:
#                                 return rv
#                             return v
                        
#                         return 'No answer'


#                     get_actual_data.short_description = '%s' % (actual_field.label or field_name)
#                     get_actual_data.allow_tags = True
#                     return get_actual_data
                

#                 def get_csv_data(num, field_name, field, form):
#                     key = '%s' % (num + 1)
#                     actual_field_name = field_name
#                     actual_field = field
#                     actual_form = form

#                     def get_actual_csv_data(self):
#                         if self.data and self.data.has_key(key):
#                             data = self.data.get(key)
#                             v = data.get(actual_field_name)
#                             rv = actual_field.get_csv_value(v)
#                             if rv:
#                                 return rv
#                             return v
                        
#                         return 'No answer'

#                     return get_actual_csv_data

                
#                 method_csv = "get_%s_for_csv" % field_name
#                 method_formatted = "get_%s_data" % field_name
#                 survey_field_names.append(field_name)
#                 survey_methods.append(method_formatted)
#                 csv_data.append((num, field_name, field, form))

#                 model.add_to_class(method_formatted, get_formatted_data(num, field_name, field, form))
#                 model.add_to_class(method_csv, get_csv_data(num, field_name, field, form))
        
#         l =  list(self.list_display)
#         l.extend(survey_methods)
#         self.list_display = tuple(l)
#         self.survey_field_names = survey_field_names
#         self.survey_methods = survey_methods
#         self.csv_data = csv_data

#         super(SurveyResponseAdmin, self).__init__(model, admin_site)


# admin.site.register(SurveyResponse, SurveyResponseAdmin)
# admin.site.add_action(export_as_csv_action("CSV Export", fields=["email"], header=False), "export csv")