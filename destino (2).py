import pygame
import sys
import os
import re
import html
import random
import smtplib
from io import BytesIO
from email.message import EmailMessage
from email.utils import make_msgid

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Gera o gráfico sem abrir outra janela.
import matplotlib.pyplot as plt


# ----------------------------
# Configurações iniciais
# ----------------------------
pygame.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Destino")

# ----------------------------
# Imagens dos personagens
# ----------------------------
imagens_personagens = {}
for _nome, _arquivo in {
    "Marcelo": "Img/nerd.png",
    "Ângela": "Img/garota_confusa.png",
    "Anderson": "Img/garoto_popular.png",
    "Leonardo": "Img/lider_sala.png",
}.items():
    try:
        imagens_personagens[_nome] = pygame.image.load(_arquivo)
    except (pygame.error, FileNotFoundError):
        pass  # Sem a imagem, o jogo desenha um quadrado branco no lugar.

# Fontes e cores
fonte_titulo = pygame.font.SysFont("timesnewroman", 56, bold=True)
fonte_texto = pygame.font.SysFont("arial", 22)
fonte_pequena = pygame.font.SysFont("arial", 18)

BRANCO = (255, 255, 255)
PRETO = (10, 10, 10)
CINZA = (45, 45, 45)
AZUL = (80, 120, 220)
VERDE = (80, 200, 120)
AMARELO = (230, 200, 60)
VERMELHO = (220, 80, 80)

CLOCK = pygame.time.Clock()
FPS = 60

# ----------------------------
# Atributos do jogador (5 = pentágono)
# ----------------------------
atributos = {
    "Adaptabilidade": 50,
    "Comunicação": 50,
    "Inteligência Emocional": 50,
    "Criatividade": 50,
    "Liderança": 50,
}
ATR_MIN, ATR_MAX = 0, 100


def ajustar_atributos(delta):
    for k, v in delta.items():
        if k in atributos:
            atributos[k] = max(ATR_MIN, min(ATR_MAX, atributos[k] + v))


# ----------------------------
# Perguntas
# ----------------------------
perguntas = [
    # Marcelo
    {
        "personagem": "Marcelo",
        "fala": "Marcelo sugere criar um cronograma com prazos rígidos para o grupo.",
        "opcoes": [
            ("Aceitar", {"Adaptabilidade": +10, "Comunicação": -10, "Liderança": +10}),
            ("Rejeitar", {"Comunicação": +10, "Adaptabilidade": -10, "Liderança": -5})
        ]
    },
    {
        "personagem": "Marcelo",
        "fala": "Ele percebe que alguns colegas não estão acompanhando o ritmo.",
        "opcoes": [
            ("Parar para explicar", {"Comunicação": +15, "Adaptabilidade": -20, "Liderança": +10}),
            ("Continuar sozinho", {"Adaptabilidade": +15, "Inteligência Emocional": -20, "Liderança": -10})
        ]
    },
    {
        "personagem": "Marcelo",
        "fala": "O prazo está apertando. Quer assumir todas as tarefas para garantir.",
        "opcoes": [
            ("Deixar ele assumir", {"Adaptabilidade": +10, "Inteligência Emocional": -15, "Liderança": -10}),
            ("Dividir tarefas igualmente", {"Inteligência Emocional": +15, "Adaptabilidade": -10, "Liderança": +10})
        ]
    },
    {
        "personagem": "Marcelo",
        "fala": "Na apresentação final, ele quer usar gráficos técnicos complicados.",
        "opcoes": [
            ("Manter gráficos", {"Adaptabilidade": +10, "Comunicação": -25}),
            ("Simplificar", {"Comunicação": +15, "Criatividade": -15, "Liderança": +5})
        ]
    },

    # Ângela
    {
        "personagem": "Ângela",
        "fala": "Aparece com uma ideia criativa para o trabalho, mas é arriscada.",
        "opcoes": [
            ("Aceitar", {"Criatividade": +20, "Inteligência Emocional": -10, "Liderança": +5}),
            ("Rejeitar", {"Adaptabilidade": +10, "Criatividade": -10})
        ]
    },
    {
        "personagem": "Ângela",
        "fala": "Ela fica ansiosa porque ninguém entende seu conceito artístico.",
        "opcoes": [
            ("Escutar e adaptar", {"Inteligência Emocional": +25, "Criatividade": -30}),
            ("Insistir na ideia", {"Criatividade": +15, "Inteligência Emocional": -10, "Liderança": +5})
        ]
    },
    {
        "personagem": "Ângela",
        "fala": "Na apresentação, ela se perde tentando explicar o projeto.",
        "opcoes": [
            ("Ajudar a explicar", {"Comunicação": +15, "Criatividade": -15, "Liderança": +10}),
            ("Deixar ela improvisar", {"Criatividade": +10, "Comunicação": -10})
        ]
    },
    {
        "personagem": "Ângela",
        "fala": "Faltam recursos para executar sua proposta.",
        "opcoes": [
            ("Improvisar materiais", {"Criatividade": +10, "Adaptabilidade": -10, "Liderança": +5}),
            ("Voltar ao plano tradicional", {"Adaptabilidade": +10, "Criatividade": -10})
        ]
    },

    # Anderson
    {
        "personagem": "Anderson",
        "fala": "Se oferece para ser o porta-voz do grupo.",
        "opcoes": [
            ("Aceitar", {"Comunicação": +10, "Adaptabilidade": -10, "Liderança": +5}),
            ("Recusar", {"Adaptabilidade": +10, "Comunicação": -10, "Liderança": -5})
        ]
    },
    {
        "personagem": "Anderson",
        "fala": "Ele decide convidar outros colegas de fora para ajudar.",
        "opcoes": [
            ("Permitir", {"Comunicação": +10, "Adaptabilidade": -15, "Liderança": +5}),
            ("Rejeitar", {"Adaptabilidade": +10, "Comunicação": -10})
        ]
    },
    {
        "personagem": "Anderson",
        "fala": "Improvisa uma fala engraçada na apresentação.",
        "opcoes": [
            ("Rir junto", {"Comunicação": +10, "Criatividade": -10}),
            ("Corrigir ele depois", {"Inteligência Emocional": +15, "Comunicação": -15, "Liderança": +10})
        ]
    },
    {
        "personagem": "Anderson",
        "fala": "Após o trabalho, recebe aplausos, mas esquece de citar os outros.",
        "opcoes": [
            ("Reivindicar crédito", {"Adaptabilidade": +15, "Inteligência Emocional": -10, "Liderança": +5}),
            ("Deixar passar", {"Inteligência Emocional": +15, "Comunicação": -10, "Liderança": -5})
        ]
    },

    # Leonardo
    {
        "personagem": "Leonardo",
        "fala": "Um colega sugere uma solução arriscada e criativa.",
        "opcoes": [
            ("Apoiar", {"Criatividade": +10, "Inteligência Emocional": -10, "Liderança": +10}),
            ("Recusar", {"Inteligência Emocional": +10, "Criatividade": -10, "Liderança": -5})
        ]
    },
    {
        "personagem": "Leonardo",
        "fala": "O grupo começa a brigar sobre quem faz o quê.",
        "opcoes": [
            ("Dividir tarefas igualmente", {"Inteligência Emocional": +10, "Criatividade": -10, "Liderança": +15}),
            ("Deixar eles se resolverem", {"Adaptabilidade": +5, "Inteligência Emocional": -10, "Liderança": -10})
        ]
    },
    {
        "personagem": "Leonardo",
        "fala": "Um membro do grupo está desmotivado e sem ânimo.",
        "opcoes": [
            ("Motivar", {"Inteligência Emocional": +10, "Adaptabilidade": -5, "Liderança": +15}),
            ("Ignorar", {"Adaptabilidade": +20, "Inteligência Emocional": -15, "Liderança": -15})
        ]
    },
    {
        "personagem": "Leonardo",
        "fala": "Na apresentação, sugere seguir o plano seguro em vez de improvisar.",
        "opcoes": [
            ("Concordar", {"Inteligência Emocional": +10, "Criatividade": -10, "Liderança": +5}),
            ("Improvisar", {"Criatividade": +10, "Adaptabilidade": -10, "Liderança": +5})
        ]
    }
]

# ----------------------------
# Áreas finais
# ----------------------------
areas = {
    "Pesquisador / Técnico": {
        "descricao": "Perfil analítico e resiliente. Ótimo para funções que exigem lógica, precisão e adaptação.",
        "profissoes": "Ex: Analista de Dados, Engenheiro, Pesquisador."
    },
    "Criativo / Designer": {
        "descricao": "Perfil imaginativo e experimental. Ideal para quem busca inovar e criar soluções visuais ou conceituais.",
        "profissoes": "Ex: Designer, Publicitário, Ilustrador."
    },
    "Comunicador / Gestor de Pessoas": {
        "descricao": "Perfil que se destaca em ouvir, articular e liderar. Bom para papéis que exigem mediação e gestão.",
        "profissoes": "Ex: Gestor de Projetos, Jornalista, RH."
    },
    "Emocionalmente Inteligente": {
        "descricao": "Perfil com alta sensibilidade social e autoconsciência, indicado para áreas que lidam com pessoas e suporte emocional.",
        "profissoes": "Ex: Psicólogo, Coach, Professor."
    },
    "Líder / Empreendedor": {
        "descricao": "Perfil que toma a frente, organiza o grupo e inspira os outros a seguir em direção a um objetivo.",
        "profissoes": "Ex: Empreendedor, Coordenador de Equipes, Gerente."
    }
}

ATRIBUTO_PARA_AREA = {
    "Adaptabilidade": "Pesquisador / Técnico",
    "Comunicação": "Comunicador / Gestor de Pessoas",
    "Inteligência Emocional": "Emocionalmente Inteligente",
    "Criatividade": "Criativo / Designer",
    "Liderança": "Líder / Empreendedor",
}


def determinar_area():
    """Retorna (nome_da_area, info_da_area) pelo atributo mais alto."""
    maior = max(atributos.items(), key=lambda x: x[1])[0]
    chave = ATRIBUTO_PARA_AREA[maior]
    return chave, areas[chave]


# ----------------------------
# Utilitários de UI
# ----------------------------
def render_centered(text, font, y, color=BRANCO):
    surf = font.render(text, True, color)
    tela.blit(surf, (LARGURA // 2 - surf.get_width() // 2, y))


def desenhar_intro_fade():
    titulo = fonte_titulo.render("BEM-VINDO", True, BRANCO)
    titulo_rect = titulo.get_rect(center=(LARGURA // 2, 110))

    linhas = [
        "Você foi selecionado!",
        "Parabéns!",
        "Agora que você está nos seus últimos dias",
        "do ensino médio,",
        "queremos que você apenas continue seu dia a dia.",
        "Enquanto isso, vamos avaliar suas ações.",
        "Lembre-se de se divertir!",
        "Pressione ENTER para começar."
    ]

    tela.fill(PRETO)
    tela.blit(titulo, titulo_rect)
    pygame.display.flip()

    for i, linha in enumerate(linhas):
        texto_surface = fonte_texto.render(linha, True, BRANCO).convert_alpha()
        texto_rect = texto_surface.get_rect(center=(LARGURA // 2, 260 + i * 40))
        start = pygame.time.get_ticks()
        dur = 1500  # ms
        while True:
            elapsed = pygame.time.get_ticks() - start
            alpha = min(255, int((elapsed / dur) * 255))
            texto_surface.set_alpha(alpha)
            tela.fill(PRETO)
            tela.blit(titulo, titulo_rect)
            tela.blit(texto_surface, texto_rect)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.flip()
            CLOCK.tick(FPS)
            if alpha >= 255:
                break


def desenhar_botao(rect, texto, hover):
    color = AZUL if hover else BRANCO
    pygame.draw.rect(tela, color, rect, border_radius=10)

    fonte_ajustada = fonte_texto
    if fonte_texto.size(texto)[0] > rect.width - 20:
        fonte_ajustada = pygame.font.SysFont("arial", 18)
    txt = fonte_ajustada.render(texto, True, PRETO)
    tela.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))


def desenhar_atributos():
    """Barras de atributos no topo (2 colunas x 3 linhas)."""
    y0 = 8
    largura_bar = 200
    espaco_horizontal = 50
    espaco_vertical = 46

    for i, (nome, valor) in enumerate(atributos.items()):
        linha = i // 2
        coluna = i % 2
        x = 50 + coluna * (largura_bar + espaco_horizontal)
        y = y0 + linha * espaco_vertical

        txt = fonte_pequena.render(nome, True, BRANCO)
        tela.blit(txt, (x, y))
        pygame.draw.rect(tela, CINZA, (x, y + 22, largura_bar, 14), border_radius=8)
        fill_w = int((valor / 100) * largura_bar)
        pygame.draw.rect(tela, VERDE, (x, y + 22, fill_w, 14), border_radius=8)


def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    cur = ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ----------------------------
# Tela de perguntas
# ----------------------------
def tela_perguntas(sequencia):
    respostas = []
    for idx, bloco in enumerate(sequencia):
        personagem = bloco["personagem"]
        fala = bloco["fala"]
        opcoes = bloco["opcoes"]

        rodando = True
        quadro = pygame.Rect(80, 160, LARGURA - 160, 380)
        area_personagem = pygame.Rect(quadro.left + 40, quadro.top + 80, 230, 250)
        botao_w, botao_h = 230, 60
        botao_a = pygame.Rect(LARGURA // 2 - botao_w - 40, quadro.bottom - 70, botao_w, botao_h)
        botao_b = pygame.Rect(LARGURA // 2 + 40, quadro.bottom - 70, botao_w, botao_h)

        while rodando:
            tela.fill(PRETO)
            desenhar_atributos()

            img = imagens_personagens.get(personagem)
            if img:
                img_redimensionada = pygame.transform.scale(img, (area_personagem.width, area_personagem.height))
                tela.blit(img_redimensionada, area_personagem.topleft)
            else:
                pygame.draw.rect(tela, BRANCO, area_personagem, border_radius=12)

            nome_surf = fonte_texto.render(personagem, True, BRANCO)
            tela.blit(nome_surf, (area_personagem.left + 6, area_personagem.top - 28))

            area_fala_largura = quadro.width - area_personagem.width - 100
            fala_lines = wrap_text(fala, fonte_texto, area_fala_largura)

            if len(fala_lines) > 3:
                fonte_fala = pygame.font.SysFont("arial", 20)
                fala_lines = wrap_text(fala, fonte_fala, area_fala_largura)
            else:
                fonte_fala = fonte_texto

            total_altura = sum([fonte_fala.size(l)[1] + 6 for l in fala_lines])
            y_text = quadro.centery - total_altura // 2

            for line in fala_lines:
                txt_s = fonte_fala.render(line, True, BRANCO)
                rect = txt_s.get_rect(
                    midtop=(area_personagem.right + 40 + area_fala_largura // 2, y_text)
                )
                tela.blit(txt_s, rect)
                y_text += txt_s.get_height() + 6

            mouse = pygame.mouse.get_pos()
            desenhar_botao(botao_a, opcoes[0][0], botao_a.collidepoint(mouse))
            desenhar_botao(botao_b, opcoes[1][0], botao_b.collidepoint(mouse))

            indice_txt = fonte_pequena.render(f"Pergunta {idx + 1} / {len(sequencia)}", True, BRANCO)
            tela.blit(indice_txt, (quadro.left + 10, quadro.top - 26))

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and rodando:
                    escolha = None
                    if botao_a.collidepoint(ev.pos):
                        escolha = 0
                    elif botao_b.collidepoint(ev.pos):
                        escolha = 1
                    if escolha is not None:
                        ajustar_atributos(opcoes[escolha][1])
                        respostas.append((idx + 1, opcoes[escolha][1]))
                        rodando = False

            pygame.display.flip()
            CLOCK.tick(FPS)
    return respostas


# ----------------------------
# Tela final: resultado + nome e e-mail
# ----------------------------
class TextBox:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.text) < 60:
                self.text += event.unicode

    def draw(self, screen):
        cor = AZUL if self.active else BRANCO
        pygame.draw.rect(screen, cor, self.rect, 2, border_radius=6)
        if self.text:
            surf = fonte_texto.render(self.text, True, BRANCO)
        else:
            surf = fonte_texto.render(self.placeholder, True, (150, 150, 150))
        screen.blit(surf, (self.rect.x + 8, self.rect.y + 8))


def email_valido(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


def tela_resultado():
    area_chave, area_info = determinar_area()

    nome_box = TextBox(200, 390, 400, 40, "Digite seu nome")
    email_box = TextBox(200, 440, 400, 40, "Digite seu e-mail")
    botao = pygame.Rect(330, 500, 140, 45)
    erro = ""

    while True:
        tela.fill(PRETO)
        quadro = pygame.Rect(40, 60, LARGURA - 80, 510)
        pygame.draw.rect(tela, CINZA, quadro, border_radius=16)

        titulo_font = pygame.font.SysFont("timesnewroman", 34, bold=True)
        titulo = titulo_font.render(area_chave, True, BRANCO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

        y = 140
        for line in wrap_text(area_info["descricao"], fonte_texto, 650):
            tela.blit(fonte_texto.render(line, True, BRANCO), (75, y))
            y += 28
        tela.blit(fonte_pequena.render(area_info["profissoes"], True, AMARELO), (75, y + 4))
        y += 40

        maior_nome, _ = max(atributos.items(), key=lambda x: x[1])
        menor_nome, _ = min(atributos.items(), key=lambda x: x[1])
        tela.blit(fonte_pequena.render(f"Sua melhor habilidade: {maior_nome}", True, BRANCO), (75, y))
        tela.blit(fonte_pequena.render(f"Habilidade a desenvolver: {menor_nome}", True, BRANCO), (75, y + 25))
        tela.blit(fonte_pequena.render(
            "Digite seu nome e e-mail para receber o gráfico de desempenho:", True, BRANCO), (75, 360))

        nome_box.draw(tela)
        email_box.draw(tela)

        mouse = pygame.mouse.get_pos()
        pygame.draw.rect(tela, (100, 255, 100) if botao.collidepoint(mouse) else VERDE, botao, border_radius=10)
        txt = fonte_texto.render("Enviar", True, PRETO)
        tela.blit(txt, (botao.centerx - txt.get_width() // 2, botao.centery - txt.get_height() // 2))

        if erro:
            e = fonte_pequena.render(erro, True, VERMELHO)
            tela.blit(e, (LARGURA // 2 - e.get_width() // 2, 552))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            nome_box.handle_event(ev)
            email_box.handle_event(ev)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and botao.collidepoint(ev.pos):
                nome = nome_box.text.strip()
                email = email_box.text.strip()
                if not nome or not email:
                    erro = "Preencha o nome e o e-mail."
                elif not email_valido(email):
                    erro = "O e-mail informado não parece válido."
                else:
                    return nome, email

        pygame.display.flip()
        CLOCK.tick(FPS)


def tela_mensagem(linhas, cor=BRANCO, esperar_clique=False):
    """Mostra uma mensagem central. Se esperar_clique, aguarda tecla/clique."""
    while True:
        tela.fill(PRETO)
        y = ALTURA // 2 - 20 * len(linhas)
        for linha in linhas:
            render_centered(linha, fonte_texto, y, cor)
            y += 40
        if esperar_clique:
            render_centered("Clique ou pressione uma tecla para sair.", fonte_pequena, ALTURA - 60, BRANCO)
        pygame.display.flip()
        CLOCK.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if esperar_clique and ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
        if not esperar_clique:
            return


# ---------------------------------------------------------
# Relatório de desempenho e envio por e-mail
# ---------------------------------------------------------
DESCRICOES_ATRIBUTOS = {
    "Adaptabilidade": {
        "descricao": "É a capacidade de lidar com mudanças, ajustar planos e encontrar alternativas diante de imprevistos.",
        "melhora": "Pratique resolver situações com mais de uma estratégia, experimente atividades novas e estabeleça planos alternativos quando organizar uma tarefa."
    },
    "Comunicação": {
        "descricao": "É a capacidade de expressar ideias com clareza, ouvir outras pessoas e compartilhar informações de maneira respeitosa.",
        "melhora": "Treine explicar assuntos em voz alta, participe de apresentações, faça perguntas e pratique ouvir sem interromper."
    },
    "Inteligência Emocional": {
        "descricao": "Envolve reconhecer e administrar as próprias emoções, compreender o sentimento das outras pessoas e lidar com conflitos.",
        "melhora": "Procure identificar o que sente antes de reagir, pratique a empatia, converse sobre conflitos com calma e peça feedback."
    },
    "Criatividade": {
        "descricao": "É a capacidade de imaginar possibilidades, conectar ideias e propor soluções diferentes para desafios.",
        "melhora": "Faça brainstorming, registre ideias, experimente atividades artísticas ou projetos pessoais e tente resolver um mesmo problema de formas diferentes."
    },
    "Liderança": {
        "descricao": "É a capacidade de tomar iniciativa, organizar o grupo, distribuir responsabilidades e motivar as pessoas rumo a um objetivo.",
        "melhora": "Assuma pequenas responsabilidades em trabalhos de grupo, pratique dividir tarefas, incentive os colegas e peça feedback sobre sua atuação."
    }
}


def classificar_pontuacao(valor):
    if valor >= 75:
        return "Destaque"
    if valor >= 60:
        return "Bom desenvolvimento"
    if valor >= 45:
        return "Em desenvolvimento"
    return "Oportunidade de desenvolvimento"


def criar_grafico_pentagono(nome_jogador):
    """Gera em memória um gráfico radar em formato de pentágono (PNG)."""
    nomes = list(atributos.keys())
    valores = [atributos[n] for n in nomes]
    n = len(nomes)

    angulos = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angulos_fech = angulos + angulos[:1]
    valores_fech = valores + valores[:1]

    fig, ax = plt.subplots(figsize=(7.5, 7.5), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)      # primeiro eixo no topo
    ax.set_theta_direction(-1)          # sentido horário
    ax.set_ylim(0, 100)
    ax.set_yticks([])
    ax.grid(False)
    ax.spines["polar"].set_visible(False)

    # Grade em formato de pentágono (níveis 20, 40, 60, 80, 100)
    for nivel in (20, 40, 60, 80, 100):
        ax.plot(angulos_fech, [nivel] * (n + 1), color="#BBBBBB", linewidth=0.9, zorder=1)
        ax.text(angulos[0], nivel + 2, str(nivel), ha="center", va="bottom",
                fontsize=8, color="#777777")
    # Eixos
    for a in angulos:
        ax.plot([a, a], [0, 100], color="#CCCCCC", linewidth=0.9, zorder=1)

    # Área do jogador
    ax.fill(angulos_fech, valores_fech, color="#4F78DC", alpha=0.35, zorder=2)
    ax.plot(angulos_fech, valores_fech, color="#2A4DB0", linewidth=2.5,
            marker="o", markersize=7, zorder=3)

    # A pontuação vai dentro do rótulo, abaixo do nome, para nunca sobrepor o texto.
    rotulos = [f"{nome.replace('Inteligência Emocional', 'Inteligência Emocional')}\n{v}/100"
               for nome, v in zip(nomes, valores)]
    rotulos = [r.replace("Inteligência Emocional\n", "Inteligência\nEmocional\n") for r in rotulos]
    ax.set_xticks(angulos)
    ax.set_xticklabels(rotulos, fontsize=12, fontweight="bold")
    ax.tick_params(axis="x", pad=18)

    ax.set_title(f"Desempenho de {nome_jogador} - Jogo Destino", fontsize=14, pad=35)

    fig.tight_layout()
    imagem = BytesIO()
    fig.savefig(imagem, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    imagem.seek(0)
    return imagem


def montar_relatorio(nome_jogador):
    """Texto simples do relatório."""
    maior_valor = max(atributos.values())
    menor_valor = min(atributos.values())
    destaques = ", ".join(n for n, v in atributos.items() if v == maior_valor)
    desenvolver = ", ".join(n for n, v in atributos.items() if v == menor_valor)
    area_chave, area_info = determinar_area()

    linhas = [
        f"Olá, {nome_jogador}!",
        "",
        "Este é o seu relatório de desempenho no jogo Destino.",
        "O gráfico em pentágono está anexado a este e-mail.",
        "",
        f"Maior resultado: {destaques} ({maior_valor}/100)",
        f"Habilidade a desenvolver: {desenvolver} ({menor_valor}/100)",
        "",
        f"PERFIL PREDOMINANTE: {area_chave}",
        area_info["descricao"],
        area_info["profissoes"],
        "",
        "ANÁLISE DOS ATRIBUTOS"
    ]

    for nome, valor in atributos.items():
        info = DESCRICOES_ATRIBUTOS[nome]
        linhas.extend([
            "",
            f"{nome}: {valor}/100 - {classificar_pontuacao(valor)}",
            info["descricao"],
            f"Sugestão para desenvolver: {info['melhora']}"
        ])

    linhas.extend([
        "",
        "Lembre-se: este resultado representa suas escolhas durante esta partida. "
        "Ele não é um diagnóstico, nem define suas capacidades ou seu futuro.",
        "Use as sugestões como ideias para experimentar e desenvolver suas habilidades.",
        "",
        "Obrigado por jogar Destino!"
    ])
    return "\n".join(linhas)


def montar_relatorio_html(nome_jogador, cid):
    """Versão HTML do relatório, com o gráfico embutido no corpo do e-mail."""
    e = html.escape
    maior_valor = max(atributos.values())
    menor_valor = min(atributos.values())
    destaques = ", ".join(n for n, v in atributos.items() if v == maior_valor)
    desenvolver = ", ".join(n for n, v in atributos.items() if v == menor_valor)
    area_chave, area_info = determinar_area()

    blocos = []
    for nome, valor in atributos.items():
        info = DESCRICOES_ATRIBUTOS[nome]
        blocos.append(
            f"<h3 style='margin-bottom:2px'>{e(nome)}: {valor}/100 "
            f"<span style='font-weight:normal;color:#555'>- {e(classificar_pontuacao(valor))}</span></h3>"
            f"<p style='margin-top:2px'>{e(info['descricao'])}<br>"
            f"<b>Sugestão para desenvolver:</b> {e(info['melhora'])}</p>"
        )

    return f"""\
<html><body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;color:#222">
<h2>Olá, {e(nome_jogador)}!</h2>
<p>Este é o seu relatório de desempenho no jogo <b>Destino</b>.</p>
<p style="text-align:center"><img src="cid:{cid}" alt="Gráfico em pentágono" style="max-width:100%"></p>
<p><b>Maior resultado:</b> {e(destaques)} ({maior_valor}/100)<br>
<b>Habilidade a desenvolver:</b> {e(desenvolver)} ({menor_valor}/100)</p>
<h3>Perfil predominante: {e(area_chave)}</h3>
<p>{e(area_info['descricao'])}<br><i>{e(area_info['profissoes'])}</i></p>
<hr>
<h2>Análise dos atributos</h2>
{''.join(blocos)}
<hr>
<p style="color:#555;font-size:13px">Este resultado representa suas escolhas durante esta partida.
Ele não é um diagnóstico, nem define suas capacidades ou seu futuro.
Use as sugestões como ideias para experimentar e desenvolver suas habilidades.</p>
<p>Obrigado por jogar Destino!</p>
</body></html>"""


def enviar_relatorio_email(nome_jogador, email_destino):
    """
    Envia o relatório e o gráfico em pentágono por SMTP.
    Configure as variáveis de ambiente:
      DESTINO_EMAIL_REMETENTE  (ex.: seuemail@gmail.com)
      DESTINO_EMAIL_SENHA      (no Gmail, use uma "senha de app")
    """
    remetente = os.getenv("DESTINO_EMAIL_REMETENTE")
    senha = os.getenv("DESTINO_EMAIL_SENHA")

    if not remetente or not senha:
        raise RuntimeError(
            "Configure DESTINO_EMAIL_REMETENTE e DESTINO_EMAIL_SENHA "
            "nas variáveis de ambiente antes de enviar."
        )
    if not email_valido(email_destino):
        raise ValueError("O endereço de e-mail informado não é válido.")

    grafico_bytes = criar_grafico_pentagono(nome_jogador).getvalue()
    cid = make_msgid(domain="destino.local")  # formato <...@destino.local>

    mensagem = EmailMessage()
    mensagem["Subject"] = "Seu resultado no jogo Destino"
    mensagem["From"] = remetente
    mensagem["To"] = email_destino
    mensagem.set_content(montar_relatorio(nome_jogador))
    mensagem.add_alternative(montar_relatorio_html(nome_jogador, cid[1:-1]), subtype="html")

    # Gráfico dentro do corpo HTML
    mensagem.get_payload()[1].add_related(
        grafico_bytes, maintype="image", subtype="png", cid=cid
    )
    # Gráfico também como anexo
    mensagem.add_attachment(
        grafico_bytes,
        maintype="image",
        subtype="png",
        filename="grafico_pentagono_destino.png"
    )

    # Configuração para Gmail. Para outro provedor, ajuste servidor e porta.
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as servidor:
        servidor.login(remetente, senha)
        servidor.send_message(mensagem)


# ----------------------------
# Execução principal
# ----------------------------
def main():
    desenhar_intro_fade()

    esperando = True
    while esperando:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                esperando = False
        CLOCK.tick(FPS)

    random.shuffle(perguntas)
    registros = tela_perguntas(perguntas[:8])

    # Ao terminar, o jogador escreve nome e e-mail.
    nome, email = tela_resultado()

    # Envia o relatório com o gráfico em pentágono.
    tela_mensagem(["Enviando seu relatório...", "Aguarde um instante."])
    try:
        enviar_relatorio_email(nome, email)
        print(f"Relatório enviado com sucesso para {email}.")
        tela_mensagem(["Relatório enviado!", f"Confira a caixa de entrada de {email}.",
                       "(Veja também a pasta de spam.)"], VERDE, esperar_clique=True)
    except Exception as erro:
        print(f"Não foi possível enviar o relatório: {erro}")
        tela_mensagem(["Não foi possível enviar o e-mail.",
                       "Confira a conexão e as configurações de e-mail."], VERMELHO,
                      esperar_clique=True)

    pygame.quit()

    return {
        "nome": nome,
        "email": email,
        "regi": registros,
        "atributos": atributos.copy()
    }


if __name__ == "__main__":
    main()
