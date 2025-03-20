import csv
from unidecode import unidecode

periodicos = "data/2025/qualis_artigos_todos.csv"
discentes = "data/2025/discentes-ativos.csv"

pesos = { 'A1' : 1.0, 'A2' : 0.875, 'A3' : 0.750, 'A4' : 0.625, 'B1' : 0.5, 'B2' : 0.2, 'B3' : 0.1, 'B4' : 0.05 } 

artigos = set()

resumo = [("2013-2016", (0,0,0,0,0,0,0)), ("2017-2020",  (0,0,0,0,0,0,0)), ("2021-2024",  (0,0,0,0,0,0,0))]

anoBase = 2013

docentes = [24, 30, 31]

totalAno = [0, 0, 0, 0]


STOPWORDS = {"da", "de", "do", "das", "dos", "e"}

def normalize_name(name):
    """Removes accents and converts to lowercase"""
    return unidecode(name).lower()

def split_name(name):
    """Splits a full name into individual words, ignoring stopwords"""
    words = set(normalize_name(name).split())
    return words - STOPWORDS  # Remove stopwords

def is_match(name1, name2, min_matches=2):
    """Checks if two names match based on common words"""
    words1 = split_name(name1)
    words2 = split_name(name2)
    common = words1 & words2  # Find common words
    return len(common) >= min_matches

discentes_ativos = []

with open(discentes) as csvfile:
    heading = next(csvfile)
    data = csv.reader(csvfile, delimiter=",", quotechar="\"")
    for row in data:
        (mat, nome, nivel) = row
        discentes_ativos.append(nome)

def verifica_autor_discente(lista_de_autores):
    for autor in lista_de_autores:
        for discente in discentes_ativos:
            print(f"comparing {autor} with {discente}")
            if is_match(discente, autor):
                print(discente)
                return True
    return False
        
with open(periodicos) as csvfile:
    heading = next(csvfile) 
    data = csv.reader(csvfile, delimiter=',', quotechar="\"")
    for row in data:
        (titulo, ano, veiculo, acronimo,tipo,autores,issn,qualis) = row
        lista_de_autores = autores.split(";")

        autor_discente = verifica_autor_discente(lista_de_autores)

        if qualis in pesos:
            artigos.add((titulo, ano, autor_discente, qualis))

for artigo in artigos:
    (titulo, ano, autor_discente, qualis) = artigo

    if int(ano) > 2024 or qualis not in pesos:
        continue
    
    idx = int((int(ano) - anoBase) / 4)

    
    (q, (totalR, totalG, ir, ig,a1,a2, ds)) = resumo[idx]
    
    if qualis.startswith("A"):
       totalR = totalR + 1
       ir = ir + pesos[qualis]
       if qualis == "A1":
           a1 = a1+1
       elif qualis == "A2":
           a2 = a2+1
       else:
           pass
    else:
        totalG = totalG + 1
        ig = ig + pesos[qualis]

    if autor_discente:
        ds = ds + 1
        
    resumo[idx] = (q, (totalR, totalG, ir, ig, a1, a2, ds))    

    if int(ano) >= 2021:
        totalAno[int(ano)-2021] = totalAno[int(ano)-2021] + 1 

print(resumo)


for idx in range(len(resumo)):
    (q, (totalR, totalG, ir, ig, a1, a2, ds)) = resumo[idx]
    print(f"{q} IR = {ir / docentes[idx]}, IG = {(ig + ir) / docentes[idx]}") 

    
print(totalAno)


w1 = "WALTER LUCAS MONTEIRO DE MENDONCA"
w2 = "Walter Lucas Monteiro de Mendonça"
print(f"Matching {w1}, {w2}, {is_match(w1, w2)}")
