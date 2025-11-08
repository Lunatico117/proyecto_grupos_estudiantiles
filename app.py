# Inicio para usar flask
from flask import Flask, render_template, request, redirect, url_for, flash
from src.viewmodel.auth_viewmodel import UsuarioAuthViewModel
from src.services.firebase import FirebaseService
import time
from src.services.firebase_global import firebase_global

auth_vm = UsuarioAuthViewModel()
app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def index():
    return render_template("index.html")

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



@app.route("/inicio_sesion", methods=["GET", "POST"])
def inicio_sesion():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]
        resultado = auth_vm.iniciar_sesion(correo, password)
        if resultado["success"]:
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("index"))
        else:
            flash(resultado["error"], "danger")
    return render_template("iniciar_sesion.html")

def main():
    app.run(debug=True)
    registro_usuario()



if __name__ == "__main__":
    main()



