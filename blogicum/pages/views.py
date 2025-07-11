from django.shortcuts import render
from django.views.generic import TemplateView


class AboutTempalateView(TemplateView):
    template_name = 'pages/about.html'


class RulesTempalateView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found_500(request):
    return render(request, 'pages/500.html', status=500)
