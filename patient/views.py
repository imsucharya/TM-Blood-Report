from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import View
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin #classs based views
from django.contrib.auth.decorators import login_required # fucntion based views

# local imports
from .process import main

# models
from .models import Patient, Document, TestResult, Label, AlternateLabel, Category

# forms
from .forms import DocumentForm, SearchForm

# general imports
from collections import defaultdict

# Create your views here

@login_required(login_url='login')
def home(request):
    template_name = 'patient/home.html'
    context = {
        'patient': Patient.objects.all()
    }
    return render(request, template_name=template_name, context=context)


class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    template_name = 'patient/patient_create.html'
    fields = ('fname', 'lname', 'address', 'zip')  # '__all__'
    success_message = "Patient was added successfully"

    def get_success_url(self):
        return reverse('patient_profile', kwargs={'pk': self.object.pk})


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    # reused PatientCrateView template
    template_name = 'patient/patient_create.html'
    fields = "__all__"

    def get_success_url(self):
        return reverse('patient_update', kwargs={'pk': self.object.pk})

# delete
class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = Patient
    template_name = 'patient/patient_delete.html'
    fields = "__all__"

    def get_success_url(self):
        return reverse('home')


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    template_name = 'patient/document_create.html'
    fields = ('name', 'document')

    def get_success_url(self):
        return reverse('home')


class DocumentUploadView(LoginRequiredMixin, View):
    template_name = 'patient/document_upload.html'

    def get(self, request, pk):
        form = DocumentForm()
        context = {
            'form': form,
            'pk': pk
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        patient = Patient.objects.get(pk=pk)
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.patient = patient
            form.save()

            # getting data from document
            data = main(form.document.path)  # return string
            data = eval(data)
            print(data)
            # saving data into db
            for item in data:
                print(item)
                name = item['name']
                value = item['Value']
                unit = item['Unit']
                alternate_label= AlternateLabel.objects.filter(name__iexact=name).first()
                try:
                    testresult, created = TestResult.objects.get_or_create(
                        label = alternate_label.label,
                        unit=unit,
                        value=value,
                        patient=patient,
                        document=form
                    ) 
                    if created:
                        testresult.save()
                except Exception as e:
                    print(e)
                    pass

            # print(data)

        # context = {
        #     'form' : DocumentForm(),
        #     'pk' : pk,
        #     'data' : data
        # }
        return redirect(reverse('response', kwargs={'patient_id': patient.id, 'document_id': form.id}))


class DisplayResponseView(LoginRequiredMixin, View):
    template_name = 'patient/display_response.html'

    def get(self, request, patient_id, document_id):
        patient_obj = Patient.objects.get(pk=patient_id)
        document_obj = Document.objects.get(pk=document_id)
        all_testresult = TestResult.objects.filter(patient=patient_obj, document=document_obj)

        context = {
            'all_testresult': all_testresult,
            'patient': patient_obj,
        }
        return render(request, self.template_name, context)


class PatientProfileView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'patient/patient_detail.html'
    context_object_name = 'patient'


class SearchPageView(LoginRequiredMixin, View):
    template_name = 'patient/patient_search_page.html'
    form = SearchForm()

    def get(self, request):
        all_patient = Patient.objects.all()
        context = {
            'all_patient': all_patient,
            'form': self.form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SearchForm(request.POST)
        context = {}
        if form.is_valid():
            #valid .cleaned_data
            search_key = form.cleaned_data['search']
            data = Patient.objects.filter(
                Q(fname__icontains=search_key)   |
                Q(lname__icontains=search_key)   |
                Q(address__icontains=search_key)   |
                Q(zip__icontains=search_key)   
            )
            context = {
                'form':self.form,
                'all_patient':data
            }
        return render(request, self.template_name,context)


class GenerateReportView(LoginRequiredMixin, View):
    template_name = 'patient/patient_generated_report.html'

    # helper funtion
    def get_all_label(self, doc1=None, doc2=None, doc3=None, doc4=None, doc5=None):
        # return union of all labels present in all five document

        # do your work here
        if doc1 is not None:
            testresult1 = TestResult.objects.filter(document=doc1)
            result1_labels = {result.label: {
                'value': result.value, 'unit': result.unit} for result in testresult1}
        else:
            result1_labels = {}

        if doc2 is not None:
            testresult2 = TestResult.objects.filter(document=doc2)
            result2_labels = {result.label: {
                'value': result.value, 'unit': result.unit} for result in testresult2}
        else:
            result2_labels = {}

        if doc3 is not None:
            testresult3 = TestResult.objects.filter(document=doc3)
            result3_labels = {result.label: {
                'value': result.value, 'unit': result.unit} for result in testresult3}
        else:
            result3_labels = {}

        if doc4 is not None:
            testresult4 = TestResult.objects.filter(document=doc4)
            result4_labels = {result.label: {
                'value': result.value, 'unit': result.unit} for result in testresult4}
        else:
            result4_labels = {}

        if doc5 is not None:
            testresult5 = TestResult.objects.filter(document=doc5)
            result5_labels = {result.label: {
                'value': result.value, 'unit': result.unit} for result in testresult5}
        else:
            result5_labels = {}
        print("this is result label")
        print(result1_labels)
        print(result2_labels)
        print(result3_labels)
        print(result4_labels)
        print(result5_labels)

        all_label = list(set(
            result1_labels.keys() | result2_labels.keys() | result3_labels.keys(
            ) | result4_labels.keys() | result5_labels.keys()
        ))

        all_categories = [category.name for category in Category.objects.all().order_by('priority')]
        present_category = list(set(label.category.name for label in all_label))
        all_category = [category for category in all_categories if category in present_category]
        
        return all_label, all_category

    def create_comparison(self, prev_report, present_report, all_label):
        
        remark_color = {
            'White'         :'#ffffff',
            'Yellow'        :'#FFFF00',
            'Pale_Yellow'   :'#FE2E2E',
            'Green'         :'#31B404',
            'Pale_Green'    :'#82FA58',
            'Red'           :'#FF0000',
            'Maroon'        :'#800000'
        }

        # if there is only one document
        is_single_document = False
        if (prev_report is None) and (present_report is not None):  # if there is not prev report
            is_single_document = True

        print('is_single', is_single_document)
        # getting all testresult associated with both document
        # storing all values n dct in {label: {value, unit}} format
        if prev_report is not None:
            testresult1 = TestResult.objects.filter(document=prev_report)
            result1_labels = {result.label: {'value': float(
                result.value), 'unit': result.unit} for result in testresult1}
        else:
            result1_labels = {}
        if present_report is not None:
            testresult2 = TestResult.objects.filter(document=present_report)
            result2_labels = {result.label: {'value': float(
                result.value), 'unit': result.unit} for result in testresult2}
        else:
            result2_labels = {}

        table = defaultdict(dict)
        for label in all_label:
            label_name = label.name
            category = label.category.name
            doc1 = result1_labels.get(label, None)
            doc2 = result2_labels.get(label, None)

            if doc1 is not None:
                doc1_value = doc1.get('value', 0)
            else:
                doc1_value = None

            if doc2 is not None:
                doc2_value = doc2.get('value', 0)
            else:
                doc2_value = None

            lower_range = label.lower_range
            upper_range = label.upper_range

            table[label_name]['value'] = doc2_value
            table[label_name]['category'] = category

            if is_single_document:
                try:
                    if doc2_value < lower_range:
                        table[label_name]['remark'] = 'Low'
                        table[label_name]['remark_color'] = remark_color['Yellow']
                        print('this is single lower remark color',
                              table[label_name]['remark_color'])
                    elif lower_range <= doc2_value <= upper_range:
                        table[label_name]['remark'] = 'Normal'
                        table[label_name]['remark_color'] = remark_color['Green']
                        print('this is single normal remark color',
                              table[label_name]['remark_color'])
                    else:
                        table[label_name]['remark'] = 'High'
                        table[label_name]['remark_color'] = remark_color['Red']
                        print('this is single high remark color',
                              table[label_name]['remark_color'])
                except Exception as e:
                    table[label_name]['remark'] = '-'
                    table[label_name]['remark_color'] = ''
                    print('lower_range, upper_range error', e)

            # if label exist for both docs
            elif (doc1 is not None) and (doc2 is not None):
                doc2_value = doc2.get('value', 0)
                doc1_value = doc1.get('value', 0)
                value_change = doc2_value - doc1_value
                try:
                    # previos value was low
                    if doc1_value < label.lower_range:
                        # value has gone lower (a)
                        if value_change < 0:
                            table[label_name]['remark'] = 'Need work'
                            table[label_name]['remark_color'] = remark_color['Pale Yellow']
                        # value is same (b)
                        elif value_change == 0:
                            table[label_name]['remark'] = 'Need work'
                            table[label_name]['remark_color'] = remark_color['Yellow']
                        # val is low but not normal (e)
                        elif value_change > 0 and doc2_value < lower_range:
                            table[label_name]['remark'] = 'Improved, Need work'
                            table[label_name]['remark_color'] = remark_color['Pale Green']
                        # val is normal (c)
                        elif lower_range <= doc2_value <= upper_range:
                            table[label_name]['remark'] = 'Improved'
                            table[label_name]['remark_color'] = remark_color['Green']
                        # val has becomne higher (d)
                        elif upper_range < doc2_value:
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Red']

                    # if value was normal
                    elif lower_range <= doc1_value <= upper_range:
                        print('value is normal')
                        if value_change < 0:  # val has gone low
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Yellow']
                        elif lower_range <= doc2_value <= upper_range:
                            table[label_name]['remark'] = ''
                            table[label_name]['remark_color'] = remark_color['White']
                        elif upper_range < doc2_value:
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Red']
                        # print(table[label_name]['remark_color'], 'remark_color')

                    # if value was high
                    elif upper_range < doc1_value:
                        if value_change > 0:  # val has gone higher
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Maroon']
                        elif value_change < 0 and upper_range < doc2_value:  # if val is lower than before still high
                            table[label_name]['remark'] = 'Improved, Need Work'
                            table[label_name]['remark_color'] = remark_color['Pale Green']
                        elif lower_range <= doc2_value <= upper_range:
                            table[label_name]['remark'] = 'Improved'
                            table[label_name]['remark_color'] = remark_color['Green']
                        elif doc2_value < lower_range:
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Yellow']
                        # print(table[label_name]['remark_color'], 'remark_color')
                except Exception as e:
                    table[label_name]['remark'] = '-'
                    table[label_name]['remark_color'] = ''
                    print('No lower upper range error',  label_name, e)

            else:  # when label exist for only one doc
                table[label_name]['remark'] = '-----'
                table[label_name]['remark_color'] = ''
        # table data type from defaultdict to dict
        table = dict(table)
        return table




    def get(self, request, pk):
        patient = Patient.objects.get(pk=pk)
        all_document = Document.objects.filter(
            patient=patient).order_by('-uploaded_at')
        doc1_obj, doc2_obj, doc3_obj, doc4_obj, doc5_obj = None, None, None, None, None
        try:
            doc1_obj = all_document[0]
            doc2_obj = all_document[1]
            doc3_obj = all_document[2]
            doc4_obj = all_document[3]
            doc5_obj = all_document[4]

        except Exception as o:
            print(o)
            pass

        # get union of all labels in all 5 documents
        all_label, all_category = self.get_all_label(doc1_obj, doc2_obj, doc3_obj, doc4_obj, doc5_obj)
        print("this is all_label")

        # create a comparison function
        all_docs = [None, doc5_obj, doc4_obj, doc3_obj, doc2_obj, doc1_obj]
         
        table = {}
        for index, present_doc in enumerate(all_docs):
            if present_doc is None:
                continue

            prev_doc = all_docs[index-1]
            col = self.create_comparison(prev_doc, present_doc, all_label)
            table[index] = {
                'name': present_doc,
                'col': col
            }
            # print(index, col)
            
        print("this is table")
        print(table)

        row_wise_table = dict()
        for label in all_label:
            row_wise_table[label.name] = {
                index:{
                    'value' : table[index]['col'][label.name].get('value', None ),
                    'remark' : table[index]['col'][label.name].get('remark', None ),
                    'remark_color' : table[index]['col'][label.name].get('remark_color', None ),
                    'category': table[index]['col'][label.name].get('category', ''),
                }for index in table.keys()
            }
        row_wise_table['document'] = {}
        for doc_index in table.keys():
            row_wise_table['document'][doc_index] = table[doc_index]['name']
        row_wise_table['document']['all_category'] = all_category

        
        print(all_label)

        context = {
            'patient': patient,
            'row_wise_table': row_wise_table,
        }
        return render(request, self.template_name, context)


class TestResultUpDateView(LoginRequiredMixin, UpdateView): #TestResultUpdateView in video
    model = TestResult
    template_name = 'patient/testresult_update.html'
    fields = ('label', 'value', 'unit')

    def get_success_url(self) -> str:
        return reverse('response', kwargs={'patient_id':self.object.patient.pk, 'document_id':self.object.document.pk})


@login_required(login_url='login')
def about(request):
    return HttpResponse('about')


class TestResultUpdateView(LoginRequiredMixin, UpdateView):
    model = TestResult
    template_name = 'patient/testresult_update.html'
    fields = ('label', 'value', 'unit')

    def get_success_url(self) -> str:
        return reverse('home')
