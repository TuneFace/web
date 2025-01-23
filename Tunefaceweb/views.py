from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.contrib import messages
from google.cloud import storage
from firebase_admin import firestore
from .forms import UsuarioTunefaceForm
from django.conf import settings
from django.core.exceptions import ValidationError
import cloudinary.uploader
import uuid
import os
from django.urls import reverse_lazy
import logging

#LOGS
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Instancia de Firestore
db = firestore.client()

# Configuración para Firebase Storage
#storage_client = storage.Client()
#bucket_name = "tu-bucket-name" ##cambiar 
#bucket = storage_client.bucket(bucket_name)

#def upload_image(file):
#    if not file.content_type.startswith('image/'):
#        raise ValidationError("El archivo subido no es una imagen válida.")
    
#    unique_name = f"{uuid.uuid4()}-{file.name}"
#    blob = bucket.blob(f"usuarios/{unique_name}")
#    blob.upload_from_file(file)
#    blob.make_public()
#    return blob.public_url

def upload_image(file): # Subir la imagen a cloudinary / cambiar luego por metodo firestore
    if not file.content_type.startswith('image/'):
        raise ValidationError("El archivo subido no es una imagen válida.")
    
    # Subir la imagen a Cloudinary
    response = cloudinary.uploader.upload(file)
    return response['secure_url']

def index(request):
    canciones_docs = db.collection('canciones').stream()
    if request.method == 'POST':
        logger.info(f'Archivos recibidos: {request.FILES}')
        form = UsuarioTunefaceForm(request.POST, request.FILES)
        if form.is_valid():
            # Preparar los datos para Firestore
            nombre = form.cleaned_data['nombre']
            local = form.cleaned_data['local']
            canciones = form.cleaned_data['canciones']
            if len(canciones) > 3:
                messages.error(request, 'Solo puedes seleccionar hasta 3 canciones.')
                return redirect('index')
            imagenes = request.FILES.getlist('imagenes')

            # Subir la imagen 
            image_urls = []
            for imagen in imagenes:
                print(imagen.name)
                image_url = upload_image(imagen)
                image_urls.append(image_url)

            # Guardar en Firestore
            db.collection('usuarios').add({
                'nombre': nombre,
                'local': local,
                'canciones': canciones,
                'imagenes': image_urls, 
            })

            messages.success(request, 'Usuario ingresado correctamente')
            return redirect('index')
        else:
            logger.error('Error al ingresar usuario: %s', form.errors)
            messages.error(request, 'Error al ingresar usuario')
    else:
        form = UsuarioTunefaceForm()

    # Preparar el contexto de canciones
    canciones_context = [
        {
            'id': doc.id,  # ID del documento
            'titulo': doc.to_dict().get('titulo', 'Sin Título'),
            'imagen_url': doc.to_dict().get('imagen_url', ''),
        }
        for doc in canciones_docs
    ]

    # Combinar los contextos
    context = {
        'form': form,
        'canciones': canciones_context,
    }

    return render(request, 'index.html', context)