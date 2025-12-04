import os
import csv
import unicodedata

import osmnx as ox


def sanitize_name(name: str) -> str:
    """
    Converte o nome do bairro em algo seguro pra nome de arquivo:
    - minúsculas
    - sem acento
    - espaços viram "_"
    - remove caracteres estranhos
    """
    # remove acentos
    nfkd = unicodedata.normalize("NFKD", name)
    only_ascii = "".join(c for c in nfkd if not unicodedata.combining(c))
    # minúsculas e underscore
    cleaned = "".join(
        ch if ch.isalnum() else "_" for ch in only_ascii.lower()
    )
    # compacta underscores repetidos
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")


def graph_to_csv(G, path_out):
    """
    Converte o grafo OSMnx (MultiDiGraph) em CSV no formato:
    u,v,w
    0,1,23.5
    ...

    Onde:
    - vértices são renumerados para 0..n-1
    - w = comprimento da aresta em metros (atributo 'length')
    - em caso de múltiplas arestas u->v, fica só a menor
    """
    os.makedirs(os.path.dirname(path_out), exist_ok=True)

    nodes = list(G.nodes())
    id_map = {node_id: idx for idx, node_id in enumerate(nodes)}

    best = {}  # (iu, iv) -> menor peso
    for u, v, data in G.edges(data=True):
        iu = id_map[u]
        iv = id_map[v]
        length = data.get("length", None)
        if length is None:
            # se não tiver comprimento, ignora (pode ser estrada estranha)
            continue
        w = float(length)
        key = (iu, iv)
        if key not in best or w < best[key]:
            best[key] = w

    with open(path_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["u", "v", "w"])
        for (iu, iv), w in best.items():
            writer.writerow([iu, iv, f"{w:.3f}"])


def baixar_grafo_bairro(bairro: str, pasta_saida: str, network_type: str = "drive"):
    """
    Baixa o grafo viário do bairro via OSM (OSMnx) e salva em CSV.
    """
    query = f"{bairro}, Rio de Janeiro, Brazil"
    print(f"\n[INFO] Baixando grafo para: {query}")

    # baixa o grafo viário (apenas vias dirigíveis)
    G = ox.graph_from_place(query, network_type=network_type, simplify=True)

    n = len(G.nodes())
    m = len(G.edges())
    print(f"[INFO] Grafo de {bairro}: n={n}, m={m}")

    nome_arquivo = f"rio_{sanitize_name(bairro)}.csv"
    path_out = os.path.join(pasta_saida, nome_arquivo)

    graph_to_csv(G, path_out)
    print(f"[OK] CSV salvo em: {path_out}")


def main():
    # pasta onde vão ficar os CSV de grafos de bairros
    pasta_saida = "graphs"

    # LISTA DE BAIRROS DO RIO
    # comece com poucos pra testar; depois você pode aumentar essa lista.
    bairros_rio = [
        "Centro",
        "Botafogo",
        "Copacabana",
        "Ipanema",
        "Leblon",
        "Tijuca",
        "Madureira",
        "Campo Grande",
        "Bangu",
        "Barra da Tijuca",
        # aqui você pode adicionar todos os bairros que quiser
        # "Realengo",
        # "Jacarepaguá",
        # "Santa Teresa",
        # ...
    ]

    os.makedirs(pasta_saida, exist_ok=True)

    for bairro in bairros_rio:
        try:
            baixar_grafo_bairro(bairro, pasta_saida, network_type="drive")
        except Exception as e:
            print(f"[ERRO] Falha ao processar bairro '{bairro}': {e}")


if __name__ == "__main__":
    main()
