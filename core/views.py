from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def main_menu(request,):

    context_dict = dict(request=request, )
    return render_to_response("main.html", context_dict)


@login_required(login_url='/login/')
def reference(request,):

    context_dict = dict(request=request, )
    return render_to_response("reference.html", context_dict)
