# Inicio para usar Flask y manejar sesiones
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps  # Para crear decoradores
from src.viewmodel.auth_viewmodel import UsuarioAuthViewModel 
from src.services.firebase_global import firebase_global  # Asegurarse de que este objeto ya tenga db inicializado

auth_vm = UsuarioAuthViewModel()
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
@app.route("/clubes")
@login_requerido
def clubes():
    return render_template("clubes.html", usuario=session["usuario"])


@app.route("/eventos")
@login_requerido
def eventos():
    return render_template("eventos.html", usuario=session["usuario"])


@app.route("/perfil")
@login_requerido
def perfil():
    return render_template("perfil.html", usuario=session["usuario"])


# ========================================================
# Ejecutar servidor
# ========================================================
def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
