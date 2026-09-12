import os
import re
import math
import shutil
import subprocess
import unicodedata
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# CONFIGURAÇÃO FIXA
# ============================================================

QUANTIDADE_VIDEOS = 45
PERGUNTAS_POR_VIDEO = 5
TEMPO_ESCOLHA = 3

VOZ = "pt-BR-AntonioNeural"
VELOCIDADE_VOZ = "+10%"

W = 1080
H = 1920
FPS = 30

DURACAO_MARCATEXTO = 0.90
PAUSA_DEPOIS_RESPOSTA = 0.55

AUDIO_HZ = 48000
AUDIO_CHANNELS = 2

FUSO = ZoneInfo("America/Fortaleza")
DATA_DO_DIA = datetime.now(FUSO).strftime("%Y-%m-%d")

PASTA_RAIZ = Path("output")
PASTA_TMP = Path("_tmp_juhquiz_rosa")
PASTA_SAIDA = PASTA_RAIZ / DATA_DO_DIA

# ============================================================
# 45 TEMAS × 5 PERGUNTAS
# Cada tema = 1 vídeo.
# correta: 0=A, 1=B, 2=C
# ============================================================
# JuhQuiz — 45 temas, 5 perguntas por tema (225 perguntas)
# Respostas corretas variam entre 0=A, 1=B e 2=C.

QUIZZES = {
    "Rock in Rio 2026": [
        {"pergunta": "Qual banda foi headliner do Palco Mundo em 4 de setembro de 2026?", "alternativas": ["Foo Fighters", "Maroon 5", "Twenty One Pilots"], "correta": 0},
        {"pergunta": "Qual artista foi o headliner do Palco Mundo em 7 de setembro de 2026?", "alternativas": ["Gilberto Gil", "Elton John", "Calvin Harris"], "correta": 1},
        {"pergunta": "Qual grupo de K-pop se apresentou no Palco Mundo em 11 de setembro de 2026?", "alternativas": ["NEXZ", "BLACKPINK", "Stray Kids"], "correta": 2},
        {"pergunta": "Qual banda foi anunciada para fechar o Palco Mundo em 12 de setembro de 2026?", "alternativas": ["Avenged Sevenfold", "Maroon 5", "The Hives"], "correta": 1},
        {"pergunta": "Em qual cidade acontece o Rock in Rio 2026?", "alternativas": ["Rio de Janeiro", "São Paulo", "Belo Horizonte"], "correta": 0},
    ],

    "Casal Flertando": [
        {"pergunta": "Qual atitude costuma demonstrar interesse de forma respeitosa?", "alternativas": ["Fazer perguntas e ouvir com atenção", "Ignorar tudo o que a pessoa diz", "Insistir depois de um não"], "correta": 0},
        {"pergunta": "Durante uma conversa, qual comportamento pode indicar que o papo está fluindo?", "alternativas": ["Responder apenas com 'sim' e 'não'", "Os dois fazem perguntas e continuam o assunto", "Um dos dois olha o celular o tempo todo"], "correta": 1},
        {"pergunta": "Qual mensagem tem mais cara de flerte leve?", "alternativas": ["Ok.", "Preciso falar com você sobre trabalho.", "Vi isso e lembrei de você 😏"], "correta": 2},
        {"pergunta": "Qual atitude é essencial mesmo quando existe química?", "alternativas": ["Respeitar limites", "Forçar intimidade", "Cobrar resposta imediata"], "correta": 0},
        {"pergunta": "Qual sinal sugere mais reciprocidade numa paquera?", "alternativas": ["Só uma pessoa inicia todas as conversas", "As duas pessoas procuram manter contato", "Uma pessoa evita qualquer conversa"], "correta": 1},
    ],

    "Receitas com Morango": [
        {"pergunta": "Qual ingrediente combina com morango para preparar uma ganache?", "alternativas": ["Chocolate", "Arroz", "Farinha de mandioca"], "correta": 0},
        {"pergunta": "Qual sobremesa costuma levar base de biscoito, creme de queijo e cobertura de morango?", "alternativas": ["Pudim", "Cheesecake", "Quindim"], "correta": 1},
        {"pergunta": "Qual combinação é comum em uma geleia simples de morango?", "alternativas": ["Morango e sal", "Morango e óleo", "Morango e açúcar"], "correta": 2},
        {"pergunta": "Qual sobremesa pode ser feita com morango, suspiro e creme?", "alternativas": ["Merengue de morango", "Pé de moleque", "Cocada"], "correta": 0},
        {"pergunta": "Para fazer um milk-shake de morango, qual ingrediente é muito usado junto da fruta?", "alternativas": ["Molho de tomate", "Sorvete", "Feijão"], "correta": 1},
    ],

    "Penteados e Roupas dos Anos 90": [
        {"pergunta": "Qual acessório de cabelo foi muito popular nos anos 90 e voltou à moda?", "alternativas": ["Scrunchie", "Cartola", "Gravata borboleta"], "correta": 0},
        {"pergunta": "Qual peça jeans era muito associada ao visual casual dos anos 90?", "alternativas": ["Terno de linho", "Jardineira", "Capa de chuva"], "correta": 1},
        {"pergunta": "Qual penteado com duas mechas soltas na frente marcou muitos looks dos anos 90?", "alternativas": ["Coque samurai", "Moicano punk", "Coque com mechas frontais"], "correta": 2},
        {"pergunta": "Qual calçado de sola alta virou símbolo de vários looks dos anos 90?", "alternativas": ["Tênis plataforma", "Sapato social clássico", "Bota de montaria"], "correta": 0},
        {"pergunta": "Qual acessório justo no pescoço foi febre na década de 90?", "alternativas": ["Tiara de princesa", "Choker", "Gravata slim"], "correta": 1},
    ],

    "Memes Brasileiros Clássicos": [
        {"pergunta": "Qual personagem aparece no famoso meme de cálculos confusos?", "alternativas": ["Nazaré Tedesco", "Carminha", "Odete Roitman"], "correta": 0},
        {"pergunta": "A expressão 'Que deselegante!' ficou famosa em uma cobertura de qual tipo de programa?", "alternativas": ["Programa de culinária", "Telejornal", "Desenho animado"], "correta": 1},
        {"pergunta": "Qual frase virou meme depois de uma criança comentar um presente de Natal?", "alternativas": ["É sobre isso", "Receba!", "Eu queria um iPhone"], "correta": 2},
        {"pergunta": "O meme 'Já acabou, Jéssica?' nasceu de qual situação?", "alternativas": ["Uma briga gravada em vídeo", "Uma propaganda de refrigerante", "Uma cena de novela"], "correta": 0},
        {"pergunta": "Qual reação combina com o meme 'Nazaré confusa'?", "alternativas": ["Comemoração", "Confusão mental", "Sono"], "correta": 1},
    ],

    "Gírias da Internet": [
        {"pergunta": "Na internet, o que significa 'POV'?", "alternativas": ["Ponto de vista", "Postagem oficial viral", "Perfil online verificado"], "correta": 0},
        {"pergunta": "Quando alguém diz que algo 'flopou', o que geralmente quer dizer?", "alternativas": ["Ficou caro", "Não teve o sucesso esperado", "Foi apagado por lei"], "correta": 1},
        {"pergunta": "O que significa dizer que alguém 'hypeou' alguma coisa?", "alternativas": ["Esqueceu completamente", "Cancelou um evento", "Criou muita expectativa ou empolgação"], "correta": 2},
        {"pergunta": "Na linguagem online, o que é uma 'thread'?", "alternativas": ["Sequência de publicações conectadas", "Filtro de foto", "Tipo de emoji"], "correta": 0},
        {"pergunta": "Quando algo é chamado de 'cringe', costuma ser visto como o quê?", "alternativas": ["Muito caro", "Constrangedor ou cafona", "Extremamente raro"], "correta": 1},
    ],

    "Emojis e Seus Significados": [
        {"pergunta": "Qual emoji costuma representar risada intensa?", "alternativas": ["😂", "😴", "😡"], "correta": 0},
        {"pergunta": "Qual emoji normalmente indica dúvida ou reflexão?", "alternativas": ["🥳", "🤔", "😭"], "correta": 1},
        {"pergunta": "Qual emoji é muito usado para representar algo 'pegando fogo' ou muito popular?", "alternativas": ["🌧️", "🧊", "🔥"], "correta": 2},
        {"pergunta": "Qual emoji costuma representar aprovação?", "alternativas": ["👍", "👎", "💤"], "correta": 0},
        {"pergunta": "Qual emoji costuma ser usado para demonstrar vergonha alheia ou constrangimento?", "alternativas": ["🎉", "😬", "🌞"], "correta": 1},
    ],

    "Ditados Populares Incompletos": [
        {"pergunta": "Complete: 'Água mole em pedra dura...'", "alternativas": ["tanto bate até que fura", "quem espera sempre alcança", "cada macaco no seu galho"], "correta": 0},
        {"pergunta": "Complete: 'Quem não tem cão...'", "alternativas": ["não vai à caça", "caça com gato", "fica em casa"], "correta": 1},
        {"pergunta": "Complete: 'De grão em grão...'", "alternativas": ["a chuva enche o rio", "o tempo passa", "a galinha enche o papo"], "correta": 2},
        {"pergunta": "Complete: 'Mais vale um pássaro na mão...'", "alternativas": ["do que dois voando", "do que um no telhado", "do que três cantando"], "correta": 0},
        {"pergunta": "Complete: 'Em casa de ferreiro...'", "alternativas": ["todo mundo trabalha", "o espeto é de pau", "a porta é de ferro"], "correta": 1},
    ],

    "Expressões Nordestinas": [
        {"pergunta": "No Nordeste, 'oxente' costuma expressar o quê?", "alternativas": ["Surpresa ou estranhamento", "Sono profundo", "Silêncio"], "correta": 0},
        {"pergunta": "Quando alguém está 'aperreado', geralmente está como?", "alternativas": ["Com muita fome", "Preocupado ou aflito", "Muito descansado"], "correta": 1},
        {"pergunta": "Em muitos lugares do Nordeste, 'mangar' de alguém significa o quê?", "alternativas": ["Abraçar", "Ajudar", "Zombar ou tirar graça"], "correta": 2},
        {"pergunta": "Dizer que algo é 'arretado' pode significar que é o quê?", "alternativas": ["Muito bom ou intenso", "Sem importância", "Sempre pequeno"], "correta": 0},
        {"pergunta": "A expressão 'visse?' costuma ser usada para quê?", "alternativas": ["Encerrar uma música", "Reforçar o que foi dito", "Pedir comida"], "correta": 1},
    ],

    "Palavras com Duplo Sentido": [
        {"pergunta": "Qual palavra pode significar uma fruta e também parte de uma camisa?", "alternativas": ["Manga", "Pera", "Uva"], "correta": 0},
        {"pergunta": "Qual palavra pode ser um lugar para sentar ou uma instituição financeira?", "alternativas": ["Mesa", "Banco", "Janela"], "correta": 1},
        {"pergunta": "Qual palavra pode ser usada para uma fonte de luz de cera e também para uma peça de barco?", "alternativas": ["Farol", "Lâmpada", "Vela"], "correta": 2},
        {"pergunta": "Qual palavra pode indicar uma nascente de água e também um recurso tipográfico?", "alternativas": ["Fonte", "Rio", "Letra"], "correta": 0},
        {"pergunta": "Qual palavra pode ser uma peça elástica de metal e também aparecer em mecanismos de colchão?", "alternativas": ["Cabo", "Mola", "Roda"], "correta": 1},
    ],

    "Brinquedos dos Anos 90": [
        {"pergunta": "Qual brinquedo eletrônico de bolso exigia cuidar de um bichinho virtual?", "alternativas": ["Tamagotchi", "Autorama", "Pião"], "correta": 0},
        {"pergunta": "Qual brinquedo tinha pequenos discos de plástico usados em disputas e coleções?", "alternativas": ["Lego", "Tazos", "Bambolê"], "correta": 1},
        {"pergunta": "Qual brinquedo de mola 'caminhava' por degraus?", "alternativas": ["Genius", "Pogobol", "Mola maluca"], "correta": 2},
        {"pergunta": "Qual brinquedo exigia equilíbrio sobre uma bola presa a uma plataforma?", "alternativas": ["Pogobol", "Aquaplay", "Vai-e-vem"], "correta": 0},
        {"pergunta": "Qual brinquedo aquático de argolas funcionava apertando botões para movimentar as peças?", "alternativas": ["Io-iô", "Aquaplay", "Beyblade"], "correta": 1},
    ],

    "Programas de TV dos Anos 90": [
        {"pergunta": "Qual programa infantil da TV Cultura tinha personagens como Nino, Morgana e Dr. Victor?", "alternativas": ["Castelo Rá-Tim-Bum", "TV Colosso", "Xou da Xuxa"], "correta": 0},
        {"pergunta": "Qual programa humorístico se passava em grande parte num apartamento no Largo do Arouche?", "alternativas": ["Casseta & Planeta", "Sai de Baixo", "Escolinha do Professor Raimundo"], "correta": 1},
        {"pergunta": "Qual programa infantil da Globo usava bonecos de cachorros como apresentadores?", "alternativas": ["Angel Mix", "Bom Dia & Cia", "TV Colosso"], "correta": 2},
        {"pergunta": "Qual apresentadora comandou o 'Xuxa Park' nos anos 90?", "alternativas": ["Xuxa", "Eliana", "Angélica"], "correta": 0},
        {"pergunta": "Qual programa de auditório ficou associado ao bordão 'Quem quer dinheiro?'?", "alternativas": ["Domingão do Faustão", "Programa Silvio Santos", "Planeta Xuxa"], "correta": 1},
    ],

    "Tecnologias que Sumiram": [
        {"pergunta": "Qual mídia quadrada era usada para salvar arquivos em computadores antigos?", "alternativas": ["Disquete", "Blu-ray", "Cartão SD"], "correta": 0},
        {"pergunta": "Qual aparelho era usado para enviar documentos pela linha telefônica?", "alternativas": ["Pager", "Fax", "MP3 player"], "correta": 1},
        {"pergunta": "Qual fita era usada para assistir filmes em videocassetes?", "alternativas": ["MiniDisc", "Cassete de áudio", "VHS"], "correta": 2},
        {"pergunta": "Qual aparelho portátil tocava CDs?", "alternativas": ["Discman", "Walkie-talkie", "Fax"], "correta": 0},
        {"pergunta": "Qual aparelho recebia pequenas mensagens e números antes dos celulares se popularizarem?", "alternativas": ["DVD player", "Pager", "Scanner"], "correta": 1},
    ],

    "Celulares Antigos": [
        {"pergunta": "Qual jogo ficou famoso nos celulares Nokia antigos?", "alternativas": ["Snake", "Fortnite", "Free Fire"], "correta": 0},
        {"pergunta": "Antes das telas sensíveis ao toque, como muitos celulares eram controlados?", "alternativas": ["Por voz apenas", "Por teclas físicas", "Por gestos no ar"], "correta": 1},
        {"pergunta": "Qual recurso era muito usado para personalizar celulares antes dos smartphones?", "alternativas": ["Filtros de realidade aumentada", "Stories", "Toques polifônicos"], "correta": 2},
        {"pergunta": "Qual tecnologia permitia enviar arquivos entre celulares próximos antes do Bluetooth se popularizar?", "alternativas": ["Infravermelho", "GPS", "NFC"], "correta": 0},
        {"pergunta": "Qual formato de mensagem dominava os celulares antes dos aplicativos de conversa?", "alternativas": ["Podcast", "SMS", "Streaming"], "correta": 1},
    ],

    "Videogames Retrô": [
        {"pergunta": "Qual personagem é o mascote mais famoso da Nintendo?", "alternativas": ["Mario", "Sonic", "Crash"], "correta": 0},
        {"pergunta": "Qual empresa lançou o Mega Drive?", "alternativas": ["Nintendo", "Sega", "Atari"], "correta": 1},
        {"pergunta": "Em qual console o primeiro jogo de 'Sonic the Hedgehog' ficou famoso?", "alternativas": ["Super Nintendo", "PlayStation 2", "Mega Drive"], "correta": 2},
        {"pergunta": "Qual jogo clássico envolve encaixar blocos que caem?", "alternativas": ["Tetris", "Pac-Man", "Frogger"], "correta": 0},
        {"pergunta": "Qual personagem amarelo come pontos em um labirinto?", "alternativas": ["Kirby", "Pac-Man", "Donkey Kong"], "correta": 1},
    ],

    "Brincadeiras de Infância": [
        {"pergunta": "Em qual brincadeira uma pessoa conta enquanto as outras se escondem?", "alternativas": ["Esconde-esconde", "Amarelinha", "Queimada"], "correta": 0},
        {"pergunta": "Qual brincadeira usa casas numeradas desenhadas no chão?", "alternativas": ["Pega-pega", "Amarelinha", "Cabra-cega"], "correta": 1},
        {"pergunta": "Qual brincadeira usa uma bola para eliminar jogadores do time adversário?", "alternativas": ["Bambolê", "Passa-anel", "Queimada"], "correta": 2},
        {"pergunta": "Qual brincadeira envolve girar uma corda e pular sem tropeçar?", "alternativas": ["Pular corda", "Telefone sem fio", "Estátua"], "correta": 0},
        {"pergunta": "Na brincadeira 'telefone sem fio', o que é passado de pessoa para pessoa?", "alternativas": ["Uma bola", "Uma mensagem sussurrada", "Uma carta"], "correta": 1},
    ],

    "Comerciais Antigos da TV Brasileira": [
        {"pergunta": "Qual produto ficou conhecido pelo bordão 'Tomou Doril, a dor sumiu'?", "alternativas": ["Doril", "Leite Moça", "Bombril"], "correta": 0},
        {"pergunta": "A frase 'Não é assim uma Brastemp' ficou ligada a qual tipo de marca?", "alternativas": ["Banco", "Eletrodomésticos", "Refrigerante"], "correta": 1},
        {"pergunta": "Qual produto infantil ficou associado ao famoso 'Compre Batom'?", "alternativas": ["Biscoito", "Refrigerante", "Chocolate"], "correta": 2},
        {"pergunta": "O garoto-propaganda conhecido como 'Garoto Bombril' anunciava qual produto?", "alternativas": ["Palha de aço", "Sabonete", "Achocolatado"], "correta": 0},
        {"pergunta": "O jingle 'O tempo passa, o tempo voa...' ficou famoso em propaganda de qual setor?", "alternativas": ["Automóveis", "Banco", "Sorvetes"], "correta": 1},
    ],

    "Embalagens que Mudaram com o Tempo": [
        {"pergunta": "Qual material substituiu muitas garrafas de vidro em refrigerantes vendidos no varejo?", "alternativas": ["PET", "Madeira", "Cerâmica"], "correta": 0},
        {"pergunta": "Qual embalagem cartonada é comum para leite e sucos de longa vida?", "alternativas": ["Lata de aço", "Caixa longa vida", "Papel manteiga"], "correta": 1},
        {"pergunta": "Qual recurso passou a facilitar a abertura de muitas latas de bebida?", "alternativas": ["Rolha", "Zíper", "Anel de abertura"], "correta": 2},
        {"pergunta": "Qual preocupação ganhou espaço no design moderno de embalagens?", "alternativas": ["Reciclabilidade", "Aumento do peso", "Uso de mais camadas sem necessidade"], "correta": 0},
        {"pergunta": "Qual informação passou a ganhar destaque obrigatório em muitas embalagens de alimentos?", "alternativas": ["Horóscopo", "Informação nutricional", "Número de seguidores"], "correta": 1},
    ],

    "Produtos que Mudaram de Nome": [
        {"pergunta": "Qual rede social passou a se chamar X?", "alternativas": ["Twitter", "Instagram", "TikTok"], "correta": 0},
        {"pergunta": "O chatbot Bard, do Google, passou a usar qual nome?", "alternativas": ["Copilot", "Gemini", "Alexa"], "correta": 1},
        {"pergunta": "A franquia de futebol PES passou a ser chamada de quê?", "alternativas": ["FIFA Street", "Winning Soccer", "eFootball"], "correta": 2},
        {"pergunta": "O pacote Office 365 passou a ser promovido principalmente sob qual nome?", "alternativas": ["Microsoft 365", "Windows 365", "Teams 365"], "correta": 0},
        {"pergunta": "A empresa antes chamada Facebook, Inc. adotou qual nome corporativo?", "alternativas": ["Alphabet", "Meta", "ByteDance"], "correta": 1},
    ],

    "Slogans Famosos": [
        {"pergunta": "Qual marca esportiva usa o slogan 'Just Do It'?", "alternativas": ["Nike", "Adidas", "Puma"], "correta": 0},
        {"pergunta": "Qual marca ficou conhecida pelo slogan 'Think Different'?", "alternativas": ["Samsung", "Apple", "Sony"], "correta": 1},
        {"pergunta": "Qual rede de fast-food usa no Brasil a ideia 'Amo muito tudo isso'?", "alternativas": ["Subway", "Burger King", "McDonald's"], "correta": 2},
        {"pergunta": "Qual marca de cosméticos é associada à frase 'Porque você vale muito'?", "alternativas": ["L'Oréal Paris", "Nivea", "Dove"], "correta": 0},
        {"pergunta": "Qual bandeira de cartão ficou famosa por campanhas com a ideia de que certas coisas 'não têm preço'?", "alternativas": ["Visa", "Mastercard", "Elo"], "correta": 1},
    ],

    "Acessórios que Voltaram à Moda": [
        {"pergunta": "Qual acessório de cabelo de tecido voltou com força nos últimos anos?", "alternativas": ["Scrunchie", "Monóculo", "Cartola"], "correta": 0},
        {"pergunta": "Qual chapéu de aba caída, popular nos anos 90, voltou a aparecer em looks casuais?", "alternativas": ["Fedora", "Bucket hat", "Chapéu-coco"], "correta": 1},
        {"pergunta": "Qual presilha grande voltou a ser usada para prender o cabelo rapidamente?", "alternativas": ["Broche", "Tiara de metal", "Piranha de cabelo"], "correta": 2},
        {"pergunta": "Qual bolsa pequena e alongada, popular nos anos 90 e 2000, voltou à moda?", "alternativas": ["Bolsa baguete", "Mala executiva", "Pochete de trilha"], "correta": 0},
        {"pergunta": "Qual colar justo ao pescoço voltou em ciclos de moda?", "alternativas": ["Corrente longa", "Choker", "Terço"], "correta": 1},
    ],

    "Maquiagem dos Anos 90": [
        {"pergunta": "Qual estilo de sobrancelha foi muito marcante nos anos 90?", "alternativas": ["Sobrancelha fina", "Sobrancelha colorida de neon", "Sobrancelha totalmente raspada como regra"], "correta": 0},
        {"pergunta": "Qual cor de batom marcou muitos looks dos anos 90?", "alternativas": ["Azul metálico", "Marrom", "Verde-limão"], "correta": 1},
        {"pergunta": "Qual acabamento de sombra foi bastante usado na década?", "alternativas": ["Efeito molhado permanente", "Glitter holográfico grosso em todo look", "Sombra perolada ou frost"], "correta": 2},
        {"pergunta": "Qual técnica de lábios era comum em muitos looks dos anos 90?", "alternativas": ["Contorno mais escuro que o batom", "Batom apenas no centro", "Sem qualquer contorno"], "correta": 0},
        {"pergunta": "Qual acabamento de pele era muito associado à maquiagem da época?", "alternativas": ["Ultra iluminado com glitter", "Mais matte", "Efeito molhado"], "correta": 1},
    ],

    "Unhas e Nail Art": [
        {"pergunta": "Qual estilo deixa a ponta da unha branca e a base natural?", "alternativas": ["Francesinha", "Ombré", "Marmorizada"], "correta": 0},
        {"pergunta": "Qual técnica cria uma transição suave entre duas cores?", "alternativas": ["Carimbo", "Ombré", "Craquelado"], "correta": 1},
        {"pergunta": "Qual acabamento produz efeito espelhado metálico nas unhas?", "alternativas": ["Jelly", "Matte", "Chrome"], "correta": 2},
        {"pergunta": "Qual ferramenta é muito usada para criar bolinhas perfeitas na nail art?", "alternativas": ["Dotting tool", "Pinça de sobrancelha", "Esponja de banho"], "correta": 0},
        {"pergunta": "No estilo 'negative space', o que costuma aparecer no desenho?", "alternativas": ["Somente glitter", "Partes da unha sem esmalte ou transparentes", "Apenas esmalte preto"], "correta": 1},
    ],

    "Moda de Festivais de Música": [
        {"pergunta": "Qual tipo de bolsa costuma ser prática em festivais por deixar as mãos livres?", "alternativas": ["Bolsa transversal", "Mala de rodinhas", "Pasta executiva"], "correta": 0},
        {"pergunta": "Qual item ajuda a proteger do sol em festivais ao ar livre?", "alternativas": ["Cachecol de lã", "Protetor solar", "Luva de couro"], "correta": 1},
        {"pergunta": "Qual escolha costuma ser mais confortável para muitas horas em pé?", "alternativas": ["Salto agulha muito alto", "Sapato rígido novo", "Tênis confortável"], "correta": 2},
        {"pergunta": "Qual peça é útil quando a temperatura cai à noite?", "alternativas": ["Camada leve ou jaqueta", "Somente roupa de banho", "Avental de cozinha"], "correta": 0},
        {"pergunta": "Para brilho no rosto, qual opção é mais responsável ambientalmente?", "alternativas": ["Purpurina plástica comum", "Glitter biodegradável", "Confete metálico"], "correta": 1},
    ],

    "Looks Icônicos de Tapete Vermelho": [
        {"pergunta": "Qual artista ficou famosa pelo vestido de carne usado no MTV Video Music Awards de 2010?", "alternativas": ["Lady Gaga", "Beyoncé", "Adele"], "correta": 0},
        {"pergunta": "Quem usou o famoso vestido de cisne no Oscar de 2001?", "alternativas": ["Cher", "Björk", "Madonna"], "correta": 1},
        {"pergunta": "Qual artista usou um enorme vestido amarelo de Guo Pei no Met Gala de 2015?", "alternativas": ["Taylor Swift", "Katy Perry", "Rihanna"], "correta": 2},
        {"pergunta": "Qual atriz apareceu com um vestido inspirado em Cinderela no Met Gala de 2019?", "alternativas": ["Zendaya", "Emma Stone", "Anne Hathaway"], "correta": 0},
        {"pergunta": "Quem chamou atenção no Oscar de 2019 com um look que misturava smoking e vestido?", "alternativas": ["Timothée Chalamet", "Billy Porter", "Rami Malek"], "correta": 1},
    ],

    "Receitas de Air Fryer": [
        {"pergunta": "Qual alimento congelado costuma ficar crocante rapidamente na air fryer?", "alternativas": ["Batata frita congelada", "Gelatina", "Sorvete"], "correta": 0},
        {"pergunta": "Qual cuidado ajuda o ar quente a circular melhor?", "alternativas": ["Encher o cesto até o topo", "Evitar amontoar os alimentos", "Cobrir todas as entradas de ar"], "correta": 1},
        {"pergunta": "Qual receita simples pode ser feita na air fryer com pão, queijo e molho?", "alternativas": ["Sopa", "Pudim líquido", "Mini pizza"], "correta": 2},
        {"pergunta": "Qual item pode ser assado na air fryer para um lanche rápido?", "alternativas": ["Pão de queijo", "Suco", "Iogurte"], "correta": 0},
        {"pergunta": "O que é recomendável fazer no meio do preparo de batatas ou legumes?", "alternativas": ["Adicionar água até cobrir", "Mexer ou virar", "Desligar e deixar por uma hora"], "correta": 1},
    ],

    "Sobremesas com 3 Ingredientes": [
        {"pergunta": "Qual trio forma uma mousse de limão simples?", "alternativas": ["Leite condensado, creme de leite e limão", "Arroz, sal e limão", "Farinha, óleo e limão"], "correta": 0},
        {"pergunta": "Qual ingrediente é essencial num brigadeiro simples junto com leite condensado e manteiga?", "alternativas": ["Vinagre", "Chocolate em pó", "Molho de tomate"], "correta": 1},
        {"pergunta": "Qual fruta congelada pode virar sorvete cremoso quando batida?", "alternativas": ["Limão inteiro com casca", "Melancia com sementes", "Banana"], "correta": 2},
        {"pergunta": "Qual combinação pode virar um docinho simples de coco?", "alternativas": ["Leite condensado, coco ralado e manteiga", "Feijão, coco e sal", "Macarrão, açúcar e coco"], "correta": 0},
        {"pergunta": "Para uma sobremesa rápida de chocolate, qual ingrediente ajuda a deixar uma ganache cremosa?", "alternativas": ["Água com sal", "Creme de leite", "Farinha de mandioca"], "correta": 1},
    ],

    "Comidas de Boteco": [
        {"pergunta": "Qual petisco é feito com pele ou gordura de porco frita até ficar crocante?", "alternativas": ["Torresmo", "Pudim", "Cuscuz doce"], "correta": 0},
        {"pergunta": "Qual petisco costuma levar bacalhau desfiado em uma massa frita?", "alternativas": ["Pastel de nata", "Bolinho de bacalhau", "Pão de mel"], "correta": 1},
        {"pergunta": "Qual opção é comum em botecos e leva linguiça com cebola?", "alternativas": ["Canjica", "Quindim", "Calabresa acebolada"], "correta": 2},
        {"pergunta": "Qual raiz frita é muito servida como petisco?", "alternativas": ["Mandioca", "Beterraba crua", "Nabo cozido"], "correta": 0},
        {"pergunta": "Qual salgado em formato alongado ou de gota costuma ter recheio de frango?", "alternativas": ["Quibe cru", "Coxinha", "Sonho"], "correta": 1},
    ],

    "Lanches de Festa Infantil": [
        {"pergunta": "Qual doce brasileiro é feito principalmente com leite condensado e chocolate?", "alternativas": ["Brigadeiro", "Quindim", "Rapadura"], "correta": 0},
        {"pergunta": "Qual docinho branco costuma levar coco ralado?", "alternativas": ["Cajuzinho", "Beijinho", "Paçoca"], "correta": 1},
        {"pergunta": "Qual salgado de festa geralmente leva recheio de frango?", "alternativas": ["Sonho", "Churros", "Coxinha"], "correta": 2},
        {"pergunta": "Qual lanche pequeno costuma levar pão, salsicha e molho?", "alternativas": ["Mini cachorro-quente", "Tapioca doce", "Pão de queijo recheado de goiabada"], "correta": 0},
        {"pergunta": "Qual doce de amendoim é comum em festas e costuma ter formato de bolinha ou caju?", "alternativas": ["Beijinho", "Cajuzinho", "Gelatina"], "correta": 1},
    ],

    "Receitas com Banana": [
        {"pergunta": "Qual bolo americano popular usa banana madura na massa e é chamado de 'banana bread'?", "alternativas": ["Pão de banana", "Pão de alho", "Bolo de milho"], "correta": 0},
        {"pergunta": "Na sobremesa nordestina cartola, banana é combinada principalmente com o quê?", "alternativas": ["Carne seca", "Queijo", "Peixe"], "correta": 1},
        {"pergunta": "Qual ingrediente pode ser usado com banana e ovos numa panqueca simples?", "alternativas": ["Molho shoyu", "Mostarda", "Aveia"], "correta": 2},
        {"pergunta": "Qual tempero combina muito com banana assada ou frita?", "alternativas": ["Canela", "Páprica picante obrigatoriamente", "Cominho em excesso"], "correta": 0},
        {"pergunta": "Qual bebida pode ser feita batendo banana com leite?", "alternativas": ["Caldo", "Vitamina", "Molho"], "correta": 1},
    ],

    "Receitas com Chocolate": [
        {"pergunta": "Qual sobremesa assada costuma ter textura densa e quadrada?", "alternativas": ["Brownie", "Pudim de pão", "Suspiro"], "correta": 0},
        {"pergunta": "Qual mistura de chocolate e creme de leite é usada em coberturas e recheios?", "alternativas": ["Merengue", "Ganache", "Calda de caramelo"], "correta": 1},
        {"pergunta": "Qual sobremesa brasileira leva leite condensado, manteiga e chocolate?", "alternativas": ["Cocada", "Pé de moleque", "Brigadeiro"], "correta": 2},
        {"pergunta": "Qual sobremesa costuma ser servida com frutas mergulhadas em chocolate derretido?", "alternativas": ["Fondue de chocolate", "Arroz-doce", "Manjar"], "correta": 0},
        {"pergunta": "Qual sobremesa aerada pode ser feita com chocolate e creme?", "alternativas": ["Paçoca", "Mousse", "Cuscuz"], "correta": 1},
    ],

    "Comidas de São João": [
        {"pergunta": "Qual comida é feita com milho verde ralado ou triturado e cozido em palha?", "alternativas": ["Pamonha", "Coxinha", "Pastel"], "correta": 0},
        {"pergunta": "Qual doce leva amendoim e açúcar e é muito comum em festas juninas?", "alternativas": ["Quindim", "Pé de moleque", "Pudim"], "correta": 1},
        {"pergunta": "Qual bebida quente costuma levar leite, açúcar e especiarias, podendo incluir milho em algumas versões regionais?", "alternativas": ["Limonada", "Água de coco", "Bebida de milho quente"], "correta": 2},
        {"pergunta": "Qual bolo é presença frequente nas festas juninas?", "alternativas": ["Bolo de milho", "Bolo de sushi", "Bolo de macarrão"], "correta": 0},
        {"pergunta": "Qual grão é a base do mungunzá doce?", "alternativas": ["Arroz integral", "Milho branco", "Feijão preto"], "correta": 1},
    ],

    "Combinações de Comida Estranhas": [
        {"pergunta": "Qual combinação doce e salgada é conhecida no Brasil como 'Romeu e Julieta'?", "alternativas": ["Queijo com goiabada", "Arroz com mel", "Feijão com chocolate"], "correta": 0},
        {"pergunta": "Qual combinação é popular nos EUA ao misturar sabor doce e salgado no café da manhã?", "alternativas": ["Sopa com cereal", "Bacon com maple syrup", "Macarrão com geleia"], "correta": 1},
        {"pergunta": "Qual mistura é comum para quem gosta de contraste entre quente e frio?", "alternativas": ["Arroz com gelo", "Feijão com sorvete", "Batata frita com sorvete"], "correta": 2},
        {"pergunta": "Qual fruta algumas pessoas comem com uma pitada de sal para realçar o sabor?", "alternativas": ["Melancia", "Uva-passa", "Coco seco"], "correta": 0},
        {"pergunta": "Qual combinação aparece em sobremesas e lanches misturando crocância e doçura?", "alternativas": ["Alface com chantilly", "Pipoca com chocolate", "Batata crua com açúcar"], "correta": 1},
    ],

    "Alimentos que Parecem uma Coisa e São Outra": [
        {"pergunta": "Botanicamente, o tomate é classificado como o quê?", "alternativas": ["Fruto", "Raiz", "Cereal"], "correta": 0},
        {"pergunta": "O amendoim pertence a qual família de alimentos?", "alternativas": ["Nozes verdadeiras", "Leguminosas", "Cereais"], "correta": 1},
        {"pergunta": "Na botânica, a banana é um tipo de quê?", "alternativas": ["Drupa", "Noz", "Baga"], "correta": 2},
        {"pergunta": "A parte carnosa do caju é considerada botanicamente o quê?", "alternativas": ["Pseudofruto", "Semente", "Raiz"], "correta": 0},
        {"pergunta": "Os pontinhos na parte externa do morango correspondem a pequenos frutos chamados de quê?", "alternativas": ["Esporos", "Aquênios", "Tubérculos"], "correta": 1},
    ],

    "Comidas que Nasceram em Outros Países": [
        {"pergunta": "O sushi está tradicionalmente associado a qual país?", "alternativas": ["Japão", "México", "Egito"], "correta": 0},
        {"pergunta": "Os tacos são um prato tradicional de qual país?", "alternativas": ["Itália", "México", "Índia"], "correta": 1},
        {"pergunta": "A paella está associada a qual país?", "alternativas": ["Portugal", "França", "Espanha"], "correta": 2},
        {"pergunta": "A pizza moderna é fortemente associada a qual país?", "alternativas": ["Itália", "Noruega", "Austrália"], "correta": 0},
        {"pergunta": "O pho, sopa de macarrão de arroz, é tradicional de qual país?", "alternativas": ["Coreia do Sul", "Vietnã", "Grécia"], "correta": 1},
    ],

    "Red Flags no Primeiro Encontro": [
        {"pergunta": "Qual atitude é uma red flag clara em um primeiro encontro?", "alternativas": ["Desrespeitar funcionários do local", "Perguntar sobre hobbies", "Chegar e pedir desculpas por um pequeno atraso"], "correta": 0},
        {"pergunta": "Qual comportamento merece atenção negativa?", "alternativas": ["Ouvir com interesse", "Ignorar limites e insistir", "Perguntar se a pessoa está confortável"], "correta": 1},
        {"pergunta": "Qual atitude pode indicar falta de respeito?", "alternativas": ["Dividir a conversa", "Aceitar opiniões diferentes", "Fazer comentários humilhantes"], "correta": 2},
        {"pergunta": "Qual comportamento pode ser uma red flag quando acontece repetidamente?", "alternativas": ["Interromper e falar apenas de si", "Fazer uma pergunta sobre o dia", "Agradecer pelo encontro"], "correta": 0},
        {"pergunta": "Qual atitude é preocupante quando a outra pessoa diz 'não'?", "alternativas": ["Mudar de assunto", "Continuar pressionando", "Respeitar a decisão"], "correta": 1},
    ],

    "Green Flags em Relacionamentos": [
        {"pergunta": "Qual atitude é uma green flag em um relacionamento?", "alternativas": ["Respeitar limites", "Controlar amizades", "Exigir senhas"], "correta": 0},
        {"pergunta": "Qual comportamento demonstra boa comunicação?", "alternativas": ["Sumir para punir", "Ouvir e conversar com respeito", "Gritar para vencer a discussão"], "correta": 1},
        {"pergunta": "Qual atitude mostra maturidade emocional?", "alternativas": ["Culpar sempre o outro", "Evitar qualquer conversa difícil", "Reconhecer erros e pedir desculpas"], "correta": 2},
        {"pergunta": "Qual comportamento fortalece a confiança?", "alternativas": ["Ser coerente entre fala e atitude", "Provocar ciúmes de propósito", "Esconder informações importantes"], "correta": 0},
        {"pergunta": "Qual atitude ajuda a manter a individualidade do casal?", "alternativas": ["Impedir hobbies separados", "Respeitar o espaço e os interesses de cada um", "Decidir tudo sozinho"], "correta": 1},
    ],

    "Linguagem Corporal no Flerte": [
        {"pergunta": "Qual comportamento pode indicar interesse durante uma conversa, embora não seja prova sozinho?", "alternativas": ["Contato visual frequente e sorriso", "Virar as costas o tempo todo", "Olhar apenas para o celular"], "correta": 0},
        {"pergunta": "Quando duas pessoas estão engajadas no papo, como o corpo costuma ficar?", "alternativas": ["Sempre distante", "Voltado uma para a outra", "Completamente imóvel"], "correta": 1},
        {"pergunta": "Qual gesto pode acontecer de forma inconsciente quando existe sintonia?", "alternativas": ["Fechar os olhos por vários minutos", "Cobrir os ouvidos", "Espelhar alguns gestos"], "correta": 2},
        {"pergunta": "Qual sinal corporal combina mais com conforto na conversa?", "alternativas": ["Postura relaxada", "Tensão constante", "Recuo sempre que o outro fala"], "correta": 0},
        {"pergunta": "O que é mais importante do que interpretar um único gesto?", "alternativas": ["Ignorar o que a pessoa diz", "Observar o conjunto e respeitar limites", "Assumir interesse automaticamente"], "correta": 1},
    ],

    "Cantadas: Boa ou Vergonha Alheia?": [
        {"pergunta": "Qual cantada é mais respeitosa para iniciar conversa?", "alternativas": ["Oi, gostei do seu estilo. Posso conversar com você?", "Você tem que me passar seu número", "Não aceito não como resposta"], "correta": 0},
        {"pergunta": "Qual abordagem tem mais chance de causar vergonha alheia por ser invasiva?", "alternativas": ["Fazer um elogio simples", "Insistir depois da pessoa demonstrar desinteresse", "Perguntar o nome"], "correta": 1},
        {"pergunta": "Qual frase mantém o flerte leve e dá espaço para a outra pessoa?", "alternativas": ["Você vai sair comigo e pronto", "Me responde agora", "Se você quiser, a gente continua esse papo depois"], "correta": 2},
        {"pergunta": "Qual atitude melhora qualquer cantada?", "alternativas": ["Respeitar a reação da pessoa", "Falar cada vez mais alto", "Bloquear a saída"], "correta": 0},
        {"pergunta": "Qual sinal indica que é melhor encerrar a tentativa de flerte?", "alternativas": ["A pessoa sorri e continua a conversa", "A pessoa demonstra desconforto e responde de forma curta", "A pessoa faz perguntas"], "correta": 1},
    ],

    "Mensagens que Parecem Flerte": [
        {"pergunta": "Qual mensagem tem mais cara de flerte?", "alternativas": ["Vi isso e lembrei de você 😏", "Favor enviar o relatório", "Ok"], "correta": 0},
        {"pergunta": "Qual mensagem demonstra vontade de prolongar o contato?", "alternativas": ["Tchau.", "Chegou bem? Me avisa 😊", "Recebido."], "correta": 1},
        {"pergunta": "Qual mensagem parece mais interessada em conhecer a pessoa?", "alternativas": ["Não quero saber", "Depois vejo", "Qual lugar você mais gosta de ir no fim de semana?"], "correta": 2},
        {"pergunta": "Qual mensagem combina com uma indireta leve?", "alternativas": ["Seu sorriso ficou na minha cabeça hoje", "A reunião mudou de horário", "Seu boleto venceu"], "correta": 0},
        {"pergunta": "Qual resposta costuma mostrar reciprocidade numa conversa de flerte?", "alternativas": ["Só visualiza por dias", "Responde e também faz perguntas", "Muda de assunto toda vez"], "correta": 1},
    ],

    "Casais Icônicos da Ficção": [
        {"pergunta": "Em 'Friends', com quem Chandler forma um casal?", "alternativas": ["Monica", "Rachel", "Phoebe"], "correta": 0},
        {"pergunta": "Em 'Shrek', quem é o grande amor do protagonista?", "alternativas": ["Rapunzel", "Fiona", "Cinderela"], "correta": 1},
        {"pergunta": "Em 'Titanic', quem vive o romance central com Jack?", "alternativas": ["Molly", "Ruth", "Rose"], "correta": 2},
        {"pergunta": "Em 'O Rei Leão', quem é a parceira de Simba?", "alternativas": ["Nala", "Sarabi", "Kiara"], "correta": 0},
        {"pergunta": "No universo do Homem-Aranha, qual personagem é um dos romances mais conhecidos de Peter Parker?", "alternativas": ["Lois Lane", "Mary Jane Watson", "Diana Prince"], "correta": 1},
    ],

    "Triângulos Amorosos de Filmes e Séries": [
        {"pergunta": "Em 'Crepúsculo', Bella fica dividida entre Edward e quem?", "alternativas": ["Jacob", "Carlisle", "Emmett"], "correta": 0},
        {"pergunta": "Em 'Jogos Vorazes', Katniss se envolve num triângulo com Peeta e quem?", "alternativas": ["Finnick", "Gale", "Haymitch"], "correta": 1},
        {"pergunta": "Em 'Bridget Jones', Bridget fica dividida entre Mark Darcy e quem?", "alternativas": ["Tom", "Jack", "Daniel Cleaver"], "correta": 2},
        {"pergunta": "Em 'The Vampire Diaries', Elena vive um triângulo famoso com Stefan e quem?", "alternativas": ["Damon", "Matt", "Klaus"], "correta": 0},
        {"pergunta": "Em 'Eu Nunca...', Devi se envolve em um triângulo com Paxton e quem?", "alternativas": ["Trent", "Ben", "Ethan"], "correta": 1},
    ],

    "Segredos de Bastidores de Shows": [
        {"pergunta": "Como é chamado o teste feito antes do show para ajustar microfones e instrumentos?", "alternativas": ["Passagem de som", "Intervalo", "Encore"], "correta": 0},
        {"pergunta": "Qual profissional ajuda a coordenar entradas, horários e mudanças no palco?", "alternativas": ["Fotógrafo", "Stage manager", "Bilheteiro"], "correta": 1},
        {"pergunta": "Como é chamada a lista com a ordem das músicas de um show?", "alternativas": ["Rider", "Mapa de luz", "Setlist"], "correta": 2},
        {"pergunta": "Qual documento pode reunir necessidades técnicas e de camarim de um artista?", "alternativas": ["Rider", "Ingresso", "Release de imprensa"], "correta": 0},
        {"pergunta": "Quem costuma ajudar na montagem e transporte de equipamentos de palco?", "alternativas": ["Maquiador exclusivamente", "Roadie", "Crítico de cinema"], "correta": 1},
    ],

    "Objetos que Só Quem Viveu os Anos 90 Conhece": [
        {"pergunta": "Qual objeto portátil recebia números e mensagens curtas antes dos celulares populares?", "alternativas": ["Pager", "Smartwatch", "Tablet"], "correta": 0},
        {"pergunta": "Qual mídia era usada para gravar músicas em aparelhos de som e walkmans?", "alternativas": ["Blu-ray", "Fita cassete", "Pen drive"], "correta": 1},
        {"pergunta": "Qual aparelho era usado para rebobinar e assistir fitas VHS?", "alternativas": ["Discman", "Rádio-relógio", "Videocassete"], "correta": 2},
        {"pergunta": "Qual mídia pequena e quadrada era comum em computadores?", "alternativas": ["Disquete", "Cartão microSD", "SSD externo"], "correta": 0},
        {"pergunta": "Qual aparelho portátil era usado para ouvir CDs?", "alternativas": ["Walkie-talkie", "Discman", "Fax"], "correta": 1},
    ],

    "Coisas que Existiam Antes da Internet": [
        {"pergunta": "Antes de pesquisar online, qual coleção de livros era usada para consultar informações gerais?", "alternativas": ["Enciclopédia", "Agenda telefônica", "Catálogo de roupas"], "correta": 0},
        {"pergunta": "Antes dos aplicativos de mapas, o que era comum usar em viagens?", "alternativas": ["Feed de notícias", "Mapa de papel", "QR Code"], "correta": 1},
        {"pergunta": "Antes dos sites de busca, onde muitas pessoas procuravam números de telefone?", "alternativas": ["Streaming", "GPS", "Lista telefônica"], "correta": 2},
        {"pergunta": "Qual aparelho permitia enviar cópias de documentos à distância pela linha telefônica?", "alternativas": ["Fax", "Toca-discos", "Projetor"], "correta": 0},
        {"pergunta": "Antes dos classificados online, onde era comum procurar anúncios de emprego e imóveis?", "alternativas": ["Aplicativo de mensagens", "Jornal impresso", "Videogame"], "correta": 1},
    ],
}

# ============================================================
# UTILITÁRIOS
# ============================================================

def slug(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    return texto or "video"


def executar(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        print(p.stderr[-5000:])
        raise RuntimeError("Comando retornou erro.")
    return p


def achar_fonte(*candidatos):
    for caminho in candidatos:
        if caminho and os.path.exists(caminho):
            return caminho
    return None


FONT_BOLD = achar_fonte(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
)

FONT_REG = achar_fonte(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
)


def fonte(tamanho, bold=True):
    caminho = FONT_BOLD if bold else FONT_REG
    if caminho:
        return ImageFont.truetype(caminho, int(tamanho))
    return ImageFont.load_default()


def wrap_text(draw, texto, fnt, max_width):
    palavras = str(texto).split()
    linhas = []
    atual = ""

    for palavra in palavras:
        teste = (atual + " " + palavra).strip()
        bb = draw.textbbox((0, 0), teste, font=fnt)
        if (bb[2] - bb[0]) <= max_width:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra

    if atual:
        linhas.append(atual)

    return linhas


def gradient_vertical(size, top_color, bottom_color):
    w, h = size
    faixa = Image.new("RGB", (1, h))
    dados = []
    for y in range(h):
        t = y / max(1, h - 1)
        dados.append(tuple(
            int(top_color[i] * (1 - t) + bottom_color[i] * t)
            for i in range(3)
        ))
    faixa.putdata(dados)
    return faixa.resize((w, h))


def texto_central(draw, xy, texto, fnt, fill):
    x, y = xy
    bb = draw.textbbox((0, 0), texto, font=fnt)
    tw = bb[2] - bb[0]
    draw.text((x - tw / 2, y), texto, font=fnt, fill=fill)


def desenhar_check(draw, cx, cy):
    draw.line(
        [(cx - 11, cy), (cx - 1, cy + 11), (cx + 18, cy - 18)],
        fill=(45, 125, 246),
        width=9
    )


def preparar_layout(perguntas):
    dummy = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(dummy)
    f_q = fonte(38, True)

    paper_x0 = 70
    paper_x1 = W - 70
    x_q = paper_x0 + 100
    max_q_width = paper_x1 - x_q - 130

    y = 370
    itens = []

    for i, q in enumerate(perguntas):
        linhas = wrap_text(draw, f"{i+1}) {q['pergunta']}", f_q, max_q_width)
        line_h = 52
        question_h = len(linhas) * line_h
        alt_top = y + question_h + 20
        alt_h = 46
        total_h = question_h + 20 + (3 * alt_h) + 50

        line_infos = []
        yy = y
        for linha in linhas:
            bb = draw.textbbox((0, 0), linha, font=f_q)
            largura = bb[2] - bb[0]
            line_infos.append({"texto": linha, "x": x_q, "y": yy, "w": largura, "h": 44})
            yy += line_h

        itens.append({
            "index": i,
            "y": y,
            "h": total_h,
            "lines": line_infos,
            "alt_top": alt_top
        })

        y += total_h + 14

    return itens


def calcular_scroll(layout, atual):
    if atual < 0:
        return 0
    return max(0, layout[atual]["y"] - 470)


def draw_marker(draw, x, y):
    body_w = 145
    body_h = 38
    draw.rounded_rectangle(
        [x, y, x + body_w, y + body_h],
        radius=12,
        fill=(255, 226, 61),
        outline=(229, 193, 17),
        width=3
    )
    draw.rounded_rectangle(
        [x + body_w - 35, y, x + body_w, y + body_h],
        radius=9,
        fill=(54, 54, 62)
    )
    draw.polygon(
        [(x - 18, y + 10), (x, y + 5), (x, y + body_h - 5), (x - 18, y + body_h - 10)],
        fill=(239, 221, 100)
    )
    draw.rectangle([x - 25, y + 13, x - 17, y + body_h - 13], fill=(102, 93, 34))


def desenhar_header_papel(draw, tema):
    draw.rectangle([82, 74, W - 88, 345], fill=(255, 254, 251))
    texto_central(draw, (W / 2, 92), "JuhQuiz", fonte(70, True), (255, 82, 148))
    texto_central(
        draw,
        (W / 2, 165),
        "QUIZ RÁPIDO • DESAFIE SEU CÉREBRO",
        fonte(23, True),
        (159, 122, 136)
    )

    tema_txt = f"TEMA: {tema.upper()}"
    bb = draw.textbbox((0, 0), tema_txt, font=fonte(28, True))
    tw = bb[2] - bb[0]
    px0 = W / 2 - tw / 2 - 30
    px1 = W / 2 + tw / 2 + 30

    draw.rounded_rectangle(
        [px0, 220, px1, 278],
        radius=29,
        fill=(255, 239, 247),
        outline=(255, 194, 219),
        width=3
    )
    texto_central(draw, (W / 2, 233), tema_txt, fonte(28, True), (208, 77, 132))


# ============================================================
# RENDER
# ============================================================

def render_frame(tema, perguntas, atual, estado, timer=None, highlight_progress=1.0, mostrar_marker=False):
    img = gradient_vertical((W, H), (255, 219, 233), (255, 196, 219))
    draw = ImageDraw.Draw(img)

    for x in range(0, W, 44):
        draw.line([(x, 0), (x + 90, H)], fill=(255, 255, 255), width=2)

    draw.ellipse([55, 95, 145, 185], fill=(255, 237, 245))
    draw.ellipse([W - 170, 80, W - 80, 170], fill=(255, 237, 245))
    draw.text((80, 110), "♥", font=fonte(56, True), fill=(226, 83, 143))
    draw.text((W - 155, 102), "✦", font=fonte(55, True), fill=(228, 137, 177))

    draw.rounded_rectangle(
        [W - 205, 130, W - 70, 265],
        radius=12,
        fill=(255, 242, 166),
        outline=(238, 215, 103),
        width=2
    )
    texto_central(draw, (W - 138, 168), "BOA", fonte(26, True), (150, 120, 30))
    texto_central(draw, (W - 138, 202), "SORTE!", fonte(26, True), (150, 120, 30))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([60, 60, W - 45, H - 55], radius=36, fill=(110, 55, 85, 65))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)

    paper = [45, 45, W - 65, H - 75]
    draw.rounded_rectangle(
        paper,
        radius=30,
        fill=(255, 254, 251),
        outline=(255, 190, 214),
        width=3
    )

    for yy in range(300, H - 100, 52):
        draw.line([(100, yy), (W - 105, yy)], fill=(255, 228, 238), width=2)

    draw.line([(120, 260), (120, H - 105)], fill=(255, 160, 198), width=3)
    draw.arc([70, 80, 190, 155], start=180, end=355, fill=(198, 143, 165), width=8)

    desenhar_header_papel(draw, tema)

    if estado == "final":
        texto_central(draw, (W / 2, 690), "QUANTAS VOCÊ ACERTOU?", fonte(58, True), (70, 61, 66))
        draw.rounded_rectangle(
            [190, 810, W - 190, 930],
            radius=35,
            fill=(255, 240, 247),
            outline=(255, 185, 213),
            width=4
        )
        texto_central(draw, (W / 2, 840), "COMENTA SUA PONTUAÇÃO", fonte(36, True), (210, 73, 131))
        texto_central(draw, (W / 2, 1010), "@juhquiz", fonte(36, True), (144, 104, 120))
        return img

    layout = preparar_layout(perguntas)
    scroll = calcular_scroll(layout, atual)

    f_q = fonte(38, True)
    f_alt = fonte(34, False)
    f_alt_bold = fonte(34, True)

    respondidos = atual if estado in ("reading", "highlight", "countdown") else atual + 1
    marker_pos = None

    # ------------------------------------------------------------
    # CORREÇÃO: tudo que pertence às perguntas é desenhado em uma
    # camada separada e depois recortado pelos limites internos da
    # folha. Assim, por exemplo, a pergunta 5 pode existir "abaixo",
    # mas só aparece quando sobe para dentro da área branca.
    # ------------------------------------------------------------
    camada_conteudo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(camada_conteudo)

    for item in layout:
        idx = item["index"]
        q = perguntas[idx]
        q_y = item["y"] - scroll

        # Mantém itens parcialmente visíveis para que apareçam à medida
        # que sobem, mas evita processar blocos totalmente fora da tela.
        if q_y + item["h"] < 300 or q_y > H:
            continue

        if idx == atual:
            cdraw.rounded_rectangle(
                [135, q_y - 8, W - 125, q_y + item["h"] - 12],
                radius=22,
                fill=(255, 247, 251)
            )

        total_path = sum(li["w"] for li in item["lines"])
        current_path = max(0.0, min(1.0, float(highlight_progress))) * total_path
        path_acc = 0.0

        for li in item["lines"]:
            lx = li["x"]
            ly = li["y"] - scroll
            lw = li["w"]

            full_mark = idx < respondidos
            if idx == atual and estado in ("countdown", "answer"):
                full_mark = True

            if idx == atual and estado == "highlight":
                faltando = current_path - path_acc
                parcial = max(0, min(lw, faltando))
                if parcial > 0:
                    cdraw.rounded_rectangle(
                        [lx - 5, ly + 6, lx + parcial + 7, ly + 47],
                        radius=10,
                        fill=(255, 238, 83)
                    )
                    if mostrar_marker and 0 < parcial < lw + 1:
                        marker_pos = (lx + parcial - 15, ly + 8)

            elif full_mark:
                cdraw.rounded_rectangle(
                    [lx - 5, ly + 6, lx + lw + 7, ly + 47],
                    radius=10,
                    fill=(255, 238, 83)
                )

            cdraw.text((lx, ly), li["texto"], font=f_q, fill=(48, 48, 48))
            path_acc += lw

        alt_y = item["alt_top"] - scroll
        letras = ["A", "B", "C"]

        for j, alt in enumerate(q["alternativas"]):
            yy = alt_y + j * 46
            cx = 185
            cy = yy + 18

            cdraw.ellipse(
                [cx - 13, cy - 13, cx + 13, cy + 13],
                outline=(130, 130, 130),
                width=3,
                fill=(255, 255, 255)
            )

            esta_revelada = idx < respondidos or (idx == atual and estado == "answer")
            if esta_revelada and j == int(q["correta"]):
                desenhar_check(cdraw, cx, cy)
                alt_font = f_alt_bold
                alt_fill = (35, 35, 35)
            else:
                alt_font = f_alt
                alt_fill = (55, 55, 55)

            cdraw.text((220, yy), f"{letras[j]}) {alt}", font=alt_font, fill=alt_fill)

        if idx == atual and estado == "countdown" and timer is not None:
            tx0, ty0, tx1, ty1 = W - 265, q_y + item["h"] - 75, W - 145, q_y + item["h"] - 20
            cdraw.rounded_rectangle(
                [tx0, ty0, tx1, ty1],
                radius=27,
                fill=(255, 250, 253),
                outline=(255, 139, 183),
                width=4
            )
            texto_central(
                cdraw,
                ((tx0 + tx1) / 2, ty0 + 7),
                str(timer),
                fonte(36, True),
                (209, 76, 132)
            )

    if marker_pos is not None:
        draw_marker(cdraw, marker_pos[0], marker_pos[1])

    # Recorte real da área útil da folha:
    # esquerda/direita ficam dentro do papel,
    # topo fica abaixo do cabeçalho,
    # fundo termina antes da borda inferior branca.
    mascara = Image.new("L", (W, H), 0)
    mdraw = ImageDraw.Draw(mascara)
    mdraw.rectangle(
        [70, 300, W - 90, H - 100],
        fill=255
    )

    transparente = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    camada_conteudo = Image.composite(camada_conteudo, transparente, mascara)
    img = Image.alpha_composite(img.convert("RGBA"), camada_conteudo).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Redesenha o cabeçalho por cima, como já acontecia antes.
    desenhar_header_papel(draw, tema)

    texto_central(
        draw,
        (W / 2, H - 120),
        "@juhquiz",
        fonte(25, True),
        (174, 123, 145)
    )

    return img


# ============================================================
# ÁUDIO / FFMPEG
# ============================================================

def limpar_tts(texto):
    return re.sub(r"\s+", " ", str(texto)).strip()


def tts_salvar(texto, caminho):
    caminho = str(caminho)
    if os.path.exists(caminho):
        os.remove(caminho)

    p = subprocess.run(
        [
            "edge-tts",
            "--voice", VOZ,
            "--rate", VELOCIDADE_VOZ,
            "--text", limpar_tts(texto),
            "--write-media", caminho
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if p.returncode != 0:
        print(p.stderr)
        raise RuntimeError("Falha ao gerar voz com Edge TTS.")

    if not os.path.exists(caminho) or os.path.getsize(caminho) < 500:
        raise RuntimeError(f"Áudio não foi criado: {caminho}")


def duracao_audio(caminho):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(caminho)
    ]
    return float(subprocess.check_output(cmd, text=True).strip())


def criar_beep(caminho, frequencia=950):
    caminho = str(caminho)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency={frequencia}:duration=0.14",
        "-af", "volume=0.55,apad=pad_dur=1",
        "-t", "1.0",
        "-c:a", "aac", "-b:a", "160k",
        "-ar", str(AUDIO_HZ),
        "-ac", str(AUDIO_CHANNELS),
        caminho
    ]
    executar(cmd)


def criar_clipe_imagem(img_path, duracao, saida, audio=None):
    img_path = str(img_path)
    saida = str(saida)
    duracao = float(duracao)

    if audio:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-i", str(audio),
            "-t", f"{duracao:.3f}",
            "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
            "-af", f"aresample={AUDIO_HZ}:async=1:first_pts=0,apad",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k",
            "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
            "-video_track_timescale", "90000",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            saida
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_HZ}",
            "-t", f"{duracao:.3f}",
            "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k",
            "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
            "-shortest",
            "-video_track_timescale", "90000",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            saida
        ]
    executar(cmd)


def criar_clipe_animacao(frames_dir, numero_frames, fps_frames, saida):
    frames_dir = Path(frames_dir)
    dur = numero_frames / float(fps_frames)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps_frames),
        "-i", str(frames_dir / "frame_%03d.png"),
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_HZ}",
        "-t", f"{dur:.3f}",
        "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
        "-shortest",
        "-video_track_timescale", "90000",
        "-movflags", "+faststart",
        str(saida)
    ]
    executar(cmd)


def juntar_clipes(lista, saida, concat_path):
    # IMPORTANTE:
    # O FFmpeg resolve caminhos relativos a partir da pasta onde está
    # o arquivo concat.txt. Como os segmentos já estão em subpastas de
    # _tmp_juhquiz_rosa, gravamos caminhos ABSOLUTOS para não duplicar
    # o prefixo da pasta.
    concat_path = Path(concat_path).resolve()
    saida = Path(saida).resolve()

    concat_path.parent.mkdir(parents=True, exist_ok=True)
    saida.parent.mkdir(parents=True, exist_ok=True)

    with open(concat_path, "w", encoding="utf-8") as f:
        for p in lista:
            p_abs = Path(p).resolve()
            if not p_abs.exists():
                raise FileNotFoundError(f"Segmento não encontrado: {p_abs}")

            caminho_ffmpeg = str(p_abs).replace("'", "'\\''")
            f.write("file '" + caminho_ffmpeg + "'\n")

    cmd = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_path),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-ar", str(AUDIO_HZ), "-ac", str(AUDIO_CHANNELS),
        "-af", f"aresample={AUDIO_HZ}:async=1:first_pts=0",
        "-avoid_negative_ts", "make_zero",
        "-movflags", "+faststart",
        str(saida)
    ]
    executar(cmd)


# ============================================================
# GERAÇÃO
# ============================================================

def validar():
    temas = list(QUIZZES.keys())

    if len(temas) < QUANTIDADE_VIDEOS:
        raise ValueError("Não há temas suficientes para 8 vídeos.")

    for tema in temas[:QUANTIDADE_VIDEOS]:
        perguntas = QUIZZES[tema]
        if len(perguntas) < PERGUNTAS_POR_VIDEO:
            raise ValueError(f"Tema '{tema}' tem menos de 5 perguntas.")

        for q in perguntas[:PERGUNTAS_POR_VIDEO]:
            if len(q["alternativas"]) != 3:
                raise ValueError(f"'{tema}' tem pergunta sem 3 alternativas.")
            if int(q["correta"]) not in (0, 1, 2):
                raise ValueError(f"'{tema}' tem índice de resposta inválido.")


def main():
    validar()

    if PASTA_TMP.exists():
        shutil.rmtree(PASTA_TMP)

    PASTA_TMP.mkdir(parents=True, exist_ok=True)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    print(f"📅 Pasta do dia: {PASTA_SAIDA}")
    print(f"🎬 Gerando {QUANTIDADE_VIDEOS} vídeos × {PERGUNTAS_POR_VIDEO} perguntas")

    beep_normal = PASTA_TMP / "beep_950.m4a"
    beep_final = PASTA_TMP / "beep_1250.m4a"

    criar_beep(beep_normal, 950)
    criar_beep(beep_final, 1250)

    videos_gerados = []
    temas = list(QUIZZES.keys())[:QUANTIDADE_VIDEOS]

    for video_num, tema in enumerate(temas, start=1):
        perguntas_tema = QUIZZES[tema][:PERGUNTAS_POR_VIDEO]

        print("\n" + "=" * 72)
        print(f"🎬 {video_num:02d}/08 — {tema}")
        print("=" * 72)

        pasta_video = PASTA_TMP / f"video_{video_num:02d}_{slug(tema)}"
        pasta_video.mkdir(parents=True, exist_ok=True)

        segmentos = []

        for idx, pergunta in enumerate(perguntas_tema):
            numero = idx + 1
            print(f" • {numero}/5 — {pergunta['pergunta']}")

            pasta_q = pasta_video / f"q{numero:02d}"
            pasta_q.mkdir(parents=True, exist_ok=True)

            # 1) lê apenas a pergunta
            audio_q = pasta_q / "pergunta.mp3"
            tts_salvar(pergunta["pergunta"], audio_q)
            dur_q = duracao_audio(audio_q) + 0.18

            frame_q = pasta_q / "01_pergunta.png"
            render_frame(
                tema, perguntas_tema,
                atual=idx,
                estado="reading",
                highlight_progress=0
            ).save(frame_q)

            clip_q = pasta_q / "01_pergunta.mp4"
            criar_clipe_imagem(frame_q, dur_q, clip_q, audio=audio_q)
            segmentos.append(clip_q)

            # 2) marca-texto percorre a pergunta toda
            frames_dir = pasta_q / "frames_marcatexto"
            frames_dir.mkdir(exist_ok=True)

            fps_marker = 20
            n_frames = max(8, int(DURACAO_MARCATEXTO * fps_marker))

            for fr in range(n_frames):
                progresso = (fr + 1) / n_frames
                frame = render_frame(
                    tema, perguntas_tema,
                    atual=idx,
                    estado="highlight",
                    highlight_progress=progresso,
                    mostrar_marker=True
                )
                frame.save(frames_dir / f"frame_{fr:03d}.png")

            clip_marker = pasta_q / "02_marcatexto.mp4"
            criar_clipe_animacao(frames_dir, n_frames, fps_marker, clip_marker)
            segmentos.append(clip_marker)

            # 3) contagem com bip
            for segundos in range(TEMPO_ESCOLHA, 0, -1):
                frame_timer = pasta_q / f"timer_{segundos}.png"
                render_frame(
                    tema, perguntas_tema,
                    atual=idx,
                    estado="countdown",
                    timer=segundos,
                    highlight_progress=1
                ).save(frame_timer)

                clip_timer = pasta_q / f"timer_{segundos}.mp4"
                som = beep_final if segundos == 1 else beep_normal
                criar_clipe_imagem(frame_timer, 1.0, clip_timer, audio=som)
                segmentos.append(clip_timer)

            # 4) fala só a resposta e marca correta
            correta = int(pergunta["correta"])
            texto_resposta = pergunta["alternativas"][correta]

            audio_resp = pasta_q / "resposta.mp3"
            tts_salvar(texto_resposta, audio_resp)
            dur_resp = duracao_audio(audio_resp) + PAUSA_DEPOIS_RESPOSTA

            frame_resp = pasta_q / "03_resposta.png"
            render_frame(
                tema, perguntas_tema,
                atual=idx,
                estado="answer",
                highlight_progress=1
            ).save(frame_resp)

            clip_resp = pasta_q / "03_resposta.mp4"
            criar_clipe_imagem(frame_resp, dur_resp, clip_resp, audio=audio_resp)
            segmentos.append(clip_resp)

        # tela final
        frame_final = pasta_video / "final.png"
        render_frame(
            tema, perguntas_tema,
            atual=len(perguntas_tema) - 1,
            estado="final"
        ).save(frame_final)

        clip_final = pasta_video / "final.mp4"
        criar_clipe_imagem(frame_final, 2.0, clip_final)
        segmentos.append(clip_final)

        nome_saida = f"{video_num:02d}_{slug(tema)}_{DATA_DO_DIA}.mp4"
        saida_video = PASTA_SAIDA / nome_saida

        juntar_clipes(segmentos, saida_video, pasta_video / "concat.txt")
        videos_gerados.append(saida_video)

        print("✅ Gerado:", saida_video)

    print("\n✅ FINALIZADO")
    print(f"📁 {PASTA_SAIDA}")
    for p in videos_gerados:
        print(" -", p)


if __name__ == "__main__":
    main()
