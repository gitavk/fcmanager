from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/login/')
def main_menu(request,):

	context_dict = dict(request=request, )
	# context_dict.update(csrf(request))
	return render_to_response("main.html", context_dict)

# Create your views here.
@login_required(login_url='/login/')
def reference(request,):

	context_dict = dict(request=request, )
	# context_dict.update(csrf(request))
	return render_to_response("reference.html", context_dict)