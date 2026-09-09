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
QUIZZES_NOVOS = {

    "Animais Domésticos": [
        {"pergunta": "Qual animal doméstico é conhecido por latir?", "alternativas": ["Gato", "Cachorro", "Coelho"], "correta": 1},
        {"pergunta": "Qual animal costuma ronronar quando está confortável?", "alternativas": ["Gato", "Galinha", "Cavalo"], "correta": 0},
        {"pergunta": "Qual destes animais possui longas orelhas e gosta de roer vegetais?", "alternativas": ["Hamster", "Papagaio", "Coelho"], "correta": 2},
        {"pergunta": "Qual ave doméstica pode aprender a imitar palavras humanas?", "alternativas": ["Pato", "Papagaio", "Codorna"], "correta": 1},
        {"pergunta": "Qual pequeno animal doméstico costuma correr em uma rodinha?", "alternativas": ["Hamster", "Cachorro", "Peixe"], "correta": 0},
    ],

    "Animais Selvagens": [
        {"pergunta": "Qual animal é conhecido como rei dos animais?", "alternativas": ["Elefante", "Leão", "Girafa"], "correta": 1},
        {"pergunta": "Qual destes animais possui uma tromba?", "alternativas": ["Elefante", "Zebra", "Tigre"], "correta": 0},
        {"pergunta": "Qual animal possui o pescoço muito comprido?", "alternativas": ["Hipopótamo", "Leopardo", "Girafa"], "correta": 2},
        {"pergunta": "Qual animal selvagem possui listras pretas e brancas?", "alternativas": ["Onça", "Zebra", "Gorila"], "correta": 1},
        {"pergunta": "Qual destes grandes felinos possui listras pretas sobre o pelo alaranjado?", "alternativas": ["Tigre", "Leão", "Guepardo"], "correta": 0},
    ],

    "Animais Marinhos": [
        {"pergunta": "Qual é o maior animal conhecido atualmente?", "alternativas": ["Tubarão-branco", "Baleia-azul", "Orca"], "correta": 1},
        {"pergunta": "Qual animal marinho possui oito braços?", "alternativas": ["Polvo", "Golfinho", "Tubarão"], "correta": 0},
        {"pergunta": "Qual animal possui uma carapaça e pode viver no mar?", "alternativas": ["Baleia", "Lula", "Tartaruga-marinha"], "correta": 2},
        {"pergunta": "Qual destes animais é um mamífero marinho conhecido por sua inteligência?", "alternativas": ["Sardinha", "Golfinho", "Polvo"], "correta": 1},
        {"pergunta": "Qual animal marinho possui corpo semelhante a uma estrela?", "alternativas": ["Estrela-do-mar", "Água-viva", "Cavalo-marinho"], "correta": 0},
    ],

    "Animais da Amazônia": [
        {"pergunta": "Qual grande felino vive na Floresta Amazônica?", "alternativas": ["Leão", "Onça-pintada", "Tigre"], "correta": 1},
        {"pergunta": "Qual peixe amazônico é conhecido por seu grande tamanho?", "alternativas": ["Pirarucu", "Salmão", "Bacalhau"], "correta": 0},
        {"pergunta": "Qual animal amazônico é conhecido por se movimentar lentamente nas árvores?", "alternativas": ["Anta", "Capivara", "Bicho-preguiça"], "correta": 2},
        {"pergunta": "Qual destes animais é um grande roedor encontrado na Amazônia?", "alternativas": ["Tamanduá", "Capivara", "Tucano"], "correta": 1},
        {"pergunta": "Qual ave amazônica possui um grande bico colorido?", "alternativas": ["Tucano", "Pinguim", "Avestruz"], "correta": 0},
    ],

    "Animais do Pantanal": [
        {"pergunta": "Qual grande felino é um dos símbolos da fauna do Pantanal?", "alternativas": ["Tigre", "Onça-pintada", "Leão"], "correta": 1},
        {"pergunta": "Qual grande roedor é facilmente encontrado no Pantanal?", "alternativas": ["Capivara", "Esquilo", "Hamster"], "correta": 0},
        {"pergunta": "Qual réptil é muito comum nos rios e áreas alagadas do Pantanal?", "alternativas": ["Camaleão", "Iguana", "Jacaré"], "correta": 2},
        {"pergunta": "Qual ave azul de grande porte é encontrada no Pantanal?", "alternativas": ["Canário", "Arara-azul", "Pardal"], "correta": 1},
        {"pergunta": "Qual animal possui focinho comprido e se alimenta principalmente de formigas?", "alternativas": ["Tamanduá", "Macaco", "Veado"], "correta": 0},
    ],

    "Animais Venenosos": [
        {"pergunta": "Qual destes animais pode inocular veneno através de sua picada?", "alternativas": ["Coelho", "Escorpião", "Pombo"], "correta": 1},
        {"pergunta": "Qual destes répteis possui espécies peçonhentas?", "alternativas": ["Serpente", "Tartaruga", "Jabuti"], "correta": 0},
        {"pergunta": "Qual pequeno animal possui oito patas e algumas espécies podem ser peçonhentas?", "alternativas": ["Formiga", "Besouro", "Aranha"], "correta": 2},
        {"pergunta": "Qual serpente brasileira possui um chocalho na ponta da cauda?", "alternativas": ["Jiboia", "Cascavel", "Sucuri"], "correta": 1},
        {"pergunta": "Qual animal marinho possui tentáculos capazes de liberar substâncias tóxicas?", "alternativas": ["Água-viva", "Golfinho", "Sardinha"], "correta": 0},
    ],

    "Animais que Voam": [
        {"pergunta": "Qual destes mamíferos consegue voar de forma ativa?", "alternativas": ["Esquilo", "Morcego", "Macaco"], "correta": 1},
        {"pergunta": "Qual ave é conhecida por conseguir voar para trás?", "alternativas": ["Beija-flor", "Galinha", "Pinguim"], "correta": 0},
        {"pergunta": "Qual inseto passa pela fase de lagarta antes de voar?", "alternativas": ["Formiga", "Barata", "Borboleta"], "correta": 2},
        {"pergunta": "Qual ave de rapina possui excelente visão?", "alternativas": ["Pato", "Águia", "Galinha"], "correta": 1},
        {"pergunta": "Qual inseto produz mel e consegue voar?", "alternativas": ["Abelha", "Grilo", "Pulga"], "correta": 0},
    ],

    "Animais que Vivem na Água": [
        {"pergunta": "Qual destes animais respira por brânquias durante toda a vida?", "alternativas": ["Golfinho", "Peixe", "Baleia"], "correta": 1},
        {"pergunta": "Qual animal vive na água, mas precisa subir à superfície para respirar?", "alternativas": ["Golfinho", "Sardinha", "Tilápia"], "correta": 0},
        {"pergunta": "Qual destes animais possui pinças?", "alternativas": ["Tubarão", "Enguia", "Caranguejo"], "correta": 2},
        {"pergunta": "Qual animal possui corpo alongado e formato semelhante ao de uma serpente?", "alternativas": ["Estrela-do-mar", "Enguia", "Ostra"], "correta": 1},
        {"pergunta": "Qual animal aquático possui concha e produz pérolas em algumas espécies?", "alternativas": ["Ostra", "Polvo", "Golfinho"], "correta": 0},
    ],

    "Recordes do Mundo Animal": [
        {"pergunta": "Qual é o animal terrestre mais alto?", "alternativas": ["Elefante", "Girafa", "Camelo"], "correta": 1},
        {"pergunta": "Qual é o maior animal terrestre atualmente?", "alternativas": ["Elefante-africano", "Rinoceronte", "Hipopótamo"], "correta": 0},
        {"pergunta": "Qual ave é conhecida por atingir altíssimas velocidades em mergulho?", "alternativas": ["Pinguim", "Avestruz", "Falcão-peregrino"], "correta": 2},
        {"pergunta": "Qual é o maior animal existente atualmente?", "alternativas": ["Elefante", "Baleia-azul", "Tubarão-branco"], "correta": 1},
        {"pergunta": "Qual é a maior ave viva em altura e peso?", "alternativas": ["Avestruz", "Águia", "Flamingo"], "correta": 0},
    ],

    "Curiosidades sobre Cachorros": [
        {"pergunta": "Qual sentido dos cachorros é especialmente desenvolvido?", "alternativas": ["Paladar", "Olfato", "Visão de cores"], "correta": 1},
        {"pergunta": "Como são chamados os filhotes de cachorro?", "alternativas": ["Cães filhotes", "Potros", "Bezerros"], "correta": 0},
        {"pergunta": "Qual parte do corpo do cachorro ajuda na comunicação por movimentos?", "alternativas": ["Unhas", "Dentes", "Cauda"], "correta": 2},
        {"pergunta": "Qual destes alimentos não deve ser oferecido aos cães por poder ser tóxico?", "alternativas": ["Cenoura", "Chocolate", "Arroz"], "correta": 1},
        {"pergunta": "Qual som é mais associado à comunicação de um cachorro?", "alternativas": ["Latido", "Miado", "Cacarejo"], "correta": 0},
    ],

    "Curiosidades sobre Gatos": [
        {"pergunta": "Qual som o gato costuma produzir quando está satisfeito?", "alternativas": ["Latido", "Ronronar", "Cacarejo"], "correta": 1},
        {"pergunta": "Qual estrutura ajuda o gato a perceber objetos próximos e movimentos de ar?", "alternativas": ["Bigodes", "Cauda", "Garras"], "correta": 0},
        {"pergunta": "Qual habilidade é muito desenvolvida nos gatos?", "alternativas": ["Respirar debaixo d'água", "Voar", "Equilíbrio"], "correta": 2},
        {"pergunta": "Qual comportamento é comum aos gatos durante várias horas do dia?", "alternativas": ["Nadar", "Dormir", "Voar"], "correta": 1},
        {"pergunta": "Qual som é normalmente usado pelo gato para se comunicar com humanos?", "alternativas": ["Miado", "Latido", "Assobio"], "correta": 0},
    ],

    "Corpo Humano": [
        {"pergunta": "Qual órgão bombeia o sangue pelo corpo?", "alternativas": ["Pulmão", "Coração", "Estômago"], "correta": 1},
        {"pergunta": "Qual é o maior órgão do corpo humano?", "alternativas": ["Pele", "Fígado", "Coração"], "correta": 0},
        {"pergunta": "Quantos pulmões normalmente possui uma pessoa?", "alternativas": ["1", "3", "2"], "correta": 2},
        {"pergunta": "Qual órgão está principalmente relacionado ao pensamento e à memória?", "alternativas": ["Rim", "Cérebro", "Estômago"], "correta": 1},
        {"pergunta": "Qual estrutura sustenta grande parte do corpo humano?", "alternativas": ["Esqueleto", "Cabelo", "Unhas"], "correta": 0},
    ],

    "Cérebro e Sistema Nervoso": [
        {"pergunta": "Qual célula é a principal unidade funcional do sistema nervoso?", "alternativas": ["Hemácia", "Neurônio", "Plaqueta"], "correta": 1},
        {"pergunta": "Qual órgão é o principal centro de controle do sistema nervoso?", "alternativas": ["Cérebro", "Fígado", "Pulmão"], "correta": 0},
        {"pergunta": "Qual estrutura liga o cérebro a grande parte dos nervos do corpo?", "alternativas": ["Fêmur", "Traqueia", "Medula espinhal"], "correta": 2},
        {"pergunta": "Qual parte do cérebro está especialmente relacionada ao equilíbrio e coordenação?", "alternativas": ["Hipófise", "Cerebelo", "Tireoide"], "correta": 1},
        {"pergunta": "Como são chamadas as estruturas que transmitem sinais entre o sistema nervoso e o corpo?", "alternativas": ["Nervos", "Veias", "Tendões"], "correta": 0},
    ],

    "Coração e Circulação": [
        {"pergunta": "Qual órgão impulsiona o sangue através dos vasos sanguíneos?", "alternativas": ["Pulmão", "Coração", "Fígado"], "correta": 1},
        {"pergunta": "Qual tipo de vaso geralmente leva sangue para fora do coração?", "alternativas": ["Artéria", "Veia", "Capilar"], "correta": 0},
        {"pergunta": "Qual componente do sangue transporta grande parte do oxigênio?", "alternativas": ["Plaquetas", "Plasma", "Hemácias"], "correta": 2},
        {"pergunta": "Quantas cavidades possui o coração humano?", "alternativas": ["Duas", "Quatro", "Seis"], "correta": 1},
        {"pergunta": "Como é chamado o movimento rítmico percebido nas artérias?", "alternativas": ["Pulso", "Reflexo", "Digestão"], "correta": 0},
    ],

    "Ossos do Corpo Humano": [
        {"pergunta": "Qual é o osso mais longo do corpo humano?", "alternativas": ["Úmero", "Fêmur", "Rádio"], "correta": 1},
        {"pergunta": "Qual estrutura óssea protege o cérebro?", "alternativas": ["Crânio", "Pelve", "Fêmur"], "correta": 0},
        {"pergunta": "Qual conjunto de ossos protege principalmente o coração e os pulmões?", "alternativas": ["Pelve", "Crânio", "Caixa torácica"], "correta": 2},
        {"pergunta": "Qual osso fica na região anterior da coxa?", "alternativas": ["Ulna", "Fêmur", "Clavícula"], "correta": 1},
        {"pergunta": "Qual estrutura é formada por várias vértebras?", "alternativas": ["Coluna vertebral", "Crânio", "Mandíbula"], "correta": 0},
    ],

    "Órgãos do Corpo Humano": [
        {"pergunta": "Qual órgão filtra o sangue e produz urina?", "alternativas": ["Pulmão", "Rim", "Estômago"], "correta": 1},
        {"pergunta": "Qual órgão participa principalmente da digestão dos alimentos após o esôfago?", "alternativas": ["Estômago", "Cérebro", "Bexiga"], "correta": 0},
        {"pergunta": "Qual órgão é responsável principalmente pelas trocas de oxigênio e gás carbônico?", "alternativas": ["Fígado", "Baço", "Pulmões"], "correta": 2},
        {"pergunta": "Qual órgão produz a bile?", "alternativas": ["Rim", "Fígado", "Coração"], "correta": 1},
        {"pergunta": "Qual órgão armazena a urina antes de sua eliminação?", "alternativas": ["Bexiga", "Pâncreas", "Estômago"], "correta": 0},
    ],

    "Sentidos do Corpo Humano": [
        {"pergunta": "Qual órgão está relacionado principalmente à visão?", "alternativas": ["Ouvido", "Olho", "Nariz"], "correta": 1},
        {"pergunta": "Qual sentido permite perceber cheiros?", "alternativas": ["Olfato", "Tato", "Visão"], "correta": 0},
        {"pergunta": "Qual órgão é responsável principalmente pela audição?", "alternativas": ["Língua", "Pele", "Ouvido"], "correta": 2},
        {"pergunta": "Qual sentido está relacionado à percepção de sabores?", "alternativas": ["Olfato", "Paladar", "Audição"], "correta": 1},
        {"pergunta": "Qual órgão participa principalmente da percepção do tato?", "alternativas": ["Pele", "Fígado", "Pulmão"], "correta": 0},
    ],

    "Curiosidades do Corpo Humano": [
        {"pergunta": "Qual parte do corpo possui impressões digitais únicas em cada pessoa?", "alternativas": ["Cotovelos", "Dedos", "Cabelos"], "correta": 1},
        {"pergunta": "Qual tecido do corpo humano cresce continuamente e precisa ser cortado regularmente?", "alternativas": ["Unhas", "Ossos", "Dentes"], "correta": 0},
        {"pergunta": "Qual órgão possui ácido que ajuda na digestão dos alimentos?", "alternativas": ["Coração", "Pulmão", "Estômago"], "correta": 2},
        {"pergunta": "Qual substância dá a cor vermelha às hemácias?", "alternativas": ["Melanina", "Hemoglobina", "Queratina"], "correta": 1},
        {"pergunta": "Qual músculo separa principalmente o tórax do abdômen e ajuda na respiração?", "alternativas": ["Diafragma", "Bíceps", "Trapézio"], "correta": 0},
    ],

    "Planetas do Sistema Solar": [
        {"pergunta": "Qual planeta é o mais próximo do Sol?", "alternativas": ["Vênus", "Mercúrio", "Marte"], "correta": 1},
        {"pergunta": "Qual é o maior planeta do Sistema Solar?", "alternativas": ["Júpiter", "Saturno", "Terra"], "correta": 0},
        {"pergunta": "Qual planeta é conhecido como planeta vermelho?", "alternativas": ["Urano", "Vênus", "Marte"], "correta": 2},
        {"pergunta": "Qual planeta é famoso por seus grandes anéis visíveis?", "alternativas": ["Mercúrio", "Saturno", "Marte"], "correta": 1},
        {"pergunta": "Em qual planeta vivemos?", "alternativas": ["Terra", "Netuno", "Júpiter"], "correta": 0},
    ],

    "Espaço e Universo": [
        {"pergunta": "Qual estrela está no centro do Sistema Solar?", "alternativas": ["Sirius", "Sol", "Polaris"], "correta": 1},
        {"pergunta": "Como é chamada a galáxia onde está o Sistema Solar?", "alternativas": ["Via Láctea", "Andrômeda", "Sombrero"], "correta": 0},
        {"pergunta": "Qual objeto possui gravidade tão intensa que nem a luz consegue escapar após cruzar seu horizonte de eventos?", "alternativas": ["Cometa", "Asteroide", "Buraco negro"], "correta": 2},
        {"pergunta": "Como é chamado um corpo de gelo e poeira que pode formar uma cauda ao se aproximar do Sol?", "alternativas": ["Planeta", "Cometa", "Satélite"], "correta": 1},
        {"pergunta": "Qual unidade é frequentemente usada para expressar enormes distâncias entre estrelas?", "alternativas": ["Ano-luz", "Centímetro", "Mililitro"], "correta": 0},
    ],

    "Lua e suas Curiosidades": [
        {"pergunta": "A Lua é um satélite natural de qual planeta?", "alternativas": ["Marte", "Terra", "Vênus"], "correta": 1},
        {"pergunta": "Como é chamada a fase em que vemos praticamente toda a face iluminada da Lua?", "alternativas": ["Lua cheia", "Lua nova", "Lua minguante"], "correta": 0},
        {"pergunta": "Quem foi o primeiro ser humano a caminhar na Lua?", "alternativas": ["Yuri Gagarin", "Buzz Aldrin", "Neil Armstrong"], "correta": 2},
        {"pergunta": "Em qual ano ocorreu o primeiro pouso tripulado na Lua?", "alternativas": ["1959", "1969", "1979"], "correta": 1},
        {"pergunta": "Qual fenômeno acontece quando a Terra fica entre o Sol e a Lua, projetando sua sombra sobre ela?", "alternativas": ["Eclipse lunar", "Aurora", "Solstício"], "correta": 0},
    ],

    "Estrelas e Constelações": [
        {"pergunta": "Qual estrela é a mais próxima da Terra?", "alternativas": ["Sirius", "Sol", "Betelgeuse"], "correta": 1},
        {"pergunta": "Como é chamado um grupo aparente de estrelas que forma desenhos no céu?", "alternativas": ["Constelação", "Cometa", "Asteroide"], "correta": 0},
        {"pergunta": "Qual constelação possui as estrelas popularmente conhecidas no Brasil como Três Marias?", "alternativas": ["Cruzeiro do Sul", "Escorpião", "Órion"], "correta": 2},
        {"pergunta": "Qual constelação é muito conhecida e aparece na bandeira do Brasil?", "alternativas": ["Ursa Maior", "Cruzeiro do Sul", "Pégaso"], "correta": 1},
        {"pergunta": "Qual processo produz grande parte da energia das estrelas?", "alternativas": ["Fusão nuclear", "Combustão de madeira", "Evaporação"], "correta": 0},
    ],

    "Astronautas e Exploração Espacial": [
        {"pergunta": "Quem foi o primeiro ser humano a viajar ao espaço?", "alternativas": ["Neil Armstrong", "Yuri Gagarin", "John Glenn"], "correta": 1},
        {"pergunta": "Quem foi o primeiro brasileiro a viajar ao espaço?", "alternativas": ["Marcos Pontes", "Santos Dumont", "Ayrton Senna"], "correta": 0},
        {"pergunta": "Qual veículo é utilizado para colocar satélites e espaçonaves no espaço?", "alternativas": ["Submarino", "Helicóptero", "Foguete"], "correta": 2},
        {"pergunta": "Como é chamada a roupa especial utilizada por astronautas fora da nave?", "alternativas": ["Armadura", "Traje espacial", "Macacão de mergulho"], "correta": 1},
        {"pergunta": "Qual laboratório habitado orbita a Terra há décadas?", "alternativas": ["Estação Espacial Internacional", "Hubble", "Voyager 1"], "correta": 0},
    ],

    "Dinossauros": [
        {"pergunta": "Qual dinossauro é famoso por seus braços pequenos e grandes dentes?", "alternativas": ["Tricerátops", "Tyrannosaurus rex", "Diplodoco"], "correta": 1},
        {"pergunta": "Qual dinossauro possuía três chifres no crânio?", "alternativas": ["Tricerátops", "Velociraptor", "Estegossauro"], "correta": 0},
        {"pergunta": "Qual dinossauro possuía grandes placas ao longo das costas?", "alternativas": ["T. rex", "Anquilossauro", "Estegossauro"], "correta": 2},
        {"pergunta": "Qual destes dinossauros tinha pescoço muito comprido?", "alternativas": ["Tricerátops", "Brachiosaurus", "Velociraptor"], "correta": 1},
        {"pergunta": "Qual ciência estuda fósseis e seres que viveram no passado?", "alternativas": ["Paleontologia", "Meteorologia", "Astronomia"], "correta": 0},
    ],

    "Animais Pré-Históricos": [
        {"pergunta": "Qual animal pré-histórico parecia um elefante coberto de pelos?", "alternativas": ["Tigre-dentes-de-sabre", "Mamute", "Dodô"], "correta": 1},
        {"pergunta": "Qual felino pré-histórico ficou famoso por seus enormes dentes caninos?", "alternativas": ["Tigre-dentes-de-sabre", "Leão-marinho", "Guepardo"], "correta": 0},
        {"pergunta": "Qual enorme réptil marinho pré-histórico pertenceu ao grupo dos mosassauros?", "alternativas": ["Mamute", "Megatério", "Mosasaurus"], "correta": 2},
        {"pergunta": "Qual tubarão extinto ficou famoso por seu enorme tamanho?", "alternativas": ["Tubarão-martelo", "Megalodon", "Tubarão-lixa"], "correta": 1},
        {"pergunta": "Qual animal extinto era uma gigantesca preguiça terrestre?", "alternativas": ["Megatério", "Mamute", "Megalodon"], "correta": 0},
    ],

    "Vulcões": [
        {"pergunta": "Como é chamada a rocha derretida enquanto ainda está abaixo da superfície terrestre?", "alternativas": ["Lava", "Magma", "Cinza"], "correta": 1},
        {"pergunta": "Como é chamada a rocha derretida quando chega à superfície?", "alternativas": ["Lava", "Magma", "Granito"], "correta": 0},
        {"pergunta": "Qual famoso vulcão destruiu Pompeia no ano 79?", "alternativas": ["Etna", "Krakatoa", "Vesúvio"], "correta": 2},
        {"pergunta": "Como é chamado um vulcão que está em atividade ou apresenta sinais de atividade?", "alternativas": ["Extinto", "Ativo", "Congelado"], "correta": 1},
        {"pergunta": "Qual país é conhecido por possuir muitos vulcões devido à sua posição no Círculo de Fogo do Pacífico?", "alternativas": ["Japão", "Uruguai", "Paraguai"], "correta": 0},
    ],

    "Terremotos e Tsunamis": [
        {"pergunta": "Qual aparelho registra ondas sísmicas?", "alternativas": ["Termômetro", "Sismógrafo", "Barômetro"], "correta": 1},
        {"pergunta": "Como é chamado o ponto no interior da Terra onde se inicia um terremoto?", "alternativas": ["Hipocentro", "Equador", "Meridiano"], "correta": 0},
        {"pergunta": "Qual fenômeno pode gerar grandes ondas oceânicas após um forte terremoto submarino?", "alternativas": ["Tornado", "Nevasca", "Tsunami"], "correta": 2},
        {"pergunta": "A movimentação de quais estruturas está relacionada a muitos terremotos?", "alternativas": ["Nuvens", "Placas tectônicas", "Rios"], "correta": 1},
        {"pergunta": "Como é chamado o ponto da superfície diretamente acima do foco de um terremoto?", "alternativas": ["Epicentro", "Horizonte", "Polo"], "correta": 0},
    ],

    "Clima e Tempo": [
        {"pergunta": "Qual instrumento mede a temperatura?", "alternativas": ["Barômetro", "Termômetro", "Anemômetro"], "correta": 1},
        {"pergunta": "Qual instrumento mede a velocidade do vento?", "alternativas": ["Anemômetro", "Régua", "Bússola"], "correta": 0},
        {"pergunta": "Qual fenômeno é formado por gotas de água que caem das nuvens?", "alternativas": ["Vento", "Nevoeiro", "Chuva"], "correta": 2},
        {"pergunta": "Como é chamada uma grande descarga elétrica atmosférica?", "alternativas": ["Granizo", "Raio", "Orvalho"], "correta": 1},
        {"pergunta": "Qual instrumento mede a pressão atmosférica?", "alternativas": ["Barômetro", "Termômetro", "Higrômetro"], "correta": 0},
    ],

    "Florestas do Mundo": [
        {"pergunta": "Qual é a maior floresta tropical do mundo?", "alternativas": ["Floresta Negra", "Floresta Amazônica", "Taiga Siberiana"], "correta": 1},
        {"pergunta": "Em qual continente está a maior parte da Floresta Amazônica?", "alternativas": ["América do Sul", "África", "Europa"], "correta": 0},
        {"pergunta": "Qual floresta tropical africana está associada à bacia de um dos maiores rios do continente?", "alternativas": ["Floresta Negra", "Taiga", "Floresta do Congo"], "correta": 2},
        {"pergunta": "Qual tipo de floresta é comum nas regiões frias do Canadá e da Rússia?", "alternativas": ["Manguezal", "Taiga", "Savana"], "correta": 1},
        {"pergunta": "Qual bioma brasileiro originalmente cobria grande parte do litoral do país?", "alternativas": ["Mata Atlântica", "Pampa", "Pantanal"], "correta": 0},
    ],

    "Desertos do Mundo": [
        {"pergunta": "Qual grande deserto quente fica no norte da África?", "alternativas": ["Atacama", "Saara", "Gobi"], "correta": 1},
        {"pergunta": "Qual deserto extremamente seco está localizado principalmente no Chile?", "alternativas": ["Atacama", "Saara", "Kalahari"], "correta": 0},
        {"pergunta": "Qual deserto está localizado entre partes da China e da Mongólia?", "alternativas": ["Saara", "Atacama", "Gobi"], "correta": 2},
        {"pergunta": "Qual animal é famoso por suas adaptações para viver em desertos?", "alternativas": ["Pinguim", "Camelo", "Golfinho"], "correta": 1},
        {"pergunta": "Qual planta é conhecida por armazenar água e sobreviver em regiões áridas?", "alternativas": ["Cacto", "Vitória-régia", "Samambaia"], "correta": 0},
    ],

    "Rios Famosos": [
        {"pergunta": "Qual rio possui a maior vazão de água do mundo?", "alternativas": ["Nilo", "Amazonas", "Tâmisa"], "correta": 1},
        {"pergunta": "Qual famoso rio atravessa o Egito?", "alternativas": ["Nilo", "Amazonas", "Danúbio"], "correta": 0},
        {"pergunta": "Qual rio atravessa cidades europeias como Viena, Bratislava e Budapeste?", "alternativas": ["Sena", "Tâmisa", "Danúbio"], "correta": 2},
        {"pergunta": "Qual rio atravessa a cidade de Londres?", "alternativas": ["Sena", "Tâmisa", "Tejo"], "correta": 1},
        {"pergunta": "Qual rio atravessa Paris?", "alternativas": ["Sena", "Reno", "Nilo"], "correta": 0},
    ],

    "Montanhas Famosas": [
        {"pergunta": "Qual é a montanha mais alta do mundo acima do nível do mar?", "alternativas": ["K2", "Everest", "Aconcágua"], "correta": 1},
        {"pergunta": "Qual é a montanha mais alta da América do Sul?", "alternativas": ["Aconcágua", "Everest", "Kilimanjaro"], "correta": 0},
        {"pergunta": "Qual montanha está localizada na Tanzânia?", "alternativas": ["Fuji", "Everest", "Kilimanjaro"], "correta": 2},
        {"pergunta": "Qual monte japonês possui formato vulcânico muito conhecido?", "alternativas": ["K2", "Monte Fuji", "Aconcágua"], "correta": 1},
        {"pergunta": "Em qual cadeia de montanhas fica o Monte Everest?", "alternativas": ["Himalaia", "Andes", "Alpes"], "correta": 0},
    ],

    "Países e Capitais": [
        {"pergunta": "Qual é a capital do Brasil?", "alternativas": ["Rio de Janeiro", "Brasília", "São Paulo"], "correta": 1},
        {"pergunta": "Qual é a capital da França?", "alternativas": ["Paris", "Lyon", "Marselha"], "correta": 0},
        {"pergunta": "Qual é a capital da Argentina?", "alternativas": ["Córdoba", "Rosário", "Buenos Aires"], "correta": 2},
        {"pergunta": "Qual é a capital do Japão?", "alternativas": ["Osaka", "Tóquio", "Kyoto"], "correta": 1},
        {"pergunta": "Qual é a capital de Portugal?", "alternativas": ["Lisboa", "Porto", "Coimbra"], "correta": 0},
    ],

    "Bandeiras do Mundo": [
        {"pergunta": "Qual país possui uma folha de bordo vermelha em sua bandeira?", "alternativas": ["Estados Unidos", "Canadá", "Austrália"], "correta": 1},
        {"pergunta": "Qual país possui um círculo vermelho sobre fundo branco em sua bandeira?", "alternativas": ["Japão", "China", "Coreia do Sul"], "correta": 0},
        {"pergunta": "Qual país possui uma bandeira verde, amarela, azul e branca?", "alternativas": ["Argentina", "Chile", "Brasil"], "correta": 2},
        {"pergunta": "Qual país possui estrelas brancas e listras vermelhas e brancas em sua bandeira?", "alternativas": ["França", "Estados Unidos", "Canadá"], "correta": 1},
        {"pergunta": "Qual país possui uma cruz azul sobre fundo branco em sua bandeira?", "alternativas": ["Finlândia", "Itália", "Espanha"], "correta": 0},
    ],

    "Monumentos Famosos": [
        {"pergunta": "Em qual cidade fica a Torre Eiffel?", "alternativas": ["Roma", "Paris", "Londres"], "correta": 1},
        {"pergunta": "Em qual país fica o Cristo Redentor?", "alternativas": ["Brasil", "Argentina", "Portugal"], "correta": 0},
        {"pergunta": "Em qual cidade fica o Coliseu?", "alternativas": ["Atenas", "Madrid", "Roma"], "correta": 2},
        {"pergunta": "Qual monumento fica em Nova York e representa uma figura segurando uma tocha?", "alternativas": ["Big Ben", "Estátua da Liberdade", "Torre de Pisa"], "correta": 1},
        {"pergunta": "Em qual país fica o Taj Mahal?", "alternativas": ["Índia", "Egito", "China"], "correta": 0},
    ],

    "Maravilhas do Mundo": [
        {"pergunta": "Qual maravilha moderna fica no Rio de Janeiro?", "alternativas": ["Machu Picchu", "Cristo Redentor", "Coliseu"], "correta": 1},
        {"pergunta": "Qual antiga cidade inca está localizada no Peru?", "alternativas": ["Machu Picchu", "Petra", "Pompeia"], "correta": 0},
        {"pergunta": "Qual maravilha moderna fica na Jordânia e foi esculpida em rochas?", "alternativas": ["Chichén Itzá", "Taj Mahal", "Petra"], "correta": 2},
        {"pergunta": "Qual monumento na Índia foi construído em mármore branco?", "alternativas": ["Coliseu", "Taj Mahal", "Cristo Redentor"], "correta": 1},
        {"pergunta": "Qual grande estrutura da China integra a lista das Novas Sete Maravilhas do Mundo?", "alternativas": ["Grande Muralha da China", "Cidade Proibida", "Templo do Céu"], "correta": 0},
    ],

    "Comidas Brasileiras": [
        {"pergunta": "Qual prato brasileiro é preparado tradicionalmente com feijão e diferentes tipos de carne?", "alternativas": ["Acarajé", "Feijoada", "Cuscuz"], "correta": 1},
        {"pergunta": "Qual alimento típico nordestino é feito principalmente de milho e pode ser cozido no vapor?", "alternativas": ["Cuscuz", "Sushi", "Risoto"], "correta": 0},
        {"pergunta": "Qual quitute baiano é feito com massa de feijão-fradinho e frito em azeite de dendê?", "alternativas": ["Brigadeiro", "Pão de queijo", "Acarajé"], "correta": 2},
        {"pergunta": "Qual alimento é muito associado à culinária de Minas Gerais?", "alternativas": ["Sushi", "Pão de queijo", "Taco"], "correta": 1},
        {"pergunta": "Qual sobremesa brasileira é feita tradicionalmente com leite condensado e chocolate?", "alternativas": ["Brigadeiro", "Tiramisù", "Macaron"], "correta": 0},
    ],

    "Comidas do Mundo": [
        {"pergunta": "Qual prato italiano é feito com massa, molho e frequentemente queijo?", "alternativas": ["Sushi", "Pizza", "Taco"], "correta": 1},
        {"pergunta": "Qual comida japonesa costuma combinar arroz temperado com peixe ou outros ingredientes?", "alternativas": ["Sushi", "Paella", "Hambúrguer"], "correta": 0},
        {"pergunta": "Qual prato espanhol costuma ser preparado com arroz e pode conter frutos do mar?", "alternativas": ["Pizza", "Lasanha", "Paella"], "correta": 2},
        {"pergunta": "Qual comida mexicana utiliza frequentemente uma tortilla dobrada com recheio?", "alternativas": ["Risoto", "Taco", "Sushi"], "correta": 1},
        {"pergunta": "Qual prato italiano é formado por camadas de massa, molho e recheio?", "alternativas": ["Lasanha", "Paella", "Ceviche"], "correta": 0},
    ],

    "Frutas Exóticas": [
        {"pergunta": "Qual fruta possui casca rosa ou avermelhada e polpa com pequenas sementes pretas?", "alternativas": ["Carambola", "Pitaya", "Maçã"], "correta": 1},
        {"pergunta": "Qual fruta possui formato semelhante a uma estrela quando cortada transversalmente?", "alternativas": ["Carambola", "Banana", "Mamão"], "correta": 0},
        {"pergunta": "Qual fruta possui casca coberta por estruturas semelhantes a pelos e polpa branca translúcida?", "alternativas": ["Melancia", "Pera", "Rambutão"], "correta": 2},
        {"pergunta": "Qual fruta é conhecida por seu odor muito forte e é popular no Sudeste Asiático?", "alternativas": ["Uva", "Durian", "Laranja"], "correta": 1},
        {"pergunta": "Qual fruta tropical possui polpa branca dividida em gomos e casca roxa espessa?", "alternativas": ["Mangostão", "Limão", "Caju"], "correta": 0},
    ],

    "Doces Famosos": [
        {"pergunta": "Qual doce brasileiro é feito principalmente com leite condensado e chocolate?", "alternativas": ["Quindim", "Brigadeiro", "Pudim"], "correta": 1},
        {"pergunta": "Qual doce francês é composto por duas partes arredondadas de merengue de amêndoas com recheio?", "alternativas": ["Macaron", "Brownie", "Churros"], "correta": 0},
        {"pergunta": "Qual sobremesa italiana leva tradicionalmente café e queijo mascarpone?", "alternativas": ["Pavê", "Petit gâteau", "Tiramisù"], "correta": 2},
        {"pergunta": "Qual doce espanhol é feito de massa frita e frequentemente servido com açúcar?", "alternativas": ["Macaron", "Churros", "Cheesecake"], "correta": 1},
        {"pergunta": "Qual sobremesa possui uma camada de açúcar caramelizado sobre um creme?", "alternativas": ["Crème brûlée", "Brownie", "Brigadeiro"], "correta": 0},
    ],

    "Marcas e Logotipos": [
        {"pergunta": "Qual empresa possui uma maçã mordida como logotipo?", "alternativas": ["Samsung", "Apple", "Sony"], "correta": 1},
        {"pergunta": "Qual marca esportiva utiliza um símbolo conhecido como Swoosh?", "alternativas": ["Nike", "Adidas", "Puma"], "correta": 0},
        {"pergunta": "Qual rede de fast-food é conhecida pelos arcos dourados?", "alternativas": ["Subway", "KFC", "McDonald's"], "correta": 2},
        {"pergunta": "Qual marca de automóveis utiliza quatro argolas interligadas?", "alternativas": ["BMW", "Audi", "Volvo"], "correta": 1},
        {"pergunta": "Qual marca esportiva possui três listras como elemento marcante de sua identidade?", "alternativas": ["Adidas", "Nike", "Reebok"], "correta": 0},
    ],

    "Tecnologia do Dia a Dia": [
        {"pergunta": "Qual aparelho é usado principalmente para fazer ligações, enviar mensagens e acessar aplicativos?", "alternativas": ["Impressora", "Smartphone", "Liquidificador"], "correta": 1},
        {"pergunta": "Qual aparelho transforma documentos digitais em cópias no papel?", "alternativas": ["Impressora", "Roteador", "Teclado"], "correta": 0},
        {"pergunta": "Qual dispositivo permite movimentar o ponteiro na tela de um computador?", "alternativas": ["Monitor", "Caixa de som", "Mouse"], "correta": 2},
        {"pergunta": "Qual aparelho distribui normalmente uma conexão de internet por Wi-Fi dentro de casa?", "alternativas": ["Scanner", "Roteador", "Projetor"], "correta": 1},
        {"pergunta": "Qual equipamento mostra visualmente as informações produzidas pelo computador?", "alternativas": ["Monitor", "Microfone", "Teclado"], "correta": 0},
    ],

    "Internet e Redes Sociais": [
        {"pergunta": "Como é chamada uma sequência de caracteres usada para acessar uma conta com segurança?", "alternativas": ["Link", "Senha", "Emoji"], "correta": 1},
        {"pergunta": "Qual símbolo é muito usado para criar hashtags?", "alternativas": ["#", "@", "&"], "correta": 0},
        {"pergunta": "Como é chamado um endereço que leva a uma página ou conteúdo na internet?", "alternativas": ["Senha", "Emoji", "Link"], "correta": 2},
        {"pergunta": "Qual símbolo geralmente aparece antes do nome de usuário em menções nas redes sociais?", "alternativas": ["#", "@", "%"], "correta": 1},
        {"pergunta": "Como é chamado o conteúdo publicado por um usuário em uma rede social?", "alternativas": ["Postagem", "Processador", "Roteador"], "correta": 0},
    ],

    "Curiosidades sobre Celulares": [
        {"pergunta": "Qual componente permite tocar diretamente nos elementos exibidos na maioria dos smartphones atuais?", "alternativas": ["Antena", "Tela sensível ao toque", "Alto-falante"], "correta": 1},
        {"pergunta": "Qual recurso permite tirar fotografias com um celular?", "alternativas": ["Câmera", "Microfone", "GPS"], "correta": 0},
        {"pergunta": "Qual tecnologia permite identificar a localização do aparelho por satélite?", "alternativas": ["Bluetooth", "NFC", "GPS"], "correta": 2},
        {"pergunta": "Qual tecnologia permite conectar acessórios próximos sem fio, como fones e caixas de som?", "alternativas": ["HDMI", "Bluetooth", "VGA"], "correta": 1},
        {"pergunta": "Qual componente fornece energia ao celular quando ele não está conectado à tomada?", "alternativas": ["Bateria", "Câmera", "Tela"], "correta": 0},
    ],

    "Coisas que Existem Dentro de Casa": [
        {"pergunta": "Qual eletrodoméstico conserva alimentos em baixa temperatura?", "alternativas": ["Fogão", "Geladeira", "Liquidificador"], "correta": 1},
        {"pergunta": "Qual aparelho é usado para lavar roupas automaticamente?", "alternativas": ["Máquina de lavar", "Micro-ondas", "Ventilador"], "correta": 0},
        {"pergunta": "Qual objeto é usado normalmente para sentar?", "alternativas": ["Janela", "Tapete", "Cadeira"], "correta": 2},
        {"pergunta": "Qual aparelho pode aquecer alimentos rapidamente usando micro-ondas?", "alternativas": ["Geladeira", "Micro-ondas", "Ventilador"], "correta": 1},
        {"pergunta": "Qual móvel é usado principalmente para guardar roupas?", "alternativas": ["Guarda-roupa", "Fogão", "Pia"], "correta": 0},
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
