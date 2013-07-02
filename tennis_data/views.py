from django.http import HttpResponse
from tennis_data.tasks import PopulateDatabase


def warmup(request):
    PopulateDatabase()
    return HttpResponse("db populated")
