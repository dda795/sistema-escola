from flask import Flask, render_template, request, redirect, session
from banco import conectar

app = Flask(__name__, static_folder="static")
app.secret_key = "escola123"

# =========================
# LOGIN
# =========================

@app.route("/")
def inicio():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    senha = request.form["senha"]

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM usuarios
        WHERE email=%s AND senha=%s
    """, (email, senha))

    usuario = cursor.fetchone()

    if usuario:
        session["usuario"] = usuario["id"]
        session["tipo"] = usuario["tipo"]
        session["nome"] = usuario["nome"]
        session["turma"] = usuario["turma"]

        if usuario["tipo"] == "admin":
            return redirect("/admin")
        return redirect("/painel")

    return "Email ou senha incorretos"


# =========================
# CADASTRO
# =========================

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/cadastrar", methods=["POST"])
def cadastrar():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO usuarios (nome,email,senha,turma,tipo)
        VALUES (%s,%s,%s,%s,'aluno')
    """, (
        request.form["nome"],
        request.form["email"],
        request.form["senha"],
        request.form["turma"]
    ))

    banco.commit()
    return redirect("/")


# =========================
# PAINEL ALUNO
# =========================

@app.route("/painel")
def painel():

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM chamados
        WHERE usuario_id=%s
    """, (session["usuario"],))

    chamados = cursor.fetchall()

    return render_template("painel.html", chamados=chamados)


# =========================
# NOVO CHAMADO
# =========================

@app.route("/novo")
def novo():
    return render_template("chamado.html")


@app.route("/criar", methods=["POST"])
def criar():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO chamados
        (titulo,descricao,categoria,usuario_id,status,data_chamado)
        VALUES (%s,%s,%s,%s,'Pendente',CURDATE())
    """, (
        request.form["titulo"],
        request.form["descricao"],
        request.form["categoria"],
        session["usuario"]
    ))

    banco.commit()
    return redirect("/painel")


# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    filtro = request.args.get("status")

    sql = """
        SELECT chamados.*, usuarios.nome
        FROM chamados
        INNER JOIN usuarios
        ON chamados.usuario_id = usuarios.id
    """

    if filtro:
        sql += " WHERE chamados.status=%s"
        cursor.execute(sql, (filtro,))
    else:
        cursor.execute(sql)

    chamados = cursor.fetchall()

    return render_template("admin.html", chamados=chamados)


# =========================
# EDITAR CHAMADO
# =========================

@app.route("/editar/<int:id>")
def editar(id):

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM chamados WHERE id=%s
    """, (id,))

    chamado = cursor.fetchone()

    return render_template("editar.html", chamado=chamado)


@app.route("/atualizar/<int:id>", methods=["POST"])
def atualizar(id):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        UPDATE chamados
        SET titulo=%s,
            descricao=%s,
            categoria=%s,
            resposta=%s
        WHERE id=%s
    """, (
        request.form["titulo"],
        request.form["descricao"],
        request.form["categoria"],
        request.form["resposta"],
        id
    ))

    banco.commit()
    return redirect("/admin")


# =========================
# AÇÕES
# =========================

@app.route("/resolver/<int:id>")
def resolver(id):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        UPDATE chamados
        SET status='Resolvido'
        WHERE id=%s
    """, (id,))

    banco.commit()
    return redirect("/admin")


@app.route("/excluir/<int:id>")
def excluir(id):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        DELETE FROM chamados
        WHERE id=%s
    """, (id,))

    banco.commit()
    return redirect("/admin")


# =========================
# SAIR
# =========================

@app.route("/sair")
def sair():
    session.clear()
    return redirect("/")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)