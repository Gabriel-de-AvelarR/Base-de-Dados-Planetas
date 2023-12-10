import tkinter as tk
from tkinter import simpledialog, StringVar, Toplevel, Label, Button, OptionMenu
from tkinter.ttk import Combobox, Treeview
from PIL import Image, ImageTk
import cx_Oracle
from datetime import datetime
import json

def ler_configuracao(arquivo_config):
    with open(arquivo_config, 'r') as file:
        configuracao = json.load(file)
    return configuracao

def conectar_banco(config):
    endereco_banco = f"{config['endereco_vm']}:{config['porta']}/{config['nome_servico']}"
    try:
        conexao = cx_Oracle.connect(config['usuario'], config['senha'], endereco_banco)
        print("Conexão bem-sucedida!")
        return conexao

    except cx_Oracle.DatabaseError as erro:
        print(f"Erro na conexão com o banco de dados: {erro}")
        return None

def inserir_dados_astronauta(conexao, nome_dado):
    if conexao is None:
        print("Não é possível inserir dados sem uma conexão válida.")
        return

    cursor = conexao.cursor()

    try:
        Nascimento = datetime.now()
        conexao.begin()

        cursor.execute("INSERT INTO ASTRONAUTA (NOME, NASCIMENTO) VALUES (:1, :2)", (nome_dado, Nascimento))
        conexao.commit()

        print("Cadastro realizado com sucesso!")

    except cx_Oracle.IntegrityError as erro:
        if erro.args[0].code == 12899:  # Código de erro para tamanho excedido
            raise ValueError("Erro: Nome do astronauta excede o tamanho máximo permitido.")
            conexao.rollback()
        elif erro.args[0].code == 1:  # Código de erro para violação de unicidade
            raise ValueError("Nome duplicado, por favor, insira um nome único.")
            conexao.rollback()
        else:
            print(f"Erro no banco de dados ao inserir dados: {erro}")
            conexao.rollback()
            return 0

    finally:
        cursor.close()

    return 1  # Retorno indicando sucesso

def inserir_dados_planeta(conexao, dados_planeta):
    if conexao is None:
        print("Não é possível inserir dados sem uma conexão válida.")
        return

    cursor = conexao.cursor()

    try:
        conexao.begin()

        consulta = """
            INSERT INTO PLANETA (NOME, TAMANHO, NIVEL_DE_SEGURANCA, DISTANCIA_DA_ESTRELA, CALOR, TRANSLACAO, ROTACAO, ESTRELA)
            VALUES (:nome, :tamanho, :nivel_seguranca, :distancia_estrela, :calor, :translacao, :rotacao, :estrela)
        """

        # Executar a consulta, tratando os valores nulos
        cursor.execute(consulta, {
            'nome': dados_planeta['nome'],
            'tamanho': dados_planeta.get('tamanho', None),
            'nivel_seguranca': dados_planeta.get('nivel_seguranca', None),
            'distancia_estrela': dados_planeta.get('distancia_estrela', None),
            'calor': dados_planeta.get('calor', None),
            'translacao': dados_planeta.get('translacao', None),
            'rotacao': dados_planeta.get('rotacao', None),
            'estrela': dados_planeta['estrela']
        })
        conexao.commit()

        print("Cadastro realizado com sucesso!")

    except cx_Oracle.IntegrityError as erro:
        if erro.args[0].code == 12899:  # Código de erro para tamanho excedido
            raise ValueError("Erro: Nome do astronauta excede o tamanho máximo permitido.")
            conexao.rollback()
        elif erro.args[0].code == 1:  # Código de erro para violação de unicidade
            raise ValueError("Nome duplicado, por favor, insira um nome único.")
            conexao.rollback()
        else:
            print(f"Erro no banco de dados ao inserir dados: {erro}")
            conexao.rollback()
            return 0

    finally:
        cursor.close()

    return 1  # Retorno indicando sucesso

def fechar_conexao(conexao):
    if conexao is not None:
        conexao.close()

def coletar_dados_astronauta(conexao, etiqueta_nome, janela):
    try:
        nome_astronauta = simpledialog.askstring("Astronauta", "Digite o nome/apelido do astronauta:")

        if inserir_dados_astronauta(conexao, nome_astronauta) == 0:
            # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
            mensagem_erro = "Erro ao inserir, nome inválido"
            exibir_janela_erro(janela, mensagem_erro)
        else:
            mensagem = f"Inserindo Astronauta: Nome - {nome_astronauta}"
            etiqueta_nome.config(text=mensagem)

    except ValueError as erro:
        # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
        exibir_janela_erro(janela, str(erro))

def coletar_dados_planeta(conexao, etiqueta_nome, janela):
    try:
        # Coletar o nome do planeta
        nome_planeta = simpledialog.askstring("Planeta", "Digite o nome do planeta:")

        # Criar variáveis StringVar para armazenar as escolhas do usuário
        escolha_tamanho_planeta = StringVar()
        escolha_nivel_seguranca = StringVar()

        # Criar a janela temporária para a seleção de opções
        janela_opcoes = Toplevel(janela)
        janela_opcoes.title("Selecione o Tamanho e Nível de Segurança do Planeta")

        # Exibir uma mensagem para instruir o usuário
        Label(janela_opcoes, text="Selecione o tamanho e o nível de segurança do planeta:").pack(pady=10)

        # Criar opções para tamanho do planeta e nível de segurança
        opcoes_tamanho_planeta = ["Pequeno", "Médio", "Grande"]
        opcoes_nivel_seguranca = ["Baixo", "Médio", "Alto"]

        # Adicionar opções de tamanho do planeta ao menu
        Label(janela_opcoes, text="Selecione o tamanho do planeta:").pack(pady=5)
        tamanho_planeta_menu = OptionMenu(janela_opcoes, escolha_tamanho_planeta, *opcoes_tamanho_planeta)
        tamanho_planeta_menu.pack(pady=5)

        # Adicionar opções de nível de segurança ao menu
        Label(janela_opcoes, text="Selecione o nível de segurança do planeta:").pack(pady=5)
        nivel_seguranca_menu = OptionMenu(janela_opcoes, escolha_nivel_seguranca, *opcoes_nivel_seguranca)
        nivel_seguranca_menu.pack(pady=5)
        # Criar uma função para verificar se ambas as opções foram selecionadas
        def verificar_selecao():
            tamanho_planeta = escolha_tamanho_planeta.get()
            nivel_seguranca = escolha_nivel_seguranca.get()
            if tamanho_planeta and nivel_seguranca:
                # Se ambas as opções foram selecionadas, fechar a janela
                janela_opcoes.destroy()
            else:
                # Caso contrário, exibir uma mensagem de erro
                mensagem_erro = "Selecione uma opção para o tamanho e o nível de segurança do planeta."
                exibir_janela_erro(janela, mensagem_erro)

        # Adicionar um botão para verificar a seleção
        Button(janela_opcoes, text="OK", command=verificar_selecao).pack(pady=10)

        # Esperar até que o usuário faça uma escolha
        janela_opcoes.wait_window(janela_opcoes)

        distancia_estrela = simpledialog.askstring("Distância da Estrela", "Digite a distância da estrela (ou deixe em branco para NULL):")
        if distancia_estrela == "":
            distancia_estrela = None
        else:
            try:
                distancia_estrela = int(distancia_estrela)
            except ValueError:
                mensagem_erro = "A distância deve ser um número inteiro."
                exibir_janela_erro(janela, mensagem_erro)
                return

        # Coletar a temperatura do planeta
        calor = simpledialog.askstring("Calor", "Digite a temperatura do planeta (ou deixe em branco para NULL):")
        if calor == "":
            calor = None
        else:
            try:
                calor = int(calor)
            except ValueError:
                mensagem_erro = "A temperatura deve ser um inteiro."
                exibir_janela_erro(janela, mensagem_erro)
                return

        # Coletar a velocidade de translação do planeta
        translacao = simpledialog.askstring("Translação", "Digite a velocidade de translação do planeta (ou deixe em branco para NULL):")
        if translacao == "":
            translacao = None
        else:
            try:
                translacao = int(translacao)
            except ValueError:
                mensagem_erro = "A translação deve ser um inteiro."
                exibir_janela_erro(janela, mensagem_erro)
                return

        # Coletar a velocidade de rotação do planeta
        rotacao = simpledialog.askstring("Rotação", "Digite a velocidade de rotação do planeta (ou deixe em branco para NULL):")
        if rotacao == "":
            rotacao = None
        else:
            try:
                rotacao = int(rotacao)
            except ValueError:
                mensagem_erro = "A rotação deve ser um inteiro."
                exibir_janela_erro(janela, mensagem_erro)
                return

        # Coletar o nome da estrela
        nome_estrela = simpledialog.askstring("Estrela", "Digite o nome da estrela que o planeta orbita:")

        # Criar um dicionário com os dados coletados
        dicionario_planeta = {
            "nome": nome_planeta,
            "tamanho": escolha_tamanho_planeta.get(),
            "nivel_seguranca": escolha_nivel_seguranca.get(),
            "distancia_estrela": distancia_estrela,
            "calor": calor,
            "translacao": translacao,
            "rotacao": rotacao,
            "estrela": nome_estrela
        }

        if inserir_dados_planeta(conexao, dicionario_planeta) == 0:
            # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
            mensagem_erro = "Erro ao inserir, dados inválidos"
            exibir_janela_erro(janela, mensagem_erro)
        else:
            mensagem = f"Inserindo Planeta: Nome - {nome_planeta}"
            etiqueta_nome.config(text=mensagem)

    except ValueError as erro:
        # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
        exibir_janela_erro(janela, str(erro))

def exibir_janela_erro(janela_pai, mensagem_erro):
    janela_erro = Toplevel(janela_pai)
    janela_erro.title("Erro")
    janela_erro.geometry("500x100")

    etiqueta_erro = tk.Label(janela_erro, text=mensagem_erro, font=("Arial", 12), fg="red")
    etiqueta_erro.pack(pady=20)

    botao_fechar = tk.Button(janela_erro, text="Fechar", command=janela_erro.destroy)
    botao_fechar.pack()

def abrir_janela_insercao(janela, conexao, etiqueta_nome):
    # Função para a janela de inserção
    def inserir_dados(tipo):
        # Aqui você pode implementar a lógica para inserir dados do tipo escolhido (astronauta ou planeta)
        etiqueta_nome.config(text=f"Inserindo {tipo}...")

    # Criar a nova janela de inserção
    janela_insercao = Toplevel(janela)
    janela_insercao.title("Inserir Dados")
    janela_insercao.geometry("400x300")  # Ajuste o tamanho conforme necessário

    # Criar botões na nova janela
    botao_astronauta = tk.Button(janela_insercao, text="Astronauta", command=lambda: coletar_dados_astronauta(conexao, etiqueta_nome, janela))
    botao_planeta = tk.Button(janela_insercao, text="Planeta", command=lambda: coletar_dados_planeta(conexao, etiqueta_nome, janela))

    # Empacotar os botões no meio da nova janela
    pos_x = (400 - botao_astronauta.winfo_reqwidth()) / 2
    pos_y = (300 - botao_astronauta.winfo_reqheight()) / 2

    botao_astronauta.place(x=pos_x, y=pos_y)
    botao_planeta.place(x=pos_x, y=pos_y + botao_astronauta.winfo_reqheight() + 10)

def abrir_janela_consultas(janela, conexao, etiqueta_nome):
    # Função para a janela de inserção
    def consultar_dados(tipo):
        # Aqui você pode implementar a lógica para inserir dados do tipo escolhido (astronauta ou planeta)
        etiqueta_nome.config(text=f"Consulta {tipo}...")

    # Criar a nova janela de inserção
    janela_consulta = Toplevel(janela)
    janela_consulta.title("Consultar Dados")
    janela_consulta.geometry("400x300")  # Ajuste o tamanho conforme necessário

    # Criar botões na nova janela
    botao_construct = tk.Button(janela_consulta, text="Construções Próximas", command=lambda: coletar_dados_consulta(conexao, etiqueta_nome, janela))
    #botao_elemento = tk.Button(janela_consulta, text="Elementos Quimicos", command=lambda: coletar_dados_elementoquimico(conexao, etiqueta_nome, janela))

    # Empacotar os botões no meio da nova janela
    pos_x = (400 - botao_construct.winfo_reqwidth()) / 2
    #pos_y = (300 - botao_elemento.winfo_reqheight()) / 2

    botao_construct.place(x=pos_x, y=pos_y)
    #botao_elemento.place(x=pos_x, y=pos_y + botao_construct.winfo_reqheight() + 10)

def mostrar_tabela_resultados(janela, dados):
    if dados is None:
        return

    # Criar a janela para mostrar a tabela
    janela_tabela = tk.Toplevel(janela)
    janela_tabela.title("Resultados da Consulta")

    # Criar um widget Treeview para exibir a tabela
    tree = Treeview(janela_tabela)

    # Definir as colunas
    tree["columns"] = tuple(range(len(dados[0])))  # Assumindo que todos os registros têm o mesmo número de colunas

    # Definir o cabeçalho da tabela
    for i, coluna in enumerate(dados[0]):
        tree.heading(i, text=str(coluna))

    dados = dados[1:]
    # Adicionar os dados à tabela
    for linha in dados:
        tree.insert("", "end", values=linha)

    # Empacotar o widget Treeview
    tree.pack(expand=True, fill=tk.BOTH)

def busca_construcoes_proximas(conexao, nome_construcao, etiqueta_nome, janela):
    if conexao is None:
        print("Não é possível buscar dados sem uma conexão válida.")
        return None  # Retorne None para indicar erro

    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT
                F.NOME AS FABRICAVEL,
                L.POSICAOX,
                L.POSICAOY,
                TRUNC(SQRT(POWER(5 - L.POSICAOX, 2) + POWER(8 - L.POSICAOY, 2))) AS DISTANCIA
            FROM
                FABRICAVEIS F
            JOIN "LOCAL" L ON F.NOME = L.FABRICAVEL
            WHERE
                F.NOME <> :nome
            ORDER BY
                DISTANCIA
            FETCH FIRST 5 ROWS ONLY
        """, {'nome': nome_construcao})

        conexao.commit()
        dados = cursor.fetchall()  # Retorna uma lista de tuplas
        print("Consulta realizada com sucesso!")
        cabecalho = ["Construção", "Posição X", "Posição Y", "Distância"]
        dados_com_cabecalho = [cabecalho] + dados

        mostrar_tabela_resultados(janela, dados_com_cabecalho)
        return dados

    except cx_Oracle.DatabaseError as erro:
        print(f"Erro no banco de dados ao executar consulta: {erro}")
        conexao.rollback()

    finally:
        cursor.close()

    return None  # Retorne None em caso de erro

#def busca_elementos(conexao, nome_elemento, etiqueta_nome, janela):
    if conexao is None:
        print("Não é possível buscar dados sem uma conexão válida.")
        return None  # Retorne None para indicar erro

    cursor = conexao.cursor()

    try:
        cursor.execute("""
                SELECT
                    EQ.SIGLA AS ELEMENTO_QUIMICO,
                    P.NOME AS PLANETA,
                    'Espécie: ' || E.NOME AS ENCONTRADO_EM
                FROM
                    ELEMENTO_QUIMICO EQ
                LEFT JOIN ESPECIES E ON EQ.SIGLA = E.ELEMENTO
                LEFT JOIN AMBIENTE A ON E.NOMEPLANETA = A.PLANETA
                LEFT JOIN PLANETA P ON A.PLANETA = P.NOME
                WHERE
                    EQ.SIGLA = :nome

                UNION

                SELECT
                    EQ.SIGLA AS ELEMENTO_QUIMICO,
                    P.NOME AS PLANETA,
                    'Minério: ' || M.NOME AS ENCONTRADO_EM
                FROM
                    ELEMENTO_QUIMICO EQ
                LEFT JOIN MINERIO M ON EQ.SIGLA = M.ELEMENTO
                LEFT JOIN POSSUI POS ON M.NOME = POS.MINERIO
                LEFT JOIN AMBIENTE A ON POS.AMBIENTE = A.PLANETA
                LEFT JOIN PLANETA P ON A.PLANETA = P.NOME
                WHERE
                    EQ.SIGLA = :nome2
            """, {'nome': nome_elemento})
        conexao.commit()

        dados = cursor.fetchall()  # Retorna uma lista de tuplas

        print("Consulta realizada com sucesso!")
        cabecalho = ["Elemento", "Planeta", "Encontrado em"]
        dados_com_cabecalho = [cabecalho] + dados

        mostrar_tabela_resultados(janela, dados_com_cabecalho)
        return dados

    except cx_Oracle.DatabaseError as erro:
        print(f"Erro no banco de dados ao executar consulta: {erro}")
        conexao.rollback()

    finally:
        cursor.close()

    return None  # Retorne None em caso de erro

def coletar_dados_consulta(conexao, etiqueta_nome, janela):
    try:
        nome_construcao = simpledialog.askstring("Construção", "Digite o nome da construção em que você se encontra:")
        dados = busca_construcoes_proximas(conexao, nome_construcao, etiqueta_nome, janela)

        if dados is not None:
            mensagem = f"Consulta realizada para a construção: {nome_construcao}"
            etiqueta_nome.config(text=mensagem)
        else:
            # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
            mensagem_erro = "Erro ao buscar construções próximas, nome inválido ou ocorreu um erro no banco de dados"
            exibir_janela_erro(janela, mensagem_erro)

    except ValueError as erro:
        # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
        exibir_janela_erro(janela, str(erro))

#def coletar_dados_elementoquimico(conexao, etiqueta_nome, janela):
    try:
        nome_elemento = simpledialog.askstring("Elemento", "Digite o nome do elemento que você deseja encontrar:")
        dados = busca_elementos(conexao, nome_elemento, etiqueta_nome, janela)

        if dados is not None:
            mensagem = f"Consulta realizada para o elemento: {nome_elemento}"
            etiqueta_nome.config(text=mensagem)
        else:
            # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
            mensagem_erro = "Erro ao buscar elementos próximos, nome inválido ou ocorreu um erro no banco de dados"
            exibir_janela_erro(janela, mensagem_erro)

    except ValueError as erro:
        # Se ocorrer um erro, abrir uma nova janela com a mensagem de erro
        exibir_janela_erro(janela, str(erro))

def iniciar_interface():
    # Ler configurações do arquivo
    configuracao = ler_configuracao("Senha.json")

    # Conectar ao banco de dados usando as configurações
    conexao = conectar_banco(configuracao)

    # Criar a janela principal
    janela = tk.Tk()
    janela.title("Enciclopédia de exploração espacial")
    janela.geometry("800x600")  # Ajuste o tamanho conforme necessário

    # Carregar a imagem e redimensioná-la
    imagem_original = Image.open("Fundo.jpg")
    nova_resolucao = (800, 600)  # Defina a nova resolução desejada
    imagem_redimensionada = imagem_original.resize(nova_resolucao, Image.ANTIALIAS)
    imagem = ImageTk.PhotoImage(imagem_redimensionada)

    # Criar um Canvas para exibir a imagem
    canvas = tk.Canvas(janela, width=nova_resolucao[0], height=nova_resolucao[1])
    canvas.pack()

    # Exibir a imagem no Canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=imagem)

    # Criar botões
    botao_inserir = tk.Button(janela, text="Inserir", command=lambda: abrir_janela_insercao(janela, conexao, etiqueta_nome))
    botao_consultar = tk.Button(janela, text="Consultar", command=lambda: coletar_dados_consulta(conexao,etiqueta_nome, janela))

    # Empacotar os botões no meio da janela
    pos_x = (nova_resolucao[0] - botao_inserir.winfo_reqwidth()) / 2
    pos_y = (nova_resolucao[1] - botao_inserir.winfo_reqheight()) / 2

    botao_inserir.place(x=pos_x, y=pos_y)
    botao_consultar.place(x=pos_x, y=pos_y + botao_inserir.winfo_reqheight() + 10)  # Ajuste a margem conforme necessário

    # Criar uma etiqueta para exibir o nome inserido ou mensagem de consulta
    etiqueta_nome = tk.Label(janela, text="")
    etiqueta_nome.pack(pady=10)

    mensagem_consulta = tk.Label(janela, text="")
    mensagem_consulta.pack(pady=10)

    # Elevar os botões acima do Canvas
    botao_inserir.lift(etiqueta_nome)
    botao_consultar.lift(etiqueta_nome)

    # Iniciar o loop principal da interface gráfica
    janela.mainloop()

    # Fechar a conexão ao sair
    fechar_conexao(conexao)

# Chamar a função para iniciar a interface
iniciar_interface()
