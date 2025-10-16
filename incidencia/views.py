from django.shortcuts import render, get_object_or_404
from .models import Incidencia

def lista_incidencias(request):
    incidencias = Incidencia.objects.all()
    return render(request, 'incidencia/lista.html', {'incidencias': incidencias})

def detalle_incidencia(request, id):
    incidencia = get_object_or_404(Incidencia, id=id)
    return render(request, 'incidencia/detalle.html', {'incidencia': incidencia})
