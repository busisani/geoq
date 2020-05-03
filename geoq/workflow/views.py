# -*- coding: UTF-8 -*-

# Python
import subprocess
from os.path import join

# django
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

# Workflow app
from workflow.models import Workflow

###################
# Utility functions
###################

def get_dotfile(workflow):
    """
    Given a workflow will return the appropriate contents of a .dot file for 
    processing by graphviz
    """
    c = Context({'workflow': workflow})
    t = loader.get_template('graphviz/workflow.dot')
    return t.render(c)

################
# view functions
################

def dotfile(request, workflow_slug):
    """
    Returns the dot file for use with graphviz given the workflow name (slug) 
    """
    w = get_object_or_404(Workflow, slug=workflow_slug)
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.dot'%w.name
    response.write(get_dotfile(w))
    return response

def graphviz(request, workflow_slug):
    """
    Returns a png representation of the workflow generated by graphviz given 
    the workflow name (slug)

    The following constant should be defined in settings.py:

    GRAPHVIZ_DOT_COMMAND - absolute path to graphviz's dot command used to
    generate the image
    """
    if not hasattr(settings, 'GRAPHVIZ_DOT_COMMAND'):
        # At least provide a helpful exception message
        raise Exception("GRAPHVIZ_DOT_COMMAND constant not set in settings.py"\
                " (to specify the absolute path to graphviz's dot command)")
    w = get_object_or_404(Workflow, slug=workflow_slug)
    # Lots of "pipe" work to avoid hitting the file-system
    proc = subprocess.Popen('%s -Tpng' % settings.GRAPHVIZ_DOT_COMMAND,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                )
    response = HttpResponse(mimetype='image/png')
    response.write(proc.communicate(get_dotfile(w).encode('utf_8'))[0])
    return response