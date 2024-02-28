from django.shortcuts import render
from django.views import View
# Create your views here.


class FormBuilder(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request=request, template_name='form/builder.html', context=context)


class MentorContactRecordForm(View):

    def get(self, request, *args, **kwargs):
        context = {
            'form': {
                'sections': [
                    {'name': 'Mentor/Mentee Information',
                     'fields': [{'name': 'date', 'type': 'date', 'row': 1,
                                 'label': 'date', 'placeholder': 'Date'},
                                {'name': 'Session Type', 'type': 'select', 'row': 1,
                                 'label': 'session type', 'placeholder': 'session type', "choices": ['a', 'b', 'c']}]
                     },
                    {'name': 'What did you get your help with ? '},
                ],
                'name': '',
                'id': '',
            }
        }

        return render(request=request, template_name='form/view.html', context=context)
