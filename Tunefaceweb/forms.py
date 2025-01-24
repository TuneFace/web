from django import forms
from firebase_admin import firestore
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError


db = firestore.client()

class SongSelectMultipleWidget(forms.SelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        if value is None:
            value = ''
        option_dict = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        # Procesar HTML seguro en el label
        if label and isinstance(label, str):
            option_dict['label'] = mark_safe(label)
        return option_dict

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True, 'class': 'form-control form-group', 'id': 'imagenes'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
    
def obtener_opciones_locales():
    docs = db.collection('locales').stream()
    opciones = [(doc.id, doc.to_dict().get('nombre', 'Sin Nombre')) for doc in docs]
    if not opciones: 
        opciones.append(('', 'No hay locales disponibles'))
    return opciones

def obtener_opciones_canciones():
    docs = db.collection('canciones').stream()
    opciones = []
    for doc in docs:
        data = doc.to_dict()
        titulo = data.get('titulo', 'Sin Título')
        imagen_url = data.get('imagen_url', '')
        label = f'<img src="{imagen_url}" style="width:30px; height:30px; margin-right:10px;"> {titulo}' if imagen_url else titulo
        opciones.append((doc.id, label)) 
    if not opciones:
        opciones.append(('', 'No hay canciones disponibles'))
    return opciones

def clean_canciones(self):
        canciones = self.cleaned_data.get('canciones', [])
        if len(canciones) > 3:
            raise ValidationError('No puedes seleccionar más de 3 canciones.')
        return canciones

def clean_imagenes(self):
        files = self.files.getlist('imagenes')  
        if not files:
            raise forms.ValidationError("No se seleccionó ninguna imagen.")
        for file in files:
            if not file.content_type.startswith('image/'):
                raise forms.ValidationError(f"El archivo {file.name} no es una imagen válida.")
        return files

class UsuarioTunefaceForm(forms.Form):
    CANCIONESCHOICES = obtener_opciones_canciones()
    LOCALCHOICES = obtener_opciones_locales()

    nombre = forms.CharField(max_length=100, label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control form-group'}))
    local = forms.ChoiceField(
        choices=LOCALCHOICES,
        label="Local",
        widget=forms.Select(attrs={
            'class': 'form-select form-group',
            'aria-label': 'Default select example',
        }),
    )
    imagenes = MultipleFileField(
        label="Imágenes",
        required=False  # Cambia a True si es obligatorio
    )
    canciones = forms.MultipleChoiceField(
        choices=CANCIONESCHOICES,
        widget=SongSelectMultipleWidget(),
        label="Canciones"
    )

    