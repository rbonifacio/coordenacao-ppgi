"""
  Este script coleta dados de citações / métricas dos
  professores do PPGI. Antes de usar, verificar se a lista
  de professores em 'authors' está correta.

  Requisitos: instalar a biblioteca scholarly.

  Execução: python3 scholar.py
"""
from scholarly import scholarly

authors = [
    "Alba Cristina Magalhaes Alves de Melo",
    "Aletéia Araújo",
    "André Costa Drummond",
    "B. macchiavello",
    "Celia Ghedini Ralha",
    "Cláudia Nalon",
    "Dibio L Borges",
    "Edna Dias Canedo",
    "Eduardo Alchieri",
    "Eduardo Peixoto",
    "Flavio de Barros Vidal",
    "Genaína Nunes Rodrigues",
    "George Teodoro",
    "Geraldo P. Rocha Filho",
    "Jacir Luiz Bordim",
    "Li Weigang",
    "Luís Paulo Faina Garcia",
    "Marcelo Marotta",
    "Maria Emilia Walter",
    "Maristela Holanda",
    "Mauricio Ayala Rincon",
    "Mylene Farias",
    "Pedro Garcia Freitas",
    "Priscila Solis",
    "Ricardo Jacobi",
    "Teofilo Emidio de Campos",
    "Thiago Paulo Faleiros",
    "Vander Alves",
    "Vinícius R. P. Borges",
    "Ricardo de Queiroz",
    "Rodrigo Bonifacio",
]

total = 0
totalH = 0
for a in authors:
    search_query = scholarly.search_author(a)
    author = next(search_query)
    res = scholarly.fill(author, sections=["basics", "indices"])

    print(f"{a}, {res['citedby']}, {res['hindex']}")
    total = total + res["citedby"]
    totalH = total + res["hindex"]

print(total)
print(totalH / len(authors))
