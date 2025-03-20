import csv

periodicos = "data/2025/qualis_artigos_publicados_periodicos.csv"

pesos = { 'A1' : 1.0, 'A2' : 0.875, 'A3' : 0.750, 'A4' : 0.625, 'B1' : 0.5, 'B2' : 0.2, 'B3' : 0.1, 'B4' : 0.05 } 

artigos = set()

resumo = [("2013-2016", (0,0,0,0,0,0)), ("2017-2020",  (0,0,0,0,0,0)), ("2021-2024",  (0,0,0,0,0,0))]

anoBase = 2013

docentes = [24, 30, 31]

totalAno = [0, 0, 0, 0]

with open(periodicos) as csvfile:
    heading = next(csvfile) 
    data = csv.reader(csvfile, delimiter=',', quotechar="\"")
    for row in data:
        (titulo, ano, veiculo, acronimo,autores,issn,qualis) = row
        if qualis in pesos:
            artigos.add((titulo, ano, qualis))


for artigo in artigos:
    (titulo, ano, qualis) = artigo

    if int(ano) > 2024 or qualis not in pesos:
        continue
    
    idx = int((int(ano) - anoBase) / 4)

    
    (q, (totalR, totalG, ir, ig,a1,a2)) = resumo[idx]
    
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

    resumo[idx] = (q, (totalR, totalG, ir, ig, a1, a2))    

    if int(ano) >= 2021:
        totalAno[int(ano)-2021] = totalAno[int(ano)-2021] + 1 
print(resumo)


for idx in range(len(resumo)):
    (q, (totalR, totalG, ir, ig, a1, a2)) = resumo[idx]
    print(f"{q} IR = {ir / docentes[idx]}, IG = {(ig + ir) / docentes[idx]}") 
    
print(totalAno)
