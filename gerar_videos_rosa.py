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

    "Enfermagem": [
        {"pergunta": "Qual aparelho mede a saturação periférica de oxigênio?",
         "alternativas": ["Oxímetro de pulso", "Glicosímetro", "Otoscópio"], "correta": 0},
        {"pergunta": "Qual instrumento é usado para auscultar sons cardíacos e pulmonares?",
         "alternativas": ["Termômetro", "Estetoscópio", "Oftalmoscópio"], "correta": 1},
        {"pergunta": "Qual equipamento é usado para medir a pressão arterial?",
         "alternativas": ["Nebulizador", "Desfibrilador", "Esfigmomanômetro"], "correta": 2},
        {"pergunta": "Qual EPI é usado nas mãos para reduzir contato com material biológico?",
         "alternativas": ["Luvas", "Propé", "Touca"], "correta": 0},
        {"pergunta": "Como se chama o registro periódico de temperatura, pulso e pressão do paciente?",
         "alternativas": ["Anamnese cirúrgica", "Sinais vitais", "Mapa nutricional"], "correta": 1},
    ],

    "Medicina": [
        {"pergunta": "Qual especialidade médica cuida principalmente do coração?",
         "alternativas": ["Dermatologia", "Cardiologia", "Oftalmologia"], "correta": 1},
        {"pergunta": "Qual especialidade médica trata doenças da pele?",
         "alternativas": ["Neurologia", "Urologia", "Dermatologia"], "correta": 2},
        {"pergunta": "Qual órgão é responsável por bombear o sangue pelo corpo?",
         "alternativas": ["Coração", "Fígado", "Baço"], "correta": 0},
        {"pergunta": "Qual exame registra a atividade elétrica do coração?",
         "alternativas": ["Endoscopia", "Eletrocardiograma", "Ultrassom abdominal"], "correta": 1},
        {"pergunta": "Qual especialidade se dedica ao sistema nervoso?",
         "alternativas": ["Pediatria", "Nefrologia", "Neurologia"], "correta": 2},
    ],

    "Odontologia": [
        {"pergunta": "Qual é a camada mais externa e dura do dente?",
         "alternativas": ["Polpa", "Dentina pulpar", "Esmalte"], "correta": 2},
        {"pergunta": "Qual instrumento ajuda o dentista a visualizar áreas dentro da boca?",
         "alternativas": ["Espelho odontológico", "Estetoscópio", "Otoscópio"], "correta": 0},
        {"pergunta": "Qual tipo de dente é mais associado à trituração dos alimentos?",
         "alternativas": ["Incisivo", "Molar", "Canino"], "correta": 1},
        {"pergunta": "Qual material ajuda a limpar os espaços entre os dentes?",
         "alternativas": ["Algodão", "Gaze seca", "Fio dental"], "correta": 2},
        {"pergunta": "Como se chama a área da odontologia voltada ao alinhamento dos dentes?",
         "alternativas": ["Ortodontia", "Endodontia", "Periodontia"], "correta": 0},
    ],

    "Farmácia": [
        {"pergunta": "Qual profissional é responsável tecnicamente por atividades farmacêuticas em uma farmácia?",
         "alternativas": ["Farmacêutico", "Nutricionista", "Fisioterapeuta"], "correta": 0},
        {"pergunta": "O que indica a data de validade de um medicamento?",
         "alternativas": ["A data em que a embalagem foi aberta",
                          "Até quando o produto mantém validade nas condições indicadas",
                          "O dia em que o paciente deve iniciar o uso"], "correta": 1},
        {"pergunta": "Qual termo identifica a substância responsável pelo efeito do medicamento?",
         "alternativas": ["Excipiente principal", "Embalagem primária", "Princípio ativo"], "correta": 2},
        {"pergunta": "Qual forma farmacêutica é sólida e geralmente engolida inteira?",
         "alternativas": ["Comprimido", "Xarope", "Pomada"], "correta": 0},
        {"pergunta": "Onde devem ser seguidas as condições de armazenamento de um medicamento?",
         "alternativas": ["Sempre no congelador", "Na orientação da embalagem ou bula", "Sempre ao sol"], "correta": 1},
    ],

    "Psicologia": [
        {"pergunta": "Qual profissional é formado para atuar profissionalmente em psicologia?",
         "alternativas": ["Fonoaudiólogo", "Psicólogo", "Farmacêutico"], "correta": 1},
        {"pergunta": "Como se chama a capacidade de reconhecer e compreender sentimentos de outra pessoa?",
         "alternativas": ["Euforia", "Amnésia", "Empatia"], "correta": 2},
        {"pergunta": "Qual processo profissional envolve escuta e intervenções psicológicas estruturadas?",
         "alternativas": ["Psicoterapia", "Radioterapia", "Fisioterapia respiratória"], "correta": 0},
        {"pergunta": "Qual documento orienta deveres éticos da atuação profissional?",
         "alternativas": ["Manual de trânsito", "Código de Ética", "Código tributário"], "correta": 1},
        {"pergunta": "Qual habilidade é essencial em uma escuta psicológica profissional?",
         "alternativas": ["Interromper constantemente", "Ignorar o relato", "Escuta atenta"], "correta": 2},
    ],

    "Nutrição": [
        {"pergunta": "Qual nutriente é a principal fonte imediata de energia para o organismo?",
         "alternativas": ["Vitamina", "Mineral", "Carboidrato"], "correta": 2},
        {"pergunta": "Qual profissional elabora planos alimentares individualizados dentro de sua atuação?",
         "alternativas": ["Nutricionista", "Arquiteto", "Engenheiro civil"], "correta": 0},
        {"pergunta": "Qual grupo de nutrientes inclui vitaminas e minerais?",
         "alternativas": ["Macronutrientes energéticos", "Micronutrientes", "Apenas proteínas"], "correta": 1},
        {"pergunta": "Qual alimento é conhecido por ser fonte de fibras?",
         "alternativas": ["Açúcar refinado", "Óleo vegetal", "Aveia"], "correta": 2},
        {"pergunta": "Qual medida ajuda a avaliar a relação entre peso e altura em adultos?",
         "alternativas": ["IMC", "Frequência cardíaca", "Pressão intraocular"], "correta": 0},
    ],

    "Fisioterapia": [
        {"pergunta": "Qual instrumento pode medir a amplitude de movimento de uma articulação?",
         "alternativas": ["Goniômetro", "Oxímetro", "Balança"], "correta": 0},
        {"pergunta": "Qual área da fisioterapia trabalha com recuperação de movimentos e funções?",
         "alternativas": ["Contabilidade", "Reabilitação", "Cartografia"], "correta": 1},
        {"pergunta": "Qual recurso auxilia uma pessoa com dificuldade para caminhar?",
         "alternativas": ["Estetoscópio", "Microscópio", "Muleta"], "correta": 2},
        {"pergunta": "Como se chama o conjunto de exercícios usados para fins terapêuticos?",
         "alternativas": ["Cinesioterapia", "Farmacoterapia", "Radioterapia"], "correta": 0},
        {"pergunta": "Qual estrutura conecta músculo ao osso?",
         "alternativas": ["Ligamento", "Tendão", "Cartilagem articular"], "correta": 1},
    ],

    "Biomedicina": [
        {"pergunta": "Qual equipamento amplia estruturas muito pequenas para observação?",
         "alternativas": ["Esfigmomanômetro", "Microscópio", "Desfibrilador"], "correta": 1},
        {"pergunta": "Qual área laboratorial estuda células do sangue?",
         "alternativas": ["Astronomia", "Geologia", "Hematologia"], "correta": 2},
        {"pergunta": "Qual técnica é usada para amplificar segmentos de DNA?",
         "alternativas": ["PCR", "ECG", "EEG"], "correta": 0},
        {"pergunta": "Qual equipamento separa componentes de uma amostra por rotação?",
         "alternativas": ["Autoclave", "Centrífuga", "Balança analítica"], "correta": 1},
        {"pergunta": "Qual área estuda microrganismos como bactérias e fungos?",
         "alternativas": ["Ortopedia", "Cardiologia", "Microbiologia"], "correta": 2},
    ],

    "Técnico de Laboratório": [
        {"pergunta": "Qual instrumento é usado para medir pequenos volumes de líquidos com precisão?",
         "alternativas": ["Paquímetro", "Martelo", "Micropipeta"], "correta": 2},
        {"pergunta": "Qual equipamento separa componentes de uma amostra por força centrífuga?",
         "alternativas": ["Centrífuga", "Estufa", "Agitador magnético"], "correta": 0},
        {"pergunta": "O que deve ser conferido antes de processar uma amostra?",
         "alternativas": ["Cor da parede", "Identificação da amostra", "Marca da cadeira"], "correta": 1},
        {"pergunta": "Qual EPI ajuda a proteger as mãos durante manipulação de amostras?",
         "alternativas": ["Óculos de sol", "Boné", "Luvas"], "correta": 2},
        {"pergunta": "Qual equipamento esteriliza materiais usando vapor sob pressão?",
         "alternativas": ["Autoclave", "Refrigerador", "Microscópio"], "correta": 0},
    ],

    "Medicina Veterinária": [
        {"pergunta": "Qual profissional cuida da saúde dos animais?",
         "alternativas": ["Médico-veterinário", "Agrimensor", "Arquiteto"], "correta": 0},
        {"pergunta": "Qual instrumento é usado para auscultar coração e pulmões de animais?",
         "alternativas": ["Paquímetro", "Estetoscópio", "Trena"], "correta": 1},
        {"pergunta": "Como se chama uma doença que pode ser transmitida entre animais e seres humanos?",
         "alternativas": ["Miopia", "Escoliose", "Zoonose"], "correta": 2},
        {"pergunta": "Qual exame pode avaliar células do sangue de um animal?",
         "alternativas": ["Hemograma", "Planta baixa", "Balanço patrimonial"], "correta": 0},
        {"pergunta": "Qual área veterinária é voltada a procedimentos cirúrgicos?",
         "alternativas": ["Biblioteconomia", "Cirurgia veterinária", "Topografia"], "correta": 1},
    ],

    "Advocacia": [
        {"pergunta": "Qual profissional representa clientes em questões jurídicas?",
         "alternativas": ["Arquiteto", "Advogado", "Biólogo"], "correta": 1},
        {"pergunta": "Qual documento brasileiro ocupa o topo do ordenamento jurídico nacional?",
         "alternativas": ["Código de Trânsito", "Regimento de condomínio", "Constituição Federal"], "correta": 2},
        {"pergunta": "Como se chama o pedido formal apresentado ao Poder Judiciário?",
         "alternativas": ["Petição", "Receita", "Laudo fotográfico"], "correta": 0},
        {"pergunta": "Qual princípio garante que ninguém será considerado culpado antes do trânsito em julgado de sentença penal condenatória?",
         "alternativas": ["Livre concorrência", "Presunção de inocência", "Publicidade comercial"], "correta": 1},
        {"pergunta": "Qual profissional público presta assistência jurídica gratuita a quem atende aos critérios legais?",
         "alternativas": ["Auditor fiscal", "Perito contábil", "Defensor público"], "correta": 2},
    ],

    "Polícia": [
        {"pergunta": "Qual documento é comumente usado para registrar formalmente uma ocorrência policial?",
         "alternativas": ["Receita médica", "Nota fiscal", "Boletim de ocorrência"], "correta": 2},
        {"pergunta": "Em uma cena de crime, qual cuidado é essencial até a chegada da perícia?",
         "alternativas": ["Preservar o local", "Mover todos os objetos", "Limpar o ambiente"], "correta": 0},
        {"pergunta": "Qual equipamento de proteção é usado no tronco contra projéteis em determinadas operações?",
         "alternativas": ["Avental de cozinha", "Colete balístico", "Colete salva-vidas"], "correta": 1},
        {"pergunta": "Qual atividade busca coletar informações para esclarecer um crime?",
         "alternativas": ["Jardinagem", "Topografia", "Investigação"], "correta": 2},
        {"pergunta": "Qual número de emergência da Polícia Militar é usado no Brasil?",
         "alternativas": ["190", "192", "193"], "correta": 0},
    ],

    "Bombeiro": [
        {"pergunta": "Qual número de emergência do Corpo de Bombeiros é usado no Brasil?",
         "alternativas": ["193", "190", "192"], "correta": 0},
        {"pergunta": "Qual equipamento portátil é usado no combate inicial a pequenos incêndios?",
         "alternativas": ["Oxímetro", "Extintor", "Projetor"], "correta": 1},
        {"pergunta": "Como se chama a retirada organizada de pessoas de uma área de risco?",
         "alternativas": ["Catalogação", "Digitalização", "Evacuação"], "correta": 2},
        {"pergunta": "Qual EPI protege a cabeça do bombeiro em operações?",
         "alternativas": ["Capacete", "Touca cirúrgica", "Boné"], "correta": 0},
        {"pergunta": "Em incêndios, a fumaça quente tende a se deslocar principalmente para onde?",
         "alternativas": ["Para baixo", "Para cima", "Somente para os lados"], "correta": 1},
    ],

    "Perícia Criminal": [
        {"pergunta": "Qual vestígio pode ser comparado por padrões únicos deixados pelos dedos?",
         "alternativas": ["Cor da roupa", "Impressão digital", "Altura da pessoa"], "correta": 1},
        {"pergunta": "Qual molécula pode ser analisada para identificação genética?",
         "alternativas": ["Glicose", "Colesterol", "DNA"], "correta": 2},
        {"pergunta": "Por que o local de crime deve ser preservado?",
         "alternativas": ["Para evitar alteração ou contaminação de vestígios",
                          "Para facilitar a decoração",
                          "Para permitir circulação livre"], "correta": 0},
        {"pergunta": "Como se chama o registro da trajetória de coleta, guarda e transferência de um vestígio?",
         "alternativas": ["Fluxo de caixa", "Cadeia de custódia", "Plano de aula"], "correta": 1},
        {"pergunta": "Qual área pericial analisa armas de fogo e projéteis?",
         "alternativas": ["Botânica ornamental", "Meteorologia", "Balística forense"], "correta": 2},
    ],

    "Professor": [
        {"pergunta": "Qual documento organiza objetivos, conteúdos e atividades de uma aula?",
         "alternativas": ["Balanço patrimonial", "Boletim de ocorrência", "Plano de aula"], "correta": 2},
        {"pergunta": "Qual avaliação acompanha a aprendizagem ao longo do processo?",
         "alternativas": ["Avaliação formativa", "Inspeção veicular", "Auditoria contábil"], "correta": 0},
        {"pergunta": "Qual recurso apresenta visualmente conteúdos em uma aula?",
         "alternativas": ["Torquímetro", "Slide", "Estetoscópio"], "correta": 1},
        {"pergunta": "Como se chama a organização dos conteúdos ao longo de um período letivo?",
         "alternativas": ["Plano de voo", "Projeto estrutural", "Planejamento pedagógico"], "correta": 2},
        {"pergunta": "Qual atitude favorece a participação dos alunos?",
         "alternativas": ["Fazer perguntas e estimular diálogo", "Impedir qualquer pergunta", "Evitar feedback"], "correta": 0},
    ],

    "Bibliotecário": [
        {"pergunta": "Qual profissional organiza e gerencia acervos de bibliotecas?",
         "alternativas": ["Bibliotecário", "Farmacêutico", "Piloto"], "correta": 0},
        {"pergunta": "Qual código identifica internacionalmente uma edição de livro?",
         "alternativas": ["CPF", "ISBN", "CEP"], "correta": 1},
        {"pergunta": "Como se chama o processo de descrever e registrar dados de uma obra no acervo?",
         "alternativas": ["Sutura", "Soldagem", "Catalogação"], "correta": 2},
        {"pergunta": "Qual sistema é conhecido por classificar livros por áreas do conhecimento em números?",
         "alternativas": ["Classificação Decimal de Dewey", "Sistema Métrico Decimal", "Código Morse"], "correta": 0},
        {"pergunta": "Qual serviço ajuda o usuário a localizar informações e fontes?",
         "alternativas": ["Serviço de bordo", "Serviço de referência", "Serviço de guincho"], "correta": 1},
    ],

    "Jornalista": [
        {"pergunta": "Como se chama o primeiro parágrafo que resume as informações principais de uma notícia?",
         "alternativas": ["Rodapé", "Lead", "Legenda"], "correta": 1},
        {"pergunta": "Qual prática é essencial antes de publicar uma informação?",
         "alternativas": ["Inventar uma fonte", "Ignorar evidências", "Verificar as fontes"], "correta": 2},
        {"pergunta": "Qual técnica é usada para obter respostas diretamente de uma fonte?",
         "alternativas": ["Entrevista", "Soldagem", "Calibração"], "correta": 0},
        {"pergunta": "Qual elemento apresenta o título principal de uma matéria?",
         "alternativas": ["Balanço", "Manchete", "Receituário"], "correta": 1},
        {"pergunta": "No jornalismo, o que significa checagem de fatos?",
         "alternativas": ["Aumentar o tamanho da fonte", "Escolher a cor do texto",
                          "Verificar se afirmações são verdadeiras"], "correta": 2},
    ],

    "Fotógrafo": [
        {"pergunta": "Qual ajuste controla a quantidade de luz que entra pela abertura da lente?",
         "alternativas": ["Balanço de branco", "Foco automático", "Abertura do diafragma"], "correta": 2},
        {"pergunta": "Qual ajuste determina por quanto tempo o sensor fica exposto à luz?",
         "alternativas": ["Velocidade do obturador", "Saturação", "Nitidez"], "correta": 0},
        {"pergunta": "Qual parâmetro altera a sensibilidade do sensor à luz?",
         "alternativas": ["FPS", "ISO", "DPI"], "correta": 1},
        {"pergunta": "Qual equipamento ajuda a manter a câmera estável?",
         "alternativas": ["Estetoscópio", "Compasso", "Tripé"], "correta": 2},
        {"pergunta": "Qual formato de arquivo preserva mais dados brutos capturados pelo sensor?",
         "alternativas": ["RAW", "TXT", "MP3"], "correta": 0},
    ],

    "Cinegrafista": [
        {"pergunta": "Qual medida indica quantos quadros são gravados por segundo?",
         "alternativas": ["FPS", "DPI", "RPM"], "correta": 0},
        {"pergunta": "Qual ajuste corrige a aparência das cores conforme a iluminação?",
         "alternativas": ["Velocidade do som", "Balanço de branco", "Distância focal do microfone"], "correta": 1},
        {"pergunta": "Qual equipamento estabiliza a câmera durante movimentos?",
         "alternativas": ["Microscópio", "Torquímetro", "Gimbal"], "correta": 2},
        {"pergunta": "Qual plano mostra o rosto ou objeto bem de perto?",
         "alternativas": ["Close-up", "Plano geral", "Plano aéreo"], "correta": 0},
        {"pergunta": "Qual documento visual organiza cenas antes da gravação?",
         "alternativas": ["Balanço patrimonial", "Storyboard", "Prontuário"], "correta": 1},
    ],

    "Designer Gráfico": [
        {"pergunta": "Qual sistema de cores é mais usado em telas digitais?",
         "alternativas": ["CMYK", "RGB", "Pantone metálico apenas"], "correta": 1},
        {"pergunta": "Qual sistema de cores é tradicionalmente usado em impressão gráfica?",
         "alternativas": ["RGB", "HSV apenas", "CMYK"], "correta": 2},
        {"pergunta": "Qual tipo de imagem pode ser ampliado sem perder qualidade por ser baseado em formas matemáticas?",
         "alternativas": ["Vetorial", "Bitmap de baixa resolução", "JPEG comprimido"], "correta": 0},
        {"pergunta": "Como se chama o estudo e escolha de fontes em um projeto visual?",
         "alternativas": ["Topografia", "Tipografia", "Tomografia"], "correta": 1},
        {"pergunta": "Qual programa vetorial é amplamente associado à criação de ilustrações e logotipos?",
         "alternativas": ["Microsoft Excel", "VLC", "Adobe Illustrator"], "correta": 2},
    ],

    "Arquiteto": [
        {"pergunta": "Qual desenho mostra a distribuição dos ambientes vistos de cima?",
         "alternativas": ["Corte longitudinal apenas", "Perspectiva aérea", "Planta baixa"], "correta": 2},
        {"pergunta": "Qual representação mostra a aparência externa de uma edificação?",
         "alternativas": ["Fachada", "Planilha", "Legenda"], "correta": 0},
        {"pergunta": "O que indica a escala em um desenho arquitetônico?",
         "alternativas": ["A cor das paredes", "A relação entre medida no desenho e medida real",
                          "A quantidade de móveis"], "correta": 1},
        {"pergunta": "Qual desenho mostra a edificação como se fosse cortada verticalmente?",
         "alternativas": ["Planta de cobertura", "Memorial fotográfico", "Corte"], "correta": 2},
        {"pergunta": "Qual software é usado em projetos de arquitetura e desenho técnico?",
         "alternativas": ["AutoCAD", "Spotify", "WhatsApp"], "correta": 0},
    ],

    "Engenharia Civil": [
        {"pergunta": "Qual elemento transfere as cargas da construção para o solo?",
         "alternativas": ["Fundação", "Telha", "Rodapé"], "correta": 0},
        {"pergunta": "Qual material é formado, em geral, por cimento, agregados e água?",
         "alternativas": ["Vidro", "Concreto", "Madeira"], "correta": 1},
        {"pergunta": "Qual componente de aço é usado para reforçar estruturas de concreto armado?",
         "alternativas": ["Rejunte", "Piso vinílico", "Armadura"], "correta": 2},
        {"pergunta": "Qual instrumento verifica se uma superfície está horizontal ou vertical?",
         "alternativas": ["Nível", "Estetoscópio", "Microscópio"], "correta": 0},
        {"pergunta": "Qual elemento estrutural horizontal costuma vencer vãos e transmitir cargas?",
         "alternativas": ["Ralo", "Viga", "Batente"], "correta": 1},
    ],

    "Engenharia Elétrica": [
        {"pergunta": "Qual unidade mede tensão elétrica?",
         "alternativas": ["Ampere", "Volt", "Ohm"], "correta": 1},
        {"pergunta": "Qual unidade mede corrente elétrica?",
         "alternativas": ["Watt", "Tesla", "Ampere"], "correta": 2},
        {"pergunta": "Qual unidade mede resistência elétrica?",
         "alternativas": ["Ohm", "Volt", "Hertz"], "correta": 0},
        {"pergunta": "Qual dispositivo protege circuitos contra sobrecorrente?",
         "alternativas": ["Tomada", "Disjuntor", "Lâmpada"], "correta": 1},
        {"pergunta": "Qual equipamento pode elevar ou reduzir níveis de tensão em corrente alternada?",
         "alternativas": ["Resistor", "Interruptor", "Transformador"], "correta": 2},
    ],

    "Engenharia Mecânica": [
        {"pergunta": "Qual grandeza descreve o efeito de giro produzido por uma força?",
         "alternativas": ["Tensão elétrica", "Luminosidade", "Torque"], "correta": 2},
        {"pergunta": "Qual componente reduz atrito e apoia eixos giratórios?",
         "alternativas": ["Rolamento", "Fusível", "Capacitor"], "correta": 0},
        {"pergunta": "Qual área da física estuda calor, trabalho e energia em sistemas?",
         "alternativas": ["Óptica geométrica apenas", "Termodinâmica", "Botânica"], "correta": 1},
        {"pergunta": "Qual processo reduz atrito entre superfícies móveis usando óleo ou graxa?",
         "alternativas": ["Oxidação", "Galvanização", "Lubrificação"], "correta": 2},
        {"pergunta": "Qual ferramenta mede dimensões externas, internas e profundidade com precisão?",
         "alternativas": ["Paquímetro", "Martelo", "Serrote"], "correta": 0},
    ],

    "Programador": [
        {"pergunta": "Como se chama um erro em um programa de computador?",
         "alternativas": ["Bug", "Pixel", "Driver"], "correta": 0},
        {"pergunta": "Qual estrutura repete um bloco de código várias vezes?",
         "alternativas": ["Comentário", "Loop", "Variável constante"], "correta": 1},
        {"pergunta": "Qual nome se dá a um espaço usado para armazenar um valor em um programa?",
         "alternativas": ["Cursor", "Janela", "Variável"], "correta": 2},
        {"pergunta": "Qual sistema é muito usado para controle de versão de código?",
         "alternativas": ["Git", "PDF", "JPEG"], "correta": 0},
        {"pergunta": "Qual bloco de código reutilizável executa uma tarefa específica?",
         "alternativas": ["Pasta", "Função", "Fonte tipográfica"], "correta": 1},
    ],

    "Cibersegurança": [
        {"pergunta": "Como se chama o golpe que tenta enganar a vítima para obter senhas ou dados?",
         "alternativas": ["Backup", "Phishing", "Firewall"], "correta": 1},
        {"pergunta": "Qual recurso adiciona uma segunda etapa de verificação ao login?",
         "alternativas": ["Modo avião", "Compactação ZIP", "Autenticação em dois fatores"], "correta": 2},
        {"pergunta": "Qual tecnologia transforma dados para que só possam ser lidos com a chave adequada?",
         "alternativas": ["Criptografia", "Desfragmentação", "Impressão"], "correta": 0},
        {"pergunta": "Qual sistema ajuda a filtrar tráfego de rede com regras de segurança?",
         "alternativas": ["Planilha", "Firewall", "Editor de texto"], "correta": 1},
        {"pergunta": "Qual prática ajuda a recuperar dados após perda ou ataque?",
         "alternativas": ["Desligar atualizações", "Reutilizar a mesma senha", "Backup"], "correta": 2},
    ],

    "Contador": [
        {"pergunta": "Qual demonstrativo apresenta ativos, passivos e patrimônio líquido?",
         "alternativas": ["Plano de aula", "Mapa rodoviário", "Balanço patrimonial"], "correta": 2},
        {"pergunta": "Como se chama o recurso controlado pela empresa capaz de gerar benefícios econômicos?",
         "alternativas": ["Ativo", "Passivo", "Despesa"], "correta": 0},
        {"pergunta": "Como se chama uma obrigação financeira da empresa?",
         "alternativas": ["Receita", "Passivo", "Ativo"], "correta": 1},
        {"pergunta": "Qual documento registra uma venda de mercadoria ou prestação de serviço para fins fiscais?",
         "alternativas": ["Receita médica", "Passaporte", "Nota fiscal"], "correta": 2},
        {"pergunta": "Qual demonstrativo mostra receitas, custos e despesas para apurar o resultado do período?",
         "alternativas": ["DRE", "CNH", "RG"], "correta": 0},
    ],

    "Economista": [
        {"pergunta": "Como se chama o aumento generalizado e persistente dos preços?",
         "alternativas": ["Inflação", "Deflação", "Estagnação"], "correta": 0},
        {"pergunta": "Qual indicador mede o valor dos bens e serviços finais produzidos em um país em determinado período?",
         "alternativas": ["CPF", "PIB", "IPVA"], "correta": 1},
        {"pergunta": "Quando a quantidade ofertada aumenta e a demanda permanece igual, qual pressão tende a ocorrer sobre o preço?",
         "alternativas": ["Pressão de alta obrigatória", "Nenhuma relação possível", "Pressão de queda"], "correta": 2},
        {"pergunta": "Qual taxa representa o custo do dinheiro em empréstimos e aplicações?",
         "alternativas": ["Taxa de juros", "Taxa de alfabetização", "Taxa de natalidade"], "correta": 0},
        {"pergunta": "Como se chama a situação de pessoas que procuram trabalho e não encontram?",
         "alternativas": ["Inflação", "Desemprego", "Superávit"], "correta": 1},
    ],

    "Administrador": [
        {"pergunta": "Qual ferramenta analisa forças, fraquezas, oportunidades e ameaças?",
         "alternativas": ["ECG", "SWOT", "PCR"], "correta": 1},
        {"pergunta": "Qual sigla representa um indicador-chave de desempenho?",
         "alternativas": ["USB", "PDF", "KPI"], "correta": 2},
        {"pergunta": "Qual documento estima receitas e despesas para um período?",
         "alternativas": ["Orçamento", "Receita médica", "Mapa topográfico"], "correta": 0},
        {"pergunta": "Qual representação mostra cargos e relações hierárquicas em uma organização?",
         "alternativas": ["Cardiograma", "Organograma", "Fluxograma elétrico"], "correta": 1},
        {"pergunta": "Qual função administrativa envolve definir objetivos e caminhos para alcançá-los?",
         "alternativas": ["Improvisação", "Descarte", "Planejamento"], "correta": 2},
    ],

    "Marketing": [
        {"pergunta": "Como se chama o grupo de pessoas que uma campanha pretende atingir?",
         "alternativas": ["Estoque", "Fornecedor único", "Público-alvo"], "correta": 2},
        {"pergunta": "Qual sigla é usada para otimização de páginas para mecanismos de busca?",
         "alternativas": ["SEO", "CPU", "GPS"], "correta": 0},
        {"pergunta": "O que significa CTA em marketing digital?",
         "alternativas": ["Custo total anual", "Chamada para ação", "Cadastro técnico automático"], "correta": 1},
        {"pergunta": "Como se chama quando um visitante realiza a ação desejada, como comprar ou se cadastrar?",
         "alternativas": ["Compressão", "Formatação", "Conversão"], "correta": 2},
        {"pergunta": "Qual conceito reúne identidade, percepção e posicionamento de uma marca?",
         "alternativas": ["Branding", "Backup", "Benchmark elétrico"], "correta": 0},
    ],

    "Piloto de Avião": [
        {"pergunta": "Qual instrumento indica a altitude da aeronave?",
         "alternativas": ["Altímetro", "Velocímetro automotivo", "Odômetro"], "correta": 0},
        {"pergunta": "Como se chama o local de onde o piloto controla a aeronave?",
         "alternativas": ["Galley", "Cockpit", "Porão de carga"], "correta": 1},
        {"pergunta": "Qual órgão ou serviço orienta o tráfego de aeronaves durante o voo e em áreas controladas?",
         "alternativas": ["Serviço postal", "Recepção do hotel", "Controle de tráfego aéreo"], "correta": 2},
        {"pergunta": "Qual superfície é destinada principalmente à decolagem e pouso?",
         "alternativas": ["Pista", "Taxiway apenas", "Hangar"], "correta": 0},
        {"pergunta": "Qual documento contém o planejamento de rota, altitude e outras informações do voo?",
         "alternativas": ["Nota fiscal", "Plano de voo", "Prontuário"], "correta": 1},
    ],

    "Comissário de Bordo": [
        {"pergunta": "Qual é uma das principais responsabilidades do comissário de bordo?",
         "alternativas": ["Pilotar a aeronave sozinho", "Segurança dos passageiros",
                          "Fazer manutenção do motor em voo"], "correta": 1},
        {"pergunta": "Como se chama a área da aeronave onde são preparados itens de serviço de bordo?",
         "alternativas": ["Cockpit", "Trem de pouso", "Galley"], "correta": 2},
        {"pergunta": "O que os passageiros devem fazer quando o aviso de cintos está aceso?",
         "alternativas": ["Manter o cinto afivelado", "Ficar em pé no corredor", "Abrir as portas"], "correta": 0},
        {"pergunta": "Qual demonstração é feita antes da decolagem?",
         "alternativas": ["Demonstração de manutenção", "Demonstração de segurança",
                          "Demonstração de pilotagem"], "correta": 1},
        {"pergunta": "Qual equipamento é usado em uma evacuação sobre a água?",
         "alternativas": ["Capacete de obra", "Avental", "Colete salva-vidas"], "correta": 2},
    ],

    "Caminhoneiro": [
        {"pergunta": "Qual equipamento registra dados como velocidade e tempo de condução em veículos que o exigem?",
         "alternativas": ["Oxímetro", "Manômetro hospitalar", "Tacógrafo"], "correta": 2},
        {"pergunta": "Qual cuidado é essencial antes de iniciar uma viagem longa?",
         "alternativas": ["Verificar pneus, freios e iluminação", "Ignorar nível de óleo", "Desativar luzes"], "correta": 0},
        {"pergunta": "Como se chama a área que o motorista não consegue ver diretamente pelos espelhos?",
         "alternativas": ["Faixa neutra", "Ponto cego", "Eixo morto"], "correta": 1},
        {"pergunta": "Qual prática ajuda a evitar deslocamento da carga durante o transporte?",
         "alternativas": ["Deixar a carga solta", "Retirar todas as cintas", "Amarração adequada"], "correta": 2},
        {"pergunta": "Qual componente mantém contato direto do caminhão com a via?",
         "alternativas": ["Pneu", "Radiador", "Alternador"], "correta": 0},
    ],

    "Mecânico Automotivo": [
        {"pergunta": "Qual componente gera energia elétrica para os sistemas do carro enquanto o motor funciona?",
         "alternativas": ["Alternador", "Radiador", "Amortecedor"], "correta": 0},
        {"pergunta": "Qual componente inicia a combustão por centelha em motores a gasolina?",
         "alternativas": ["Pastilha de freio", "Vela de ignição", "Filtro de cabine"], "correta": 1},
        {"pergunta": "Qual fluido lubrifica partes internas do motor?",
         "alternativas": ["Água destilada apenas", "Fluido de freio", "Óleo do motor"], "correta": 2},
        {"pergunta": "Qual componente do sistema de freio pressiona o disco para reduzir a velocidade?",
         "alternativas": ["Pastilha de freio", "Correia dentada", "Bico injetor"], "correta": 0},
        {"pergunta": "Qual sistema ajuda a controlar a temperatura do motor?",
         "alternativas": ["Sistema de som", "Sistema de arrefecimento", "Sistema de iluminação"], "correta": 1},
    ],

    "Eletricista": [
        {"pergunta": "Qual instrumento pode medir tensão, corrente e resistência elétrica?",
         "alternativas": ["Termômetro", "Multímetro", "Microscópio"], "correta": 1},
        {"pergunta": "Qual dispositivo desliga o circuito em caso de sobrecorrente?",
         "alternativas": ["Interruptor simples", "Lâmpada", "Disjuntor"], "correta": 2},
        {"pergunta": "Qual condutor de proteção é associado ao aterramento?",
         "alternativas": ["Condutor de proteção", "Fase adicional", "Neutro decorativo"], "correta": 0},
        {"pergunta": "Qual unidade mede a tensão elétrica?",
         "alternativas": ["Ohm", "Volt", "Ampere"], "correta": 1},
        {"pergunta": "Qual EPI é apropriado para trabalhos elétricos quando especificado para a tensão e atividade?",
         "alternativas": ["Luva de cozinha", "Luva de lã comum", "Luva isolante adequada"], "correta": 2},
    ],

    "Marceneiro": [
        {"pergunta": "Qual ferramenta manual é usada para cortar madeira?",
         "alternativas": ["Estetoscópio", "Bisturi", "Serrote"], "correta": 2},
        {"pergunta": "Qual ferramenta verifica ângulos retos em peças de madeira?",
         "alternativas": ["Esquadro", "Termômetro", "Compasso de navegação"], "correta": 0},
        {"pergunta": "Qual material é usado para alisar superfícies de madeira?",
         "alternativas": ["Gaze", "Lixa", "Algodão"], "correta": 1},
        {"pergunta": "Qual ferramenta remove pequenas camadas de madeira para nivelar uma superfície?",
         "alternativas": ["Martelo", "Alicate", "Plaina"], "correta": 2},
        {"pergunta": "Qual produto é usado para unir peças de madeira em muitas montagens?",
         "alternativas": ["Cola para madeira", "Soro fisiológico", "Óleo de motor"], "correta": 0},
    ],

    "Pedreiro": [
        {"pergunta": "Qual ferramenta é usada para aplicar e espalhar argamassa?",
         "alternativas": ["Colher de pedreiro", "Estetoscópio", "Tesoura escolar"], "correta": 0},
        {"pergunta": "Qual instrumento verifica se uma parede está vertical?",
         "alternativas": ["Paquímetro", "Prumo", "Microscópio"], "correta": 1},
        {"pergunta": "Qual ferramenta ajuda a conferir se uma superfície está nivelada?",
         "alternativas": ["Otoscópio", "Oxímetro", "Nível"], "correta": 2},
        {"pergunta": "Qual mistura é usada para assentar tijolos e blocos?",
         "alternativas": ["Argamassa", "Gasolina", "Verniz"], "correta": 0},
        {"pergunta": "Qual material cerâmico é muito usado na construção de paredes?",
         "alternativas": ["Tecido", "Tijolo", "Vidro de relógio"], "correta": 1},
    ],

    "Chef de Cozinha": [
        {"pergunta": "Como se chama a organização prévia de ingredientes e utensílios antes do preparo?",
         "alternativas": ["À la carte", "Mise en place", "Flambagem"], "correta": 1},
        {"pergunta": "Qual técnica cozinha rapidamente o alimento em pouca gordura e alta temperatura?",
         "alternativas": ["Congelar", "Fermentar", "Saltear"], "correta": 2},
        {"pergunta": "Qual termo indica massa cozida firme ao morder?",
         "alternativas": ["Al dente", "Au gratin", "À milanesa"], "correta": 0},
        {"pergunta": "Qual utensílio é essencial para cortar e picar ingredientes?",
         "alternativas": ["Estetoscópio", "Faca de chef", "Chave inglesa"], "correta": 1},
        {"pergunta": "Qual técnica usa um recipiente aquecido indiretamente por água quente?",
         "alternativas": ["Fritura profunda", "Defumação", "Banho-maria"], "correta": 2},
    ],

    "Confeiteiro": [
        {"pergunta": "Qual mistura clássica leva chocolate e creme de leite?",
         "alternativas": ["Merengue italiano", "Caramelo seco", "Ganache"], "correta": 2},
        {"pergunta": "Qual utensílio é usado para confeitar bolos com cremes?",
         "alternativas": ["Saco de confeitar", "Alicate", "Serrote"], "correta": 0},
        {"pergunta": "Qual cobertura de açúcar pode ser aberta e usada para revestir bolos?",
         "alternativas": ["Molho pesto", "Pasta americana", "Maionese"], "correta": 1},
        {"pergunta": "Qual ingrediente é batido para formar chantilly tradicional?",
         "alternativas": ["Óleo de cozinha", "Caldo de carne", "Creme de leite fresco"], "correta": 2},
        {"pergunta": "Qual utensílio ajuda a medir ingredientes secos ou líquidos com precisão?",
         "alternativas": ["Balança culinária", "Bússola", "Voltímetro"], "correta": 0},
    ],

    "Cabeleireiro": [
        {"pergunta": "Qual ferramenta é usada para cortar fios de cabelo?",
         "alternativas": ["Tesoura", "Alicate de pressão", "Bisturi"], "correta": 0},
        {"pergunta": "Qual produto é usado após o shampoo para ajudar a condicionar os fios?",
         "alternativas": ["Desinfetante", "Condicionador", "Detergente de louça"], "correta": 1},
        {"pergunta": "Qual aparelho usa calor para alisar temporariamente os fios?",
         "alternativas": ["Liquidificador", "Furadeira", "Chapinha"], "correta": 2},
        {"pergunta": "Qual produto é usado em processos de descoloração capilar?",
         "alternativas": ["Pó descolorante", "Farinha de trigo", "Talco industrial"], "correta": 0},
        {"pergunta": "Qual ferramenta cria cachos com calor?",
         "alternativas": ["Martelo", "Modelador de cachos", "Paquímetro"], "correta": 1},
    ],

    "Manicure": [
        {"pergunta": "Qual ferramenta é usada para dar forma à borda das unhas?",
         "alternativas": ["Pincel de parede", "Lixa", "Chave de fenda"], "correta": 1},
        {"pergunta": "Qual produto costuma ser aplicado antes do esmalte colorido?",
         "alternativas": ["Removedor", "Álcool em gel", "Base"], "correta": 2},
        {"pergunta": "Qual produto é aplicado por cima do esmalte para acabamento e brilho?",
         "alternativas": ["Top coat", "Primer de parede", "Condicionador"], "correta": 0},
        {"pergunta": "Qual equipamento pode esterilizar instrumentos metálicos apropriados para esse processo?",
         "alternativas": ["Secador de cabelo", "Autoclave", "Liquidificador"], "correta": 1},
        {"pergunta": "Qual instrumento é usado para empurrar delicadamente a cutícula?",
         "alternativas": ["Serrote", "Pinça amperimétrica", "Espátula de cutícula"], "correta": 2},
    ],

    "Maquiador": [
        {"pergunta": "Qual produto é usado para uniformizar o tom da pele?",
         "alternativas": ["Máscara de cílios", "Batom", "Base"], "correta": 2},
        {"pergunta": "Qual produto ajuda a disfarçar olheiras e pequenas imperfeições?",
         "alternativas": ["Corretivo", "Delineador", "Blush"], "correta": 0},
        {"pergunta": "Qual produto colore as maçãs do rosto?",
         "alternativas": ["Primer", "Blush", "Fixador de cabelo"], "correta": 1},
        {"pergunta": "Qual produto é aplicado nos cílios para destacá-los?",
         "alternativas": ["Pó compacto", "Iluminador", "Máscara de cílios"], "correta": 2},
        {"pergunta": "Qual produto costuma preparar a pele antes da maquiagem?",
         "alternativas": ["Primer", "Esmalte", "Shampoo"], "correta": 0},
    ],

    "Costureiro": [
        {"pergunta": "Qual instrumento é usado para medir o corpo e tecidos?",
         "alternativas": ["Fita métrica", "Termômetro", "Nível"], "correta": 0},
        {"pergunta": "Qual ferramenta faz pontos unindo tecidos manualmente?",
         "alternativas": ["Serrote", "Agulha", "Paquímetro"], "correta": 1},
        {"pergunta": "Como se chama a dobra costurada na borda de uma peça?",
         "alternativas": ["Gola", "Punho", "Bainha"], "correta": 2},
        {"pergunta": "Qual item permite abrir e fechar partes de roupas e bolsas?",
         "alternativas": ["Zíper", "Lixa", "Broca"], "correta": 0},
        {"pergunta": "Qual máquina é usada para acabamento das bordas e evitar desfiamento?",
         "alternativas": ["Furadeira", "Overloque", "Impressora"], "correta": 1},
    ],

    "Agrônomo": [
        {"pergunta": "Qual medida indica se um solo é ácido, neutro ou alcalino?",
         "alternativas": ["RPM", "pH", "DPI"], "correta": 1},
        {"pergunta": "Como se chama o fornecimento controlado de água às culturas?",
         "alternativas": ["Ventilação", "Soldagem", "Irrigação"], "correta": 2},
        {"pergunta": "Qual prática alterna diferentes culturas na mesma área ao longo do tempo?",
         "alternativas": ["Rotação de culturas", "Monocultura contínua obrigatória", "Poda ornamental"], "correta": 0},
        {"pergunta": "O que representam as letras NPK em fertilizantes?",
         "alternativas": ["Níquel, prata e criptônio", "Nitrogênio, fósforo e potássio",
                          "Neônio, polônio e cálcio"], "correta": 1},
        {"pergunta": "Qual abordagem combina diferentes métodos para controlar pragas com menor dependência de um único método?",
         "alternativas": ["Irrigação por gotejamento", "Calagem", "Manejo integrado de pragas"], "correta": 2},
    ],

    "Astronauta": [
        {"pergunta": "Como se chama a condição de aparente ausência de peso vivida em órbita?",
         "alternativas": ["Magnetismo", "Pressurização", "Microgravidade"], "correta": 2},
        {"pergunta": "Qual traje protege o astronauta durante atividades fora da nave?",
         "alternativas": ["Traje espacial", "Roupa de mergulho comum", "Avental"], "correta": 0},
        {"pergunta": "Qual estação espacial é conhecida pela sigla ISS?",
         "alternativas": ["Instituto Solar de Satélites", "Estação Espacial Internacional",
                          "Sistema Interestelar Simulado"], "correta": 1},
        {"pergunta": "Como se chama uma atividade realizada por astronautas fora de uma espaçonave?",
         "alternativas": ["GPS", "ETA", "EVA"], "correta": 2},
        {"pergunta": "Qual veículo é usado para levar cargas ou pessoas da superfície rumo ao espaço?",
         "alternativas": ["Foguete", "Submarino", "Trem"], "correta": 0},
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
