# Inicio para usar Flask y manejar sesiones
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps  # Para crear decoradores
from src.viewmodel.auth_viewmodel import UsuarioAuthViewModel 
from src.services.firebase_global import firebase_global  # Asegurarse de que este objeto ya tenga db inicializado
from src.viewmodel.usuarios_viewmodel import UsuarioViewModel
from src.viewmodel.grupos_viewmodel import GruposViewModel

usuario_vm = UsuarioViewModel()  # Inicializamos el ViewModel para manejar usuarios
auth_vm = UsuarioAuthViewModel()
grupos_vm = GruposViewModel()
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necesario para manejar sesiones


# ========================================================
# Decorador para verificar si el usuario ha iniciado sesión
# ========================================================
def login_requerido(f):
    """
    Verifica si el usuario tiene sesión activa.
    Si no, lo redirige a la página de inicio de sesión.
    """
    @wraps(f)
    def decorador(*args, **kwargs):
        if "usuario" not in session:
            flash("Debes iniciar sesión para acceder a esta página", "warning")
            return redirect(url_for("inicio_sesion"))
        return f(*args, **kwargs)  # Si hay sesión, continúa
    return decorador


# ========================================================
# Ruta principal: muestra home o dashboard según la sesión
# ========================================================
@app.route("/")
def index():
    usuario_actual = session.get("usuario")  # Revisamos si hay usuario logueado
    if usuario_actual:  # Usuario logueado → mostrar index_usuario.html
        return render_template("index_usuario.html", usuario=usuario_actual)
    else:  # No logueado → mostrar home normal
        return render_template("index.html")


# ========================================================
# Registro de usuario
# ========================================================
@app.route("/registro", methods=["GET", "POST"])
def registro_usuario():
    if request.method == "POST":
        nombre = request.form["name"]
        correo = request.form["correo"]
        password = request.form["password"]
        carrera = request.form["carrera"]

        resultado = auth_vm.registrar_usuario(nombre, correo, password, carrera)
        if resultado["success"]:
            flash("Registro exitoso", "success")
            return redirect(url_for("index"))
        else:
            flash(resultado["error"], "danger")
    return render_template("registrarse.html")


# ========================================================
# Inicio de sesión
# ========================================================
@app.route("/inicio_sesion", methods=["GET", "POST"])
def inicio_sesion():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]
        resultado = auth_vm.iniciar_sesion(correo, password)

        if resultado["success"]:
            # Convertimos el correo a la clave usada en Firebase
            correo_key = correo.replace(".", "_dot_").replace("@", "_at_")
            ruta = f"usuarios/{correo_key}"
            # Traemos los datos completos desde Firebase
            datos_usuario = firebase_global.obtener_datos(ruta)

            if datos_usuario is None:
                flash("No se encontraron datos del usuario en Firebase.", "danger")
                return redirect(url_for("inicio_sesion"))

            # Guardamos en sesión los datos reales del usuario
            session["usuario"] = {
                "correo": correo,
                "nombre": datos_usuario.get("nombre_completo", "Usuario"),  # Ahora sí será el nombre real
                "carrera": datos_usuario.get("carrera", "")
            }

            flash(f"Bienvenido, {session['usuario']['nombre']}!", "success")
            return redirect(url_for("index"))  # Redirige al dashboard automáticamente
        else:
            flash(resultado["error"], "danger")

    return render_template("iniciar_sesion.html")



# ========================================================
# Cerrar sesión
# ========================================================
@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.pop("usuario", None)  # Eliminamos la sesión
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("index"))


# ========================================================
# Rutas protegidas: solo accesibles si hay sesión activa
# ========================================================

@app.route("/eventos")
@login_requerido
def eventos():
    return render_template("eventos.html", usuario=session["usuario"])


# ========================================================
# Perfil
# ========================================================

@app.route("/perfil", methods=["GET", "POST"])
@login_requerido
def perfil():
    correo = session["usuario"]["correo"]

    if request.method == "POST":
        data = request.get_json()
        # Actualizamos usuario usando exactamente los argumentos que acepta el ViewModel
        resultado = usuario_vm.actualizar_usuario(
            correo,
            nombre_completo=data.get("nombre_completo"),
            password=data.get("password"),  # coincide con el ViewModel
            carrera=data.get("carrera"),
            descripcion_personal=data.get("descripcion_personal")  # coincide con el ViewModel
        )

        if resultado["success"]:
            # Actualizamos la sesión para reflejar cambios
            session["usuario"].update({
                "nombre_completo": data.get("nombre_completo"),
                "carrera": data.get("carrera"),
                "bio": data.get("descripcion_personal")
            })
        return {"success": resultado["success"]}

    # GET → mostrar perfil
    usuario_obj = usuario_vm.obtener_usuario(correo)
    if not usuario_obj:
        flash("No se encontraron datos del usuario en Firebase.", "danger")
        return redirect(url_for("index"))

    grupos_usuario = usuario_vm.consultar_grupos_usuario(correo)
    usuario_data = {
        "correo": correo,
        "nombre_completo": usuario_obj.nombre_completo,
        "carrera": usuario_obj.carrera,
        "bio": getattr(usuario_obj, "descripcion_personal", ""),  # usar el atributo correcto
        "grupos": grupos_usuario  # lista de dict con 'id_grupo' y 'nombre'
    }

    return render_template("perfil.html", usuario=usuario_data)


@app.route("/perfil/eliminar", methods=["POST"])
@login_requerido
def eliminar_perfil():
    correo = session["usuario"]["correo"]

    try:
        resultado = usuario_vm.eliminar_usuario(correo)
        session.pop("usuario", None)  # eliminar sesión
        flash("Usuario eliminado correctamente.", "success")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"No se pudo eliminar el usuario: {e}", "danger")
        return redirect(url_for("perfil"))



# ========================================================
# Clubes
# ========================================================
@app.route("/clubes", methods=["GET"])
@login_requerido
def clubes():
    # Sesión demo si no existe autenticación real
    try:
        grupos_vm = GruposViewModel(firebase_global)

        # Semilla opcional (una sola vez) si no hay 'grupos' en Firebase
        existentes = firebase_global.obtener_datos("grupos") or {}
        if not existentes:
            try:
                flash("Se crearon clubes de ejemplo.", "success")
            except Exception as e:
                flash(f"No se pudo sembrar grupos: {e}", "danger")

        grupos = grupos_vm.listar_grupos() or []
    except Exception as e:
        grupos = []
        flash(f"Error cargando clubes: {e}", "danger")

    return render_template("clubes.html", grupos=grupos, correo=correo_actual())

def correo_actual():
    # Prioriza la sesión “usuario” real; mantiene compatibilidad con el fallback existente
    if "usuario" in session and session["usuario"].get("correo"):
        return session["usuario"]["correo"]
    return session.get("correo")


# Ruta para salirse de un grupo
@app.route("/salirse_grupo/<id_grupo>", methods=["POST"])
@login_requerido
def salirse_grupo(id_grupo):
    correo = session["usuario"]["correo"]
    resultado = usuario_vm.salirse_de_grupo(correo, id_grupo)
    return {"success": resultado["success"]}



# ---------- CLUBES (crear) ----------
@app.route("/clubes/crear", methods=["POST"])
@login_requerido
def crear_club():
    nombre = (request.form.get("nombre") or "").strip()
    descripcion = (request.form.get("descripcion") or "").strip()
    categoria = (request.form.get("categoria") or "").strip()
    orgs_raw = (request.form.get("organizadores") or "").strip()

    categorias_validas = {"Tecnología", "Ciencia", "Cultura", "Deportes"}
    if not nombre:
        flash("El nombre del grupo es obligatorio.", "warning")
        return redirect(url_for("clubes"))
    if categoria not in categorias_validas:
        flash("Categoría inválida.", "warning")
        return redirect(url_for("clubes"))

    # organizadores tipeados
    organizadores = [c.strip() for c in orgs_raw.split(",") if c.strip()]
    # añade SIEMPRE al creador
    creador = correo_actual()
    if creador and creador not in organizadores:
        organizadores.insert(0, creador)

    try:
        vm = GruposViewModel(firebase_global)
        # crear_grupo devuelve dict con id_grupo
        nuevo = vm.crear_grupo(
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            organizadores=organizadores
        )
        # Añadir también al creador como integrante (si no lo está)
        if creador:
            vm.agregar_integrante(nuevo["id_grupo"], creador)

        flash("Grupo creado.", "success")
    except Exception as e:
        flash(f"No se pudo crear el grupo: {e}", "danger")

    return redirect(url_for("clubes"))


# ---------- CLUBES (unirme) ----------
@app.route("/clubes/unirme/<id_grupo>", methods=["POST"])
@login_requerido
def unirme_club(id_grupo):
    correo = correo_actual()
    if not correo:
        flash("Debes iniciar sesión para unirte.", "warning")
        return redirect(url_for("inicio_sesion"))

    try:
        grupos_vm = GruposViewModel(firebase_global)
        ok = grupos_vm.agregar_integrante(id_grupo, correo)
        flash("Te uniste al grupo." if ok else "Ya perteneces o no fue posible unirte.", "success" if ok else "warning")
    except Exception as e:
        flash(f"No se pudo procesar la solicitud: {e}", "danger")

    return redirect(url_for("clubes"))


# ---------- CLUBES (salirme) ----------
@app.route("/clubes/salirme/<id_grupo>", methods=["POST"])
@login_requerido
def salirme_club(id_grupo):
    correo = correo_actual()
    if not correo:
        flash("Debes iniciar sesión para salir de un grupo.", "warning")
        return redirect(url_for("inicio_sesion"))
    ...


    try:
        grupos_vm = GruposViewModel(firebase_global)
        # Intentar usar remover_integrante si existe en el VM
        if hasattr(grupos_vm, "remover_integrante"):
            ok = grupos_vm.remover_integrante(id_grupo, correo)
            # TODO: reglas de negocio si es último organizador
        else:
            # Fallback: remover usando el modelo Grupo
            grupo_obj = grupos_vm.obtener_grupo(id_grupo)
            if not grupo_obj:
                flash("Grupo no encontrado.", "warning")
                return redirect(url_for("clubes"))

            dto = grupo_obj.to_dict() if hasattr(grupo_obj, "to_dict") else dict(grupo_obj)
            integrantes = list(dto.get("integrantes") or [])
            if correo in integrantes:
                integrantes.remove(correo)
                dto["integrantes"] = integrantes
                firebase_global.guardar_datos(f"grupos/{id_grupo}", dto)
                ok = True
            else:
                ok = False

        if ok:
            flash("Saliste del grupo.", "success")
        else:
            flash("No estabas en el grupo o no fue posible salir.", "warning")
    except Exception as e:
        flash(f"No se pudo procesar la solicitud: {e}", "danger")

    return redirect(url_for("clubes"))


# ---------- CLUBES (eliminar grupo) ----------
@app.route("/clubes/eliminar/<id_grupo>", methods=["POST"])
@login_requerido
def eliminar_club(id_grupo):
    user = correo_actual()
    try:
        vm = GruposViewModel(firebase_global)
        grupo = vm.obtener_grupo(id_grupo)
        if not grupo:
            flash("Grupo no encontrado.", "warning")
            return redirect(url_for("clubes"))

        # Solo organizadores pueden eliminar
        orgs = list(grupo.organizadores or [])
        if user not in orgs:
            flash("No tienes permisos para eliminar este grupo.", "danger")
            return redirect(url_for("clubes"))

        res = vm.eliminar_grupo(id_grupo)  # usa tu VM
        if res.get("success"):
            flash(f"Grupo eliminado.", "success")
        else:
            flash(res.get("error") or "No se pudo eliminar el grupo.", "danger")
    except Exception as e:
        flash(f"Error al eliminar el grupo: {e}", "danger")
    return redirect(url_for("clubes"))


# ---------- CLUBES (expulsar integrante) ----------
@app.route("/clubes/expulsar/<id_grupo>/<correo_miembro>", methods=["POST"])
@login_requerido
def expulsar_miembro(id_grupo, correo_miembro):
    user = correo_actual()
    try:
        vm = GruposViewModel(firebase_global)
        grupo = vm.obtener_grupo(id_grupo)
        if not grupo:
            flash("Grupo no encontrado.", "warning")
            return redirect(url_for("grupo_detalle", id_grupo=id_grupo))

        orgs = list(grupo.organizadores or [])
        if user not in orgs:
            flash("No tienes permisos para expulsar integrantes.", "danger")
            return redirect(url_for("grupo_detalle", id_grupo=id_grupo))

        # Protege a los organizadores: no expulsables desde aquí
        if correo_miembro in orgs:
            flash("No puedes expulsar a un organizador desde esta acción.", "warning")
            return redirect(url_for("grupo_detalle", id_grupo=id_grupo))

        ok = vm.remover_integrante(id_grupo, correo_miembro)
        flash("Integrante expulsado." if ok else "No fue posible expulsar.", "success" if ok else "warning")
    except Exception as e:
        flash(f"Error al expulsar: {e}", "danger")
    return redirect(url_for("grupo_detalle", id_grupo=id_grupo))


# ---------- DETALLES ----------
@app.route("/grupos/<id_grupo>", methods=["GET"])
@login_requerido
def grupo_detalle(id_grupo):
    try:
        grupos_vm = GruposViewModel(firebase_global)
        grupo = grupos_vm.obtener_grupo(id_grupo)
        if not grupo:
            flash("Grupo no encontrado.", "warning")
            return redirect(url_for("clubes"))
    except Exception as e:
        flash(f"Error al cargar grupo: {e}", "danger")
        return redirect(url_for("clubes"))
    return render_template("grupo_detalle.html", grupo=grupo.to_dict(), correo=correo_actual())

# ========================================================
# Ejecutar servidor
# ========================================================
def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
    