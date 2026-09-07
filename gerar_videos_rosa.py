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
QUIZZES = {
    "Profissões e Trabalhos": [
        {"pergunta": "Qual profissional é responsável por projetar edifícios?", "alternativas": ["Mecânico", "Arquiteto", "Farmacêutico"], "correta": 1},
        {"pergunta": "Qual profissional trabalha diretamente no combate a incêndios?", "alternativas": ["Contador", "Dentista", "Bombeiro"], "correta": 2},
        {"pergunta": "Qual profissional cuida da saúde dos animais?", "alternativas": ["Veterinário", "Advogado", "Arquiteto"], "correta": 0},
        {"pergunta": "Quem representa clientes em processos judiciais?", "alternativas": ["Padeiro", "Advogado", "Eletricista"], "correta": 1},
        {"pergunta": "Qual profissional atua em farmácias e orienta sobre medicamentos?", "alternativas": ["Jornalista", "Veterinário", "Farmacêutico"], "correta": 2},
    ],

    "Objetos do Dia a Dia": [
        {"pergunta": "Qual objeto é usado normalmente para saber as horas?", "alternativas": ["Tesoura", "Pente", "Relógio"], "correta": 2},
        {"pergunta": "Qual objeto usamos para abrir uma porta com fechadura?", "alternativas": ["Chave", "Copo", "Prato"], "correta": 0},
        {"pergunta": "Qual objeto é usado para cortar papel?", "alternativas": ["Colher", "Tesoura", "Almofada"], "correta": 1},
        {"pergunta": "Qual objeto é usado para pentear o cabelo?", "alternativas": ["Régua", "Garfo", "Pente"], "correta": 2},
        {"pergunta": "Qual objeto é usado normalmente para enxugar o corpo após o banho?", "alternativas": ["Toalha", "Panela", "Caderno"], "correta": 0},
    ],

    "Coisas de Escola": [
        {"pergunta": "Qual material apaga o que foi escrito a lápis?", "alternativas": ["Borracha", "Cola", "Tesoura"], "correta": 0},
        {"pergunta": "Qual disciplina estuda números, cálculos e operações?", "alternativas": ["História", "Matemática", "Geografia"], "correta": 1},
        {"pergunta": "Qual objeto é usado para apontar um lápis?", "alternativas": ["Régua", "Grampeador", "Apontador"], "correta": 2},
        {"pergunta": "Onde o estudante normalmente faz suas anotações?", "alternativas": ["Caderno", "Estojo", "Mochila"], "correta": 0},
        {"pergunta": "Qual instrumento escolar é usado para medir linhas retas?", "alternativas": ["Pincel", "Régua", "Borracha"], "correta": 1},
    ],

    "Brinquedos Antigos": [
        {"pergunta": "Qual brinquedo gira no chão depois de ser lançado com um barbante?", "alternativas": ["Peteca", "Pião", "Bambolê"], "correta": 1},
        {"pergunta": "Qual brinquedo sobe e desce preso a um fio?", "alternativas": ["Ioiô", "Pipa", "Bilboquê"], "correta": 0},
        {"pergunta": "Qual brincadeira utiliza pequenas esferas de vidro?", "alternativas": ["Amarelinha", "Pega-pega", "Bolinha de gude"], "correta": 2},
        {"pergunta": "Qual brinquedo tradicional é rebatido com a mão e possui penas?", "alternativas": ["Pião", "Peteca", "Carrinho"], "correta": 1},
        {"pergunta": "Qual brinquedo possui uma bola presa por um cordão a uma peça com encaixe?", "alternativas": ["Bilboquê", "Dominó", "Bambolê"], "correta": 0},
    ],

    "Brinquedos Atuais": [
        {"pergunta": "Qual brinquedo possui bolhas que podem ser pressionadas repetidamente?", "alternativas": ["Pião", "Ioiô", "Pop it"], "correta": 2},
        {"pergunta": "Qual quebra-cabeça possui faces formadas por pequenos quadrados coloridos?", "alternativas": ["Bambolê", "Cubo mágico", "Peteca"], "correta": 1},
        {"pergunta": "Qual brinquedo é formado por peças que se encaixam para montar construções?", "alternativas": ["Blocos de montar", "Bilboquê", "Pião"], "correta": 0},
        {"pergunta": "Qual brinquedo pode ser dirigido usando um controle à distância?", "alternativas": ["Dominó", "Bola de gude", "Carrinho de controle remoto"], "correta": 2},
        {"pergunta": "Como é chamado um boneco inspirado em heróis e personagens?", "alternativas": ["Bambolê", "Boneco de ação", "Peteca"], "correta": 1},
    ],

    "Jogos de Tabuleiro": [
        {"pergunta": "Em qual jogo o objetivo é dar xeque-mate no rei adversário?", "alternativas": ["Xadrez", "Dominó", "Ludo"], "correta": 0},
        {"pergunta": "Qual jogo usa peças divididas ao meio com pontos?", "alternativas": ["Xadrez", "Damas", "Dominó"], "correta": 2},
        {"pergunta": "Em qual jogo os participantes podem comprar propriedades e cobrar aluguel?", "alternativas": ["Batalha Naval", "Banco Imobiliário", "Damas"], "correta": 1},
        {"pergunta": "Qual jogo tradicional usa peças diagonais em um tabuleiro quadriculado?", "alternativas": ["Damas", "Uno", "Dominó"], "correta": 0},
        {"pergunta": "Qual jogo consiste em descobrir a posição dos navios do adversário?", "alternativas": ["Ludo", "Xadrez", "Batalha Naval"], "correta": 2},
    ],

    "Palavras Difíceis": [
        {"pergunta": "O que significa a palavra 'efêmero'?", "alternativas": ["Que nunca termina", "Que dura pouco tempo", "Que é muito pesado"], "correta": 1},
        {"pergunta": "O que significa 'benevolente'?", "alternativas": ["Apressado", "Barulhento", "Bondoso"], "correta": 2},
        {"pergunta": "O que significa a palavra 'sucinto'?", "alternativas": ["Breve e direto", "Muito antigo", "Extremamente caro"], "correta": 0},
        {"pergunta": "O que significa alguém ser perspicaz?", "alternativas": ["Ser muito lento", "Perceber as coisas com facilidade", "Dormir bastante"], "correta": 1},
        {"pergunta": "O que significa algo ser inócuo?", "alternativas": ["Ser muito caro", "Ser barulhento", "Não causar dano"], "correta": 2},
    ],

    "Sinônimos e Antônimos": [
        {"pergunta": "Qual é o antônimo de alto?", "alternativas": ["Grande", "Comprido", "Baixo"], "correta": 2},
        {"pergunta": "Qual palavra é sinônimo de rápido?", "alternativas": ["Veloz", "Lento", "Pesado"], "correta": 0},
        {"pergunta": "Qual é o antônimo de cheio?", "alternativas": ["Pesado", "Vazio", "Grande"], "correta": 1},
        {"pergunta": "Qual palavra é sinônimo de bonito?", "alternativas": ["Fraco", "Feio", "Belo"], "correta": 2},
        {"pergunta": "Qual palavra é sinônimo de começar?", "alternativas": ["Iniciar", "Terminar", "Parar"], "correta": 0},
    ],

    "Ditados Populares": [
        {"pergunta": "Complete: Quem espera sempre...", "alternativas": ["Alcança", "Esquece", "Corre"], "correta": 0},
        {"pergunta": "Complete: Quem não arrisca, não...", "alternativas": ["Descansa", "Petisca", "Aprende"], "correta": 1},
        {"pergunta": "Complete: De grão em grão, a galinha enche o...", "alternativas": ["Ninho", "Prato", "Papo"], "correta": 2},
        {"pergunta": "Complete: Água mole em pedra dura, tanto bate até que...", "alternativas": ["Fura", "Seca", "Some"], "correta": 0},
        {"pergunta": "Complete: Mais vale um pássaro na mão do que...", "alternativas": ["Um cantando", "Dois voando", "Três dormindo"], "correta": 1},
    ],

    "Expressões Brasileiras": [
        {"pergunta": "O que significa a expressão 'quebrar o galho'?", "alternativas": ["Ficar bravo", "Ajudar a resolver um problema", "Quebrar uma árvore"], "correta": 1},
        {"pergunta": "O que significa 'pisar na bola'?", "alternativas": ["Jogar futebol", "Correr muito", "Cometer um erro"], "correta": 2},
        {"pergunta": "O que significa 'colocar a mão na massa'?", "alternativas": ["Começar a fazer algo", "Desistir", "Dormir"], "correta": 0},
        {"pergunta": "O que significa 'ficar de boca aberta'?", "alternativas": ["Ficar com sono", "Ficar surpreso", "Ficar com fome"], "correta": 1},
        {"pergunta": "O que significa 'dar com a língua nos dentes'?", "alternativas": ["Ficar em silêncio", "Comer rapidamente", "Contar um segredo"], "correta": 2},
    ],

    "Gírias Brasileiras": [
        {"pergunta": "Na gíria, o que significa dizer que algo é 'top'?", "alternativas": ["Muito velho", "Muito longe", "Muito bom"], "correta": 2},
        {"pergunta": "Na gíria brasileira, o que significa 'grana'?", "alternativas": ["Dinheiro", "Roupa", "Comida"], "correta": 0},
        {"pergunta": "O que significa dizer que alguém 'mandou bem'?", "alternativas": ["Foi embora", "Fez algo bem", "Mandou uma carta"], "correta": 1},
        {"pergunta": "O que significa a expressão 'dar ruim'?", "alternativas": ["Melhorar", "Ficar barato", "Algo dar errado"], "correta": 2},
        {"pergunta": "Na gíria, o que geralmente significa dizer 'partiu'?", "alternativas": ["Vamos", "Pare", "Durma"], "correta": 0},
    ],

    "Adivinhações": [
        {"pergunta": "O que é, o que é: tem dentes, mas não morde?", "alternativas": ["Pente", "Jacaré", "Cachorro"], "correta": 0},
        {"pergunta": "O que é, o que é: quanto mais se tira, maior fica?", "alternativas": ["Balde", "Buraco", "Caixa"], "correta": 1},
        {"pergunta": "O que é, o que é: cai em pé e corre deitado?", "alternativas": ["Gato", "Árvore", "Chuva"], "correta": 2},
        {"pergunta": "O que é, o que é: tem asa e bico, mas não voa nem bica?", "alternativas": ["Bule", "Galinha", "Avião"], "correta": 0},
        {"pergunta": "O que é, o que é: tem cabeça e dentes, mas não é gente?", "alternativas": ["Peixe", "Alho", "Boneca"], "correta": 1},
    ],

    "Raciocínio Lógico": [
        {"pergunta": "Se Ana é mais alta que Bia e Bia é mais alta que Carla, quem é a mais alta?", "alternativas": ["Bia", "Ana", "Carla"], "correta": 1},
        {"pergunta": "Uma família tem dois pais e dois filhos, mas apenas três pessoas. Quem são?", "alternativas": ["Três irmãos", "Três primos", "Avô, pai e filho"], "correta": 2},
        {"pergunta": "Se hoje é segunda-feira, que dia será daqui a dois dias?", "alternativas": ["Quarta-feira", "Terça-feira", "Sexta-feira"], "correta": 0},
        {"pergunta": "Todos os cães são animais. Rex é um cão. Rex é o quê?", "alternativas": ["Planta", "Animal", "Objeto"], "correta": 1},
        {"pergunta": "Qual número completa: 3, 6, 9, 12, ...?", "alternativas": ["14", "16", "15"], "correta": 2},
    ],

    "Matemática Rápida": [
        {"pergunta": "Quanto é 8 vezes 7?", "alternativas": ["54", "64", "56"], "correta": 2},
        {"pergunta": "Quanto é 100 dividido por 4?", "alternativas": ["25", "20", "40"], "correta": 0},
        {"pergunta": "Quanto é 15 mais 27?", "alternativas": ["32", "42", "52"], "correta": 1},
        {"pergunta": "Quanto é 9 vezes 9?", "alternativas": ["72", "99", "81"], "correta": 2},
        {"pergunta": "Quanto é metade de 150?", "alternativas": ["75", "50", "100"], "correta": 0},
    ],

    "Sequências e Padrões": [
        {"pergunta": "Qual número vem depois: 5, 10, 15, 20?", "alternativas": ["25", "22", "30"], "correta": 0},
        {"pergunta": "Complete a sequência: 2, 4, 8, 16, ...", "alternativas": ["24", "32", "18"], "correta": 1},
        {"pergunta": "Qual número vem depois: 30, 25, 20, 15?", "alternativas": ["5", "12", "10"], "correta": 2},
        {"pergunta": "Complete: 1, 4, 7, 10, ...", "alternativas": ["13", "12", "14"], "correta": 0},
        {"pergunta": "Qual letra vem depois: A, C, E, G?", "alternativas": ["H", "I", "J"], "correta": 1},
    ],

    "Perguntas de Pegadinha": [
        {"pergunta": "Quantos meses do ano possuem pelo menos 28 dias?", "alternativas": ["1", "12", "6"], "correta": 1},
        {"pergunta": "Onde devem ser enterrados os sobreviventes de um acidente de avião?", "alternativas": ["No país mais próximo", "No aeroporto", "Sobreviventes não são enterrados"], "correta": 2},
        {"pergunta": "O que pesa mais: um quilo de ferro ou um quilo de algodão?", "alternativas": ["Pesam igual", "Ferro", "Algodão"], "correta": 0},
        {"pergunta": "Quantas vezes você pode subtrair 10 de 100 antes de deixar de estar subtraindo de 100?", "alternativas": ["10 vezes", "Uma vez", "5 vezes"], "correta": 1},
        {"pergunta": "Qual mão é melhor para mexer o café?", "alternativas": ["Direita", "Esquerda", "Nenhuma, é melhor usar uma colher"], "correta": 2},
    ],

    "Verdade ou Mito": [
        {"pergunta": "Polvos possuem três corações. Isso é verdade ou mito?", "alternativas": ["Mito", "Depende da espécie", "Verdade"], "correta": 2},
        {"pergunta": "O Sol é uma estrela. Isso é verdade ou mito?", "alternativas": ["Verdade", "Mito", "Só durante o dia"], "correta": 0},
        {"pergunta": "Morcegos são completamente cegos. Isso é verdade ou mito?", "alternativas": ["Verdade", "Mito", "Somente à noite"], "correta": 1},
        {"pergunta": "A água pura ao nível do mar ferve aproximadamente a 100 graus Celsius. Verdade ou mito?", "alternativas": ["Só no inverno", "Mito", "Verdade"], "correta": 2},
        {"pergunta": "A Grande Muralha da China é facilmente visível da Lua a olho nu. Verdade ou mito?", "alternativas": ["Mito", "Verdade", "Somente à noite"], "correta": 0},
    ],

    "Invenções Curiosas": [
        {"pergunta": "Quem inventou o fecho de velcro após observar sementes presas à roupa?", "alternativas": ["Thomas Edison", "George de Mestral", "Nikola Tesla"], "correta": 1},
        {"pergunta": "Qual engenheiro descobriu acidentalmente o efeito que levou ao forno de micro-ondas?", "alternativas": ["Alexander Bell", "James Watt", "Percy Spencer"], "correta": 2},
        {"pergunta": "Qual invenção de Walter Hunt é usada para prender tecidos?", "alternativas": ["Alfinete de segurança", "Rádio", "Bússola"], "correta": 0},
        {"pergunta": "Qual invenção usa pequenos dentes para abrir e fechar roupas e bolsas?", "alternativas": ["Botão", "Zíper", "Grampo"], "correta": 1},
        {"pergunta": "Qual produto de escritório surgiu de um adesivo de baixa aderência desenvolvido pela 3M?", "alternativas": ["Calculadora", "Caneta esferográfica", "Post-it"], "correta": 2},
    ],

    "Descobertas Famosas": [
        {"pergunta": "Quem descobriu a penicilina em 1928?", "alternativas": ["Isaac Newton", "Louis Pasteur", "Alexander Fleming"], "correta": 2},
        {"pergunta": "Quem descobriu os raios X em 1895?", "alternativas": ["Wilhelm Röntgen", "Albert Einstein", "Thomas Edison"], "correta": 0},
        {"pergunta": "Quem identificou a radioatividade natural do urânio?", "alternativas": ["Charles Darwin", "Henri Becquerel", "Galileu Galilei"], "correta": 1},
        {"pergunta": "Qual cientista formulou as leis do movimento e da gravitação universal?", "alternativas": ["Darwin", "Pasteur", "Isaac Newton"], "correta": 2},
        {"pergunta": "Quem realizou observações pioneiras de microrganismos usando microscópios?", "alternativas": ["Antonie van Leeuwenhoek", "Graham Bell", "James Watt"], "correta": 0},
    ],

    "Grandes Inventores": [
        {"pergunta": "Quem aperfeiçoou uma lâmpada incandescente comercialmente prática?", "alternativas": ["Thomas Edison", "Charles Darwin", "Galileu"], "correta": 0},
        {"pergunta": "Qual inventor é fortemente associado ao desenvolvimento da corrente alternada?", "alternativas": ["Louis Pasteur", "Nikola Tesla", "Johannes Gutenberg"], "correta": 1},
        {"pergunta": "Qual brasileiro ficou famoso por seus trabalhos pioneiros na aviação?", "alternativas": ["Machado de Assis", "Portinari", "Santos Dumont"], "correta": 2},
        {"pergunta": "Quem desenvolveu a prensa de tipos móveis na Europa do século XV?", "alternativas": ["Johannes Gutenberg", "Marco Polo", "Albert Einstein"], "correta": 0},
        {"pergunta": "Quem criou a World Wide Web?", "alternativas": ["Bill Gates", "Tim Berners-Lee", "Steve Jobs"], "correta": 1},
    ],

    "Meios de Transporte": [
        {"pergunta": "Qual meio de transporte se desloca sobre trilhos?", "alternativas": ["Avião", "Trem", "Navio"], "correta": 1},
        {"pergunta": "Qual meio de transporte é usado para viajar pelo ar?", "alternativas": ["Ônibus", "Bicicleta", "Avião"], "correta": 2},
        {"pergunta": "Qual veículo normalmente possui duas rodas e pedais?", "alternativas": ["Bicicleta", "Caminhão", "Trem"], "correta": 0},
        {"pergunta": "Qual transporte urbano pode circular por túneis subterrâneos?", "alternativas": ["Navio", "Metrô", "Helicóptero"], "correta": 1},
        {"pergunta": "Qual meio de transporte é usado para atravessar oceanos transportando cargas?", "alternativas": ["Motocicleta", "Metrô", "Navio"], "correta": 2},
    ],

    "Carros Famosos": [
        {"pergunta": "Qual fabricante produz o modelo Mustang?", "alternativas": ["Toyota", "Fiat", "Ford"], "correta": 2},
        {"pergunta": "Qual marca fabrica o Corolla?", "alternativas": ["Toyota", "Ferrari", "Jeep"], "correta": 0},
        {"pergunta": "Qual marca ficou famosa pelo Fusca?", "alternativas": ["Peugeot", "Volkswagen", "Volvo"], "correta": 1},
        {"pergunta": "Qual fabricante italiano usa o cavalo rampante como símbolo?", "alternativas": ["Honda", "Ford", "Ferrari"], "correta": 2},
        {"pergunta": "Qual marca fabrica o modelo Civic?", "alternativas": ["Honda", "Renault", "Fiat"], "correta": 0},
    ],

    "Motos e Velocidade": [
        {"pergunta": "Quantas rodas possui normalmente uma motocicleta?", "alternativas": ["2", "3", "4"], "correta": 0},
        {"pergunta": "Qual equipamento protege a cabeça do motociclista?", "alternativas": ["Cinto", "Capacete", "Colete salva-vidas"], "correta": 1},
        {"pergunta": "Qual marca fabrica a linha de motocicletas Ninja?", "alternativas": ["Ferrari", "Volvo", "Kawasaki"], "correta": 2},
        {"pergunta": "Qual unidade é usada no Brasil para indicar a velocidade dos veículos?", "alternativas": ["km/h", "kg", "litro"], "correta": 0},
        {"pergunta": "Qual comando na mão direita normalmente controla a aceleração da motocicleta?", "alternativas": ["Buzina", "Punho do acelerador", "Retrovisor"], "correta": 1},
    ],

    "Aviões e Aviação": [
        {"pergunta": "Qual parte principal do avião produz sustentação durante o voo?", "alternativas": ["Rodas", "Asas", "Janelas"], "correta": 1},
        {"pergunta": "Como é chamado o local onde aviões pousam e decolam?", "alternativas": ["Porto", "Rodoviária", "Aeroporto"], "correta": 2},
        {"pergunta": "Quem normalmente comanda uma aeronave?", "alternativas": ["Piloto", "Marinheiro", "Motorista"], "correta": 0},
        {"pergunta": "Como é chamada a área onde ficam os controles dos pilotos?", "alternativas": ["Porão", "Cabine de comando", "Convés"], "correta": 1},
        {"pergunta": "Qual instrumento indica a altitude de uma aeronave?", "alternativas": ["Cronômetro", "Termômetro", "Altímetro"], "correta": 2},
    ],

    "Navios e Oceanos": [
        {"pergunta": "Como é chamada a parte da frente de um navio?", "alternativas": ["Popa", "Convés", "Proa"], "correta": 2},
        {"pergunta": "Qual instrumento tradicional ajuda a encontrar direções durante uma navegação?", "alternativas": ["Bússola", "Termômetro", "Microscópio"], "correta": 0},
        {"pergunta": "Como é chamado o lado direito de uma embarcação olhando para a proa?", "alternativas": ["Bombordo", "Estibordo", "Popa"], "correta": 1},
        {"pergunta": "Como é chamado o local onde navios atracam?", "alternativas": ["Aeroporto", "Estação", "Porto"], "correta": 2},
        {"pergunta": "Qual oceano separa grande parte das Américas da Europa e da África?", "alternativas": ["Atlântico", "Pacífico", "Ártico"], "correta": 0},
    ],

    "Trânsito e Placas": [
        {"pergunta": "Qual cor do semáforo indica que o veículo deve parar?", "alternativas": ["Vermelho", "Verde", "Azul"], "correta": 0},
        {"pergunta": "Qual placa octogonal vermelha determina parada obrigatória?", "alternativas": ["Hospital", "PARE", "Estacionamento"], "correta": 1},
        {"pergunta": "Qual equipamento deve ser usado pelos ocupantes de um automóvel?", "alternativas": ["Colete salva-vidas", "Capacete de ciclismo", "Cinto de segurança"], "correta": 2},
        {"pergunta": "Qual cor do semáforo normalmente permite seguir?", "alternativas": ["Verde", "Vermelho", "Preto"], "correta": 0},
        {"pergunta": "Para que serve uma faixa de pedestres?", "alternativas": ["Estacionar carros", "Indicar local de travessia", "Marcar pista de pouso"], "correta": 1},
    
],

    "Casas e Arquitetura": [
        {"pergunta": "Qual parte da casa protege principalmente contra chuva e sol?", "alternativas": ["Parede", "Telhado", "Rodapé"], "correta": 1},
        {"pergunta": "Qual estrutura é usada para subir de um andar para outro?", "alternativas": ["Parede", "Portão", "Escada"], "correta": 2},
        {"pergunta": "Qual abertura permite entrada de luz e ventilação em um cômodo?", "alternativas": ["Janela", "Piso", "Teto"], "correta": 0},
        {"pergunta": "Qual profissional elabora projetos arquitetônicos?", "alternativas": ["Veterinário", "Arquiteto", "Farmacêutico"], "correta": 1},
        {"pergunta": "Como é chamada uma construção com vários pavimentos?", "alternativas": ["Barraca", "Ponte", "Edifício"], "correta": 2},
    ],

    "Objetos Antigos": [
        {"pergunta": "Qual aparelho era usado para tocar discos de vinil?", "alternativas": ["Scanner", "Micro-ondas", "Vitrola"], "correta": 2},
        {"pergunta": "Qual aparelho era usado para escrever documentos antes dos computadores se popularizarem?", "alternativas": ["Máquina de escrever", "Televisão", "Rádio"], "correta": 0},
        {"pergunta": "Qual aparelho portátil ficou famoso por tocar fitas cassete?", "alternativas": ["Tablet", "Walkman", "Blu-ray"], "correta": 1},
        {"pergunta": "Qual aparelho doméstico era usado para assistir fitas VHS?", "alternativas": ["Roteador", "Smartphone", "Videocassete"], "correta": 2},
        {"pergunta": "Qual objeto antigo podia ser aquecido com brasas para passar roupas?", "alternativas": ["Ferro a carvão", "Ventilador", "Liquidificador"], "correta": 0},
    ],

    "Coisas dos Anos 80": [
        {"pergunta": "Qual tipo de fita era muito usado para ouvir música nos anos 80?", "alternativas": ["Fita cassete", "Blu-ray", "Pendrive"], "correta": 0},
        {"pergunta": "Qual aparelho portátil popularizou a música em fitas cassete durante os anos 80?", "alternativas": ["Tablet", "Walkman", "Smartwatch"], "correta": 1},
        {"pergunta": "Qual formato de vídeo doméstico teve grande popularidade nos anos 80?", "alternativas": ["Streaming", "DVD", "VHS"], "correta": 2},
        {"pergunta": "Qual quebra-cabeça colorido virou um ícone mundial nos anos 80?", "alternativas": ["Cubo mágico", "Pop it", "Fidget spinner"], "correta": 0},
        {"pergunta": "Qual tipo de telefone doméstico era comum antes dos smartphones?", "alternativas": ["Celular dobrável", "Telefone fixo", "Smartwatch"], "correta": 1},
    ],

    "Coisas dos Anos 90": [
        {"pergunta": "Qual brinquedo eletrônico permitia cuidar de um bichinho virtual?", "alternativas": ["Drone", "Tamagotchi", "Pop it"], "correta": 1},
        {"pergunta": "Qual console da Sony foi lançado originalmente nos anos 90?", "alternativas": ["PlayStation 5", "Xbox Series X", "PlayStation"], "correta": 2},
        {"pergunta": "Qual mídia física era muito usada para ouvir álbuns musicais?", "alternativas": ["CD", "Streaming", "Blu-ray"], "correta": 0},
        {"pergunta": "Qual aparelho doméstico era usado para reproduzir fitas VHS?", "alternativas": ["Roteador", "Videocassete", "Smartphone"], "correta": 1},
        {"pergunta": "Qual brinquedo de mola podia 'andar' por degraus?", "alternativas": ["Drone", "Hoverboard", "Mola maluca"], "correta": 2},
    ],

    "Coisas dos Anos 2000": [
        {"pergunta": "Qual rede social teve enorme popularidade no Brasil nos anos 2000?", "alternativas": ["TikTok", "Threads", "Orkut"], "correta": 2},
        {"pergunta": "Qual programa de mensagens instantâneas foi muito usado em computadores?", "alternativas": ["MSN Messenger", "Telegram", "Discord"], "correta": 0},
        {"pergunta": "Qual mídia substituiu amplamente o VHS para assistir filmes em casa?", "alternativas": ["Disquete", "DVD", "Fita cassete"], "correta": 1},
        {"pergunta": "Qual aparelho portátil armazenava arquivos de música no formato MP3?", "alternativas": ["Vitrola", "Mimeógrafo", "MP3 player"], "correta": 2},
        {"pergunta": "Qual celular clássico ficou famoso pelo jogo Snake?", "alternativas": ["Nokia 3310", "Galaxy Fold", "iPhone 15"], "correta": 0},
    ],

    "Nostalgia da Infância": [
        {"pergunta": "Qual brincadeira usa casas numeradas desenhadas no chão?", "alternativas": ["Amarelinha", "Xadrez", "Dominó"], "correta": 0},
        {"pergunta": "Qual brinquedo é empinado no céu usando linha e vento?", "alternativas": ["Carrinho", "Pipa", "Boneca"], "correta": 1},
        {"pergunta": "Qual brincadeira consiste em uma pessoa procurar as outras que estão escondidas?", "alternativas": ["Queimada", "Pega-pega", "Esconde-esconde"], "correta": 2},
        {"pergunta": "Qual doce em formato de bola era muito comum em festas infantis brasileiras?", "alternativas": ["Brigadeiro", "Sushi", "Croissant"], "correta": 0},
        {"pergunta": "Qual brincadeira envolve pular uma corda girada pelas mãos?", "alternativas": ["Bolinha de gude", "Pular corda", "Dominó"], "correta": 1},
    ],

    "Programas de TV Antigos": [
        {"pergunta": "Qual programa infantil brasileiro tinha um castelo cheio de personagens educativos?", "alternativas": ["TV Colosso", "Castelo Rá-Tim-Bum", "Globo Rural"], "correta": 1},
        {"pergunta": "Qual programa infantil brasileiro era apresentado por cachorros em uma emissora de TV?", "alternativas": ["Xou da Xuxa", "Sítio do Picapau Amarelo", "TV Colosso"], "correta": 2},
        {"pergunta": "Qual apresentadora comandou o famoso Xou da Xuxa?", "alternativas": ["Xuxa Meneghel", "Angélica", "Eliana"], "correta": 0},
        {"pergunta": "Em qual programa apareciam personagens como Emília e Visconde de Sabugosa?", "alternativas": ["Chaves", "Sítio do Picapau Amarelo", "TV Colosso"], "correta": 1},
        {"pergunta": "Qual seriado mexicano ficou famoso no Brasil pelo personagem que mora em uma vila?", "alternativas": ["Chapolin", "Rebelde", "Chaves"], "correta": 2},
    ],

    "Propagandas Famosas": [
        {"pergunta": "Qual marca brasileira ficou famosa pelo personagem conhecido como Garoto Bombril?", "alternativas": ["Brastemp", "Coca-Cola", "Bombril"], "correta": 2},
        {"pergunta": "A frase 'Amo muito tudo isso' ficou associada a qual rede de fast-food?", "alternativas": ["McDonald's", "Subway", "Burger King"], "correta": 0},
        {"pergunta": "A expressão 'Não é assim uma Brastemp' ficou ligada a qual tipo de marca?", "alternativas": ["Automóveis", "Eletrodomésticos", "Tênis"], "correta": 1},
        {"pergunta": "O slogan 'Desce redondo' ficou famoso em propagandas de qual bebida?", "alternativas": ["Café", "Suco", "Cerveja"], "correta": 2},
        {"pergunta": "A frase 'Tomou Doril, a dor sumiu' divulgava qual tipo de produto?", "alternativas": ["Analgésico", "Refrigerante", "Sabão"], "correta": 0},
    ],

    "Brincadeiras de Infância": [
        {"pergunta": "Em qual brincadeira uma pessoa deve encontrar os outros participantes escondidos?", "alternativas": ["Pega-pega", "Esconde-esconde", "Queimada"], "correta": 1},
        {"pergunta": "Qual brincadeira utiliza uma bola para tentar acertar os jogadores do outro time?", "alternativas": ["Amarelinha", "Cabra-cega", "Queimada"], "correta": 2},
        {"pergunta": "Qual brincadeira possui casas numeradas desenhadas no chão?", "alternativas": ["Amarelinha", "Pique-bandeira", "Telefone sem fio"], "correta": 0},
        {"pergunta": "Em qual brincadeira uma pessoa fica vendada e tenta encontrar os outros?", "alternativas": ["Pega-pega", "Cabra-cega", "Dominó"], "correta": 1},
        {"pergunta": "Qual brincadeira transmite uma frase cochichada de uma pessoa para outra?", "alternativas": ["Queimada", "Pular corda", "Telefone sem fio"], "correta": 2},
    ],

    "Festas Brasileiras": [
        {"pergunta": "Qual festa tradicional do Maranhão tem como destaque a figura de um boi?", "alternativas": ["Carnaval", "Oktoberfest", "Bumba Meu Boi"], "correta": 2},
        {"pergunta": "Em qual cidade catarinense acontece uma famosa Oktoberfest brasileira?", "alternativas": ["Blumenau", "Salvador", "Recife"], "correta": 0},
        {"pergunta": "Qual grande festa religiosa acontece anualmente em Belém do Pará?", "alternativas": ["Festa do Peão", "Círio de Nazaré", "Carnaval de Olinda"], "correta": 1},
        {"pergunta": "Em qual cidade paulista acontece uma famosa Festa do Peão?", "alternativas": ["Campinas", "Santos", "Barretos"], "correta": 2},
        {"pergunta": "Qual festa amazonense tem os bois Garantido e Caprichoso?", "alternativas": ["Festival de Parintins", "Festa do Divino", "Lavagem do Bonfim"], "correta": 0},
    ],


    "Carnaval": [
        {"pergunta": "Como é chamada a música criada especialmente para o desfile de uma escola de samba?", "alternativas": ["Marcha militar", "Samba-enredo", "Sertanejo"], "correta": 1},
        {"pergunta": "Qual ritmo e dança é símbolo do Carnaval pernambucano?", "alternativas": ["Axé", "Samba", "Frevo"], "correta": 2},
        {"pergunta": "Qual veículo musical é muito associado ao Carnaval de Salvador?", "alternativas": ["Trio elétrico", "Carro de boi", "Trem"], "correta": 0},
        {"pergunta": "Como é chamado o local construído para desfiles de escolas de samba?", "alternativas": ["Estádio", "Sambódromo", "Teatro"], "correta": 1},
        {"pergunta": "Qual manifestação cultural também é muito ligada ao Carnaval de Pernambuco?", "alternativas": ["Tango", "Flamenco", "Maracatu"], "correta": 2},
    ],

    "Natal pelo Mundo": [
        {"pergunta": "Em qual data é comemorado o Natal em grande parte do mundo cristão?", "alternativas": ["31 de outubro", "1 de janeiro", "25 de dezembro"], "correta": 2},
        {"pergunta": "O panetone surgiu originalmente em qual país?", "alternativas": ["Itália", "Brasil", "Japão"], "correta": 0},
        {"pergunta": "Qual país europeu é famoso por seus tradicionais mercados de Natal?", "alternativas": ["Austrália", "Alemanha", "México"], "correta": 1},
        {"pergunta": "Qual planta vermelha é muito usada como decoração natalina?", "alternativas": ["Girassol", "Orquídea azul", "Poinsétia"], "correta": 2},
        {"pergunta": "Qual personagem tradicional distribui presentes no Natal?", "alternativas": ["Papai Noel", "Coelho da Páscoa", "Cupido"], "correta": 0},
    ],

    "Halloween": [
        {"pergunta": "Em que data é comemorado tradicionalmente o Halloween?", "alternativas": ["31 de outubro", "25 de dezembro", "1 de janeiro"], "correta": 0},
        {"pergunta": "Qual vegetal é tradicionalmente esculpido para criar lanternas de Halloween?", "alternativas": ["Batata", "Abóbora", "Cenoura"], "correta": 1},
        {"pergunta": "Qual expressão as crianças usam ao pedir doces em países de língua inglesa?", "alternativas": ["Happy Birthday", "Good Morning", "Trick or Treat"], "correta": 2},
        {"pergunta": "Qual antiga celebração celta é frequentemente relacionada às origens do Halloween?", "alternativas": ["Samhain", "Oktoberfest", "Hanami"], "correta": 0},
        {"pergunta": "Quais cores são muito associadas ao Halloween?", "alternativas": ["Azul e branco", "Laranja e preto", "Verde e amarelo"], "correta": 1},
    ],

    "Folclore Brasileiro": [
        {"pergunta": "Qual personagem do folclore brasileiro é conhecido por ter uma perna só?", "alternativas": ["Curupira", "Saci", "Boitatá"], "correta": 1},
        {"pergunta": "Qual personagem possui os pés virados para trás?", "alternativas": ["Iara", "Boto", "Curupira"], "correta": 2},
        {"pergunta": "Qual personagem é descrita como uma sereia dos rios?", "alternativas": ["Iara", "Cuca", "Mula sem Cabeça"], "correta": 0},
        {"pergunta": "Qual personagem amazônico se transforma em homem durante festas, segundo a lenda?", "alternativas": ["Saci", "Boto-cor-de-rosa", "Boitatá"], "correta": 1},
        {"pergunta": "Qual criatura folclórica é descrita como uma serpente de fogo?", "alternativas": ["Cuca", "Lobisomem", "Boitatá"], "correta": 2},
    ],

    "Lendas Urbanas": [
        {"pergunta": "Qual lenda brasileira fala de uma aparição em banheiros de escolas?", "alternativas": ["Homem do Saco", "Chupacabra", "Loira do Banheiro"], "correta": 2},
        {"pergunta": "Qual lenda envolve repetir um nome diante de um espelho?", "alternativas": ["Bloody Mary", "Pé Grande", "Mothman"], "correta": 0},
        {"pergunta": "Qual criatura lendária ficou conhecida por supostamente atacar animais na América Latina?", "alternativas": ["Sereia", "Chupacabra", "Unicórnio"], "correta": 1},
        {"pergunta": "Qual figura folclórica urbana é usada em histórias para assustar crianças que desobedecem?", "alternativas": ["Papai Noel", "Coelho da Páscoa", "Homem do Saco"], "correta": 2},
        {"pergunta": "Qual personagem de terror surgiu originalmente como uma criação da internet?", "alternativas": ["Slender Man", "Drácula", "Frankenstein"], "correta": 0},
    ],

    "Mistérios Históricos": [
        {"pergunta": "Qual colônia inglesa ficou conhecida pelo desaparecimento de seus habitantes no século XVI?", "alternativas": ["Roanoke", "Jamestown", "Plymouth"], "correta": 0},
        {"pergunta": "Qual navio foi encontrado à deriva em 1872 sem sua tripulação?", "alternativas": ["Titanic", "Mary Celeste", "Santa Maria"], "correta": 1},
        {"pergunta": "Qual manuscrito misterioso é escrito em um sistema ainda não decifrado completamente?", "alternativas": ["Magna Carta", "Livro dos Mortos", "Manuscrito Voynich"], "correta": 2},
        {"pergunta": "Em qual país ficam as famosas Linhas de Nazca?", "alternativas": ["Peru", "Egito", "Índia"], "correta": 0},
        {"pergunta": "Qual região do Atlântico ficou famosa por histórias de desaparecimentos de navios e aviões?", "alternativas": ["Mar Vermelho", "Triângulo das Bermudas", "Mar Cáspio"], "correta": 1},
    ],

    "Lugares Abandonados Famosos": [
        {"pergunta": "Qual cidade ucraniana foi evacuada após o desastre nuclear de Chernobyl?", "alternativas": ["Kiev", "Odessa", "Pripyat"], "correta": 2},
        {"pergunta": "Qual ilha japonesa abandonada é conhecida como Hashima?", "alternativas": ["Ilha Battleship", "Ilha de Páscoa", "Ilha de Capri"], "correta": 0},
        {"pergunta": "Qual cidade fantasma da Namíbia foi abandonada após o declínio da mineração de diamantes?", "alternativas": ["Bodie", "Kolmanskop", "Craco"], "correta": 1},
        {"pergunta": "Qual cidade fantasma preservada fica no estado americano da Califórnia?", "alternativas": ["Detroit", "Salem", "Bodie"], "correta": 2},
        {"pergunta": "Qual cidade italiana abandonada foi construída sobre uma colina na região da Basilicata?", "alternativas": ["Craco", "Veneza", "Florença"], "correta": 0},
    ],

    "Fenômenos Estranhos da Natureza": [
        {"pergunta": "Como é chamado o fenômeno de luzes coloridas no céu das regiões polares?", "alternativas": ["Aurora boreal", "Tsunami", "Eclipse lunar"], "correta": 0},
        {"pergunta": "Qual fenômeno faz certos organismos marinhos emitirem luz?", "alternativas": ["Evaporação", "Bioluminescência", "Condensação"], "correta": 1},
        {"pergunta": "Como é chamada a ilusão óptica que pode parecer mostrar água no deserto?", "alternativas": ["Aurora", "Tornado", "Miragem"], "correta": 2},
        {"pergunta": "Qual fenômeno forma um círculo luminoso ao redor do Sol ou da Lua?", "alternativas": ["Halo", "Terremoto", "Maré vermelha"], "correta": 0},
        {"pergunta": "Qual fenômeno atmosférico raro é descrito como uma esfera luminosa durante tempestades?", "alternativas": ["Arco-íris", "Raio globular", "Nevasca"], "correta": 1},
    ],

    "Coisas que Quase Ninguém Sabe": [
        {"pergunta": "Botanicamente, qual destas frutas é considerada uma baga?", "alternativas": ["Morango", "Maçã", "Banana"], "correta": 2},
        {"pergunta": "Qual animal possui sangue azulado devido à hemocianina?", "alternativas": ["Polvo", "Cachorro", "Galinha"], "correta": 0},
        {"pergunta": "Em qual planeta um dia dura mais do que um ano?", "alternativas": ["Marte", "Vênus", "Júpiter"], "correta": 1},
        {"pergunta": "Qual animal é conhecido por produzir fezes em formato aproximadamente cúbico?", "alternativas": ["Girafa", "Coelho", "Wombat"], "correta": 2},
        {"pergunta": "Botanicamente, qual destas não é considerada uma baga verdadeira?", "alternativas": ["Morango", "Uva", "Banana"], "correta": 0},
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
