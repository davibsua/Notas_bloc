import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import uuid
from django.http import HttpResponseNotFound

# Ruta de los archivos de usuarios y notas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE_PATH = os.path.join(BASE_DIR, '..', 'data', 'usuarios.txt')
NOTES_DIR_PATH = os.path.join(BASE_DIR, '..', 'data', 'notas')


# Función para iniciar sesión
def iniciar_sesion(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        password = request.POST.get('password')
        notfound = None

        with open(USER_FILE_PATH, "r") as usuarios:
            contenido = usuarios.read()
            split_lines = contenido.splitlines()
            
            for line in split_lines:
                split_c = line.split("/")
                if user == split_c[0] and password == split_c[1]:
                    request.session['user'] = user  # Guardar el usuario en la sesión
                    return redirect('usuario')  # Redirigir a la página de usuario
            notfound = "Las credenciales son incorrectas"
        
        return render(request, 'bloc_notas/iniciar_sesion.html', {'notfound': notfound})

    return render(request, 'bloc_notas/iniciar_sesion.html')

# Función para crear cuenta
def crear_cuenta(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        password = request.POST.get('password')

        if user and password:
            with open(USER_FILE_PATH, "a") as usuarios:
                usuarios.write(f"{user}/{password}\n")
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('iniciar_sesion')
        else:
            messages.error(request, "Debes completar ambos campos.")
    
    return render(request, 'bloc_notas/crear_cuenta.html')

# Función para mostrar la página de usuario
def usuario(request):
    user = request.session.get('user')  # Obtener el usuario desde la sesión
    if user:
        notas = []
        # Crear una carpeta específica para cada usuario
        user_notes_folder = os.path.join(os.path.dirname(__file__), '..', 'data', 'notas', user)  # Usamos el nombre de usuario como la carpeta

        # Verificar si la carpeta del usuario existe, si no, crearla
        if not os.path.exists(user_notes_folder):
            os.makedirs(user_notes_folder)

        # Suponemos que cada nota tiene un archivo con el formato '<nota_id>_nota.txt'
        for nota_file in os.listdir(user_notes_folder):
            if nota_file.endswith('_nota.txt'):
                nota_id = nota_file.split('_')[0]  # ID único de la nota
                # Leer el título de la nota desde el archivo
                with open(os.path.join(user_notes_folder, nota_file), 'r') as f:
                    titulo = f.readline().strip().replace("Título: ", "")  # Extraer el título
                notas.append({'id': nota_id, 'titulo': titulo})  # Agregar el título al diccionario

        return render(request, 'bloc_notas/usuario.html', {'user': user, 'notas': notas})
    else:
        return redirect('iniciar_sesion')  # Redirigir al inicio de sesión si no hay sesión activa



def agregar_nota(request):
    user = request.session.get('user')  # Obtener el nombre de usuario de la sesión
    if not user:
        return redirect('iniciar_sesion')  # Redirigir si el usuario no ha iniciado sesión

    if request.method == 'POST':
        # Obtener título y contenido de la nota
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')

        if not titulo or not contenido:
            return render(request, 'notes/agregar_nota.html', {
                'error': 'El título y el contenido de la nota son obligatorios.'
            })

        # Crear un ID único para la nota
        nota_id = str(uuid.uuid4())

        # Ruta para guardar la nota en un archivo de texto
        directorio_usuario = os.path.join(os.path.dirname(__file__), '..', 'data', 'notas', user)
        os.makedirs(directorio_usuario, exist_ok=True)  # Asegurarse de que el directorio exista

        archivo_nota = os.path.join(directorio_usuario, f'{nota_id}_nota.txt')
        
        # Guardar el contenido de la nota en el archivo
        with open(archivo_nota, 'w', encoding='utf-8') as f:
            f.write(titulo + "\n" + contenido)

        return redirect('usuario')  # Redirigir al usuario a su página de notas

    # Si es un GET, mostrar el formulario para agregar nota
    return render(request, 'bloc_notas/agregar_nota.html')


def ver_nota(request, nota_id):
    user = request.session.get('user')  # Asegurarte de que el usuario esté en la sesión
    if not user:
        return redirect('iniciar_sesion')

    # Construir la ruta para acceder al archivo de la nota
    nota_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'notas', user, f'{nota_id}_nota.txt')

    try:
        # Abrir el archivo de la nota y leer todas sus líneas
        with open(nota_file_path, 'r') as f:
            lines = f.readlines()

        # Omitir la primera línea (el título) y juntar las restantes como contenido
        contenido = ''.join(lines[1:]).strip()
    except FileNotFoundError:
        # Si no se encuentra el archivo, se devuelve un error 404
        return HttpResponseNotFound('Nota no encontrada')

    # Renderizar la plantilla ver_nota.html y pasar solo el contenido de la nota
    return render(request, 'bloc_notas/ver_nota.html', {'contenido': contenido})


def cerrar_sesion(request):
    # Eliminar la sesión activa
    if 'user' in request.session:
        del request.session['user']  # Eliminar la clave de usuario de la sesión
    return redirect('iniciar_sesion')