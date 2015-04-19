from django.http import HttpResponse, Http404
from django.core.files.storage import DefaultStorage


def file_view(request, filename=None):
    storage = DefaultStorage()
    try:
        file = storage.open(filename, 'rb')
        file_content = file.read()
        return HttpResponse(file_content, content_type="application/octet-stream")
    except Exception as e:
        raise Http404(e)
