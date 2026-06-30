from banco import conectar


banco = conectar()


if banco.is_connected():

    print("Conectado com sucesso!")