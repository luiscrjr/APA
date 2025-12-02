import math
import heapq
from collections import defaultdict, deque
import csv
import glob
import os
import time

# -----------------------------
# Types and constants
# -----------------------------
INF = float("inf")

# ----------------------------
# Util: construir adjacency
# ----------------------------
def build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for (u, v, w) in edges:
        adj[u].append((v, w))
    return adj

# ----------------------------
# Pivot: mediana de três
# ----------------------------
def median_of_three_pivot(S, dhat):
    nodes = list(S)
    m = len(nodes)
    if m == 0:
        raise ValueError("S vazio no pivot")
    if m <= 3:
        return nodes[m // 2]
    a = min(nodes, key=lambda x: dhat[x])
    b = nodes[m // 2]
    c = max(nodes, key=lambda x: dhat[x])
    da, db, dc = dhat[a], dhat[b], dhat[c]
    if da <= db <= dc:
        return b
    if db <= da <= dc:
        return a
    return c

# ----------------------------
# Dijkstra limitado por bound
# ----------------------------
def dijkstra_limited(S, B, adj, dhat):
    """
    Executa Dijkstra iniciando com os vértices de S (com distancias em dhat already set),
    mas **não relaxa** arestas que gerariam distância > B.
    Atualiza dhat in-place.
    """
    # heap de (dist, vertex)
    heap = []
    pushed = set()

    for v in S:
        # Só insere se dhat[v] for finito e <= B
        if dhat[v] < INF and dhat[v] <= B:
            heapq.heappush(heap, (dhat[v], v))
            pushed.add(v)

    while heap:
        d, u = heapq.heappop(heap)
        # se essa entrada está desatualizada, ignora
        if d != dhat[u]:
            continue
        # se o menor elemento excede B, podemos parar: heap ordenado por distância
        if d > B:
            break
        # relaxa vizinhos, mas respeita bound
        for (v, w) in adj[u]:
            nd = d + w
            if nd < dhat[v] and nd <= B:
                dhat[v] = nd
                heapq.heappush(heap, (nd, v))
    # retorna sem nada (dhat modificado in-place)

# ----------------------------
# BMSSP iterativo (pilha)
# ----------------------------
def bmssp(n, edges, source=0, B_initial=INF):
    """
    Implementação BMSSP usando Dijkstra limitado como subrotina.
    Retorna vetor de distâncias dhat[0..n-1].
    """
    adj = build_adj(n, edges)

    # inicializa dhat
    dhat = [INF] * n
    dhat[source] = 0.0

    # pilha de frames (B, S)
    stack = [(B_initial, {source})]

    while stack:
        B, S = stack.pop()
        if not S:
            continue

        # caso base: se S pequeno ou B pequeno, rodar dijkstra limitado direto
        if len(S) == 1 or B <= 1.0:
            dijkstra_limited(S, B, adj, dhat)
            continue

        # escolhe pivot
        pivot = median_of_three_pivot(S, dhat)
        bound = min(B, dhat[pivot])

        # se bound não reduz nada, faz dijkstra limitado com B
        if abs(bound - B) < 1e-12:
            dijkstra_limited(S, B, adj, dhat)
            continue

        # executa dijkstra limitado até 'bound'
        dijkstra_limited(S, bound, adj, dhat)

        # particiona S em left e right usando apenas os vértices de S
        left = set()
        right = set()
        for u in S:
            d = dhat[u]
            if d == INF:
                continue
            # inclui tolerância numérica pequena
            if d <= bound + 1e-12:
                left.add(u)
            elif d < B - 1e-12:
                right.add(u)

        # empilha subproblemas (apenas se reduzir o tamanho)
        # ordem de push: right depois left (porque stack LIFO) — não obrigatório
        if right and len(right) < len(S):
            stack.append((B, right))
        if left and len(left) < len(S):
            stack.append((bound, left))

    return dhat

def load_graph_from_csv(path):
    """
    Lê um grafo dirigido ponderado de um CSV no formato:
    u,v,w
    0,1,2.5
    1,2,1.0
    ...
    Retorna (n, edges), onde:
      n = número de vértices (0..n-1)
      edges = lista de tuplas (u, v, w)
    """
    edges = []
    vertices = set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # pula cabeçalho
        for row in reader:
            if not row or len(row) < 3:
                continue
            u = int(row[0])
            v = int(row[1])
            w = float(row[2])
            edges.append((u, v, w))
            vertices.add(u)
            vertices.add(v)

    if not vertices:
        return 0, []

    n = max(vertices) + 1
    return n, edges

def save_distances_to_csv(path_out, dist):
    """
    Salva as distâncias em um CSV com colunas:
    vertex,dist
    Se a distância for infinita (vértice inalcançável), grava "INF".
    """
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    with open(path_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["vertex", "dist"])
        for v, d in enumerate(dist):
            if d == math.inf:
                writer.writerow([v, "INF"])
            else:
                writer.writerow([v, f"{d:.6f}"])

def main():
    folder_in = "graphs"
    folder_out = "results_BMSSP"

    pattern = os.path.join(folder_in, "*.csv")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"Nenhum CSV encontrado em '{folder_in}'.")
        return

    # novo: arquivo de tempos
    os.makedirs(folder_out, exist_ok=True)
    tempos_path = os.path.join(folder_out, "tempos_BMSSP.csv")
    with open(tempos_path, "w", newline="", encoding="utf-8") as f_tempos:
        wtempo = csv.writer(f_tempos)
        wtempo.writerow(["arquivo", "n_vertices", "n_arestas", "tempo_segundos"])

        print("Processando grafos com BMSSP...")
        for path in files:
            n, edges = load_graph_from_csv(path)
            if n == 0:
                print(f"[AVISO] Grafo vazio em {os.path.basename(path)}, ignorando.")
                continue

            inicio = time.perf_counter()  # início da medição
            #dist = BMSSP(n, edges, source=0)
            
            dist = bmssp(n, edges)
            #dist = list(dist.values())
            fim = time.perf_counter()     # fim da medição
            elapsed = fim - inicio

            # nome de saída: results_BMSSP/BMSSP_<nome_original>
            base_name = os.path.basename(path)
            out_name = f"BMSSP_{base_name}"
            out_path = os.path.join(folder_out, out_name)

            save_distances_to_csv(out_path, dist)

            # grava tempo no CSV de tempos
            wtempo.writerow([base_name, n, len(edges), f"{elapsed:.6f}"])

            print(f"  - {base_name}: {n} vértices, {len(edges)} arestas, tempo={elapsed:.6f}s -> salvo em {out_name}")

    print("Concluído. Resultados em:", folder_out)
    print("Tempos em:", tempos_path)

if __name__ == "__main__":
    main()
