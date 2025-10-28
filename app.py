# Inicio para usar flask
"""
from flask import Flask, render_template, request, jsonify
from src.viewmodel.usuarios_viewmodel import UsuarioViewModel
from src.viewmodel.grupos_viewmodel import GruposViewModel

app = Flask(__name__)

# Instancias del ViewModel
usuario_vm = UsuarioViewModel()
grupo_vm = GruposViewModel()

@app.route('/')
def inicio():
    return "¡Bienvenido al sistema de grupos UNAL!"

if __name__ == '__main__':
    app.run(debug=True)
"""
