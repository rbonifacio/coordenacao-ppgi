import csv
from unidecode import unidecode

periodicos_csv = "data/2025/qualis_artigos_todos.csv"
#periodicos_csv = "data/2025/qualis_artigos_publicados_periodicos.csv"

discentes_csv = "data/2025/discentes-ativos.csv"
egressos_csv = "data/2025/egressos.csv"

pesos = { 'A1' : 1.0, 'A2' : 0.875, 'A3' : 0.750, 'A4' : 0.625, 'B1' : 0.5, 'B2' : 0.2, 'B3' : 0.1, 'B4' : 0.05 } 

artigos = set()

resumo = [("2013-2016", (0,0,0,0,0,0,0)), ("2017-2020",  (0,0,0,0,0,0,0)), ("2021-2024",  (0,0,0,0,0,0,0))]

anoBase = 2013

docentes = [24, 30, 31]

totalAno = [0, 0, 0, 0]


STOPWORDS = {"da", "de", "do", "das", "dos", "e", "jr", "junior", "filho", "neto"}

def normalize_name(name):
    """Removes accents and converts to lowercase"""
    return unidecode(name).lower().replace(".", "")

def split_name(name):
    """Splits a full name into individual words, ignoring stopwords"""
    words = normalize_name(name).split()
    for s in STOPWORDS:
        if s in words:
            words.remove(s)
    return words

def is_match(name1, name2, min_matches=2):
    """Checks if two names match based on common words"""
    words1 = split_name(name1)
    words2 = split_name(name2)
    # if words1[0] == words2[0] and words1[-1] == words2[-1]:
    #     return True
    words1 = set(words1)
    words2 = set(words2)
    matches = len(words1 & words2)
    return matches >= min_matches and len(words1) - matches <= 1 and matches and len(words2) - matches <= 1

discentes = set()

with open(discentes_csv) as csvfile:
    heading = next(csvfile)
    data = csv.reader(csvfile, delimiter=",", quotechar="\"")
    for row in data:
        (mat, nome, nivel) = row
        if nivel == "Doutorado":
            discentes.add(nome)

with open(egressos_csv) as csvfile:
    heading = next(csvfile)
    data = csv.reader(csvfile, delimiter=",", quotechar="\"")
    for row in data:
        (titulo,egresso,tipo,data,quadrienio) = row
        if tipo == "TESE":
            discentes.add(egresso)

discentes_pub = set()

def verifica_autor_discente(title, lista_de_autores):
    for autor in lista_de_autores:
        for discente in discentes:
            n1 = normalize_name(autor).split()[0]
            n2 = normalize_name(discente).split()[0]
            if n1 == n2 and is_match(discente, autor):
                discentes_pub.add(discente)
                return True
    return False
        
with open(periodicos_csv) as csvfile:
    heading = next(csvfile) 
    data = csv.reader(csvfile, delimiter=',', quotechar="\"")
    for row in data:
        (titulo, ano, veiculo, acronimo,tipo,autores,issn,qualis) = row
        # (titulo, ano, veiculo, acronimo,autores,issn,qualis) = row
       
        lista_de_autores = autores.split(";")

        autor_discente = verifica_autor_discente(titulo, lista_de_autores)

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


    if (qualis.startswith("A")) and autor_discente:
        ds = ds+1
        
    resumo[idx] = (q, (totalR, totalG, ir, ig, a1, a2, ds))    

    if int(ano) >= 2021:
        totalAno[int(ano)-2021] = totalAno[int(ano)-2021] + 1 

print(resumo)


for idx in range(len(resumo)):
    (q, (totalR, totalG, ir, ig, a1, a2, ds)) = resumo[idx]
    print(f"{q} IR = {ir / docentes[idx]}, IG = {(ig + ir) / docentes[idx]}") 

    
print(totalAno)

print(discentes_pub)

print(len(discentes_pub))
