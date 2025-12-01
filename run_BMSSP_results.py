import csv
import glob
import os
import math
from collections import defaultdict
import heapq
import time  # <- novo

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

INF = float("inf")

# ======================================
#   Graph
# ======================================
class Graph:
    def __init__(self, n, edges):
        self.n = n
        self.adj = defaultdict(list)
        for (u, v, w) in edges:
            self.adj[u].append((v, float(w)))

    def out_edges(self, u):
        return self.adj[u]


# ======================================
#   NodeSet
# ======================================
class NodeSet(set):
    def has(self, v):
        return v in self


# ======================================
#   Median of three
# ======================================
def median_of_three_pivot(S: NodeSet, dhat: dict):
    nodes = list(S)
    if len(nodes) <= 3:
        return nodes[len(nodes)//2]

    sorted_nodes = sorted(nodes, key=lambda x: dhat[x])
    first = sorted_nodes[0]
    middle = sorted_nodes[len(sorted_nodes)//2]
    last = sorted_nodes[-1]

    cand = [first, middle, last]
    cand.sort(key=lambda x: dhat[x])
    return cand[1]


# ======================================
#   BucketQueue (Δ-stepping)
# ======================================
class BucketQueue:
    def __init__(self, delta):
        self.delta = float(delta)
        self.buckets = []
        self.min_idx = 0
        self.pos = {}

    def _ensure_bucket(self, idx):
        while idx >= len(self.buckets):
            self.buckets.append([])

    def insert(self, v, dist):
        idx = int(dist / self.delta)
        self._ensure_bucket(idx)
        self.buckets[idx].append(v)
        self.pos[v] = idx

    def extract_min(self):
        while self.min_idx < len(self.buckets) and not self.buckets[self.min_idx]:
            self.min_idx += 1

        if self.min_idx >= len(self.buckets):
            return None, False

        v = self.buckets[self.min_idx].pop(0)
        del self.pos[v]
        return v, True

    def decrease_key(self, v, new_dist):
        if v in self.pos:
            old = self.pos[v]
            bucket = self.buckets[old]
            for i in range(len(bucket)):
                if bucket[i] == v:
                    bucket.pop(i)
                    break
        self.insert(v, new_dist)


# ======================================
#   Δ-stepping bounded Dijkstra
# ======================================
def dijkstra_delta_stepping(S: NodeSet, B, G: Graph, dhat, delta):
    q = BucketQueue(delta)

    for s in S:
        q.insert(s, dhat[s])

    while True:
        u, ok = q.extract_min()
        if not ok:
            break

        du = dhat[u]
        if du >= B:
            continue

        for (v, w) in G.out_edges(u):
            nd = du + w
            if nd < dhat[v]:
                dhat[v] = nd
                if nd < B:
                    q.decrease_key(v, nd)


# ======================================
#   BMSSP core (recursivo)
# ======================================
def BMSSP_core(B, S: NodeSet, G: Graph, dhat):
    if len(S) == 0:
        return

    if len(S) == 1 or B <= 1.0:
        dijkstra_delta_stepping(S, B, G, dhat, delta=1.0)
        return

    pivot = median_of_three_pivot(S, dhat)
    bound = min(B, dhat[pivot])

    if abs(bound - B) < 1e-9:
        dijkstra_delta_stepping(S, B, G, dhat, delta=1.0)
        return

    dijkstra_delta_stepping(S, bound, G, dhat, delta=1.0)

    left = NodeSet()
    right = NodeSet()

    # separa por dhat
    for u in range(G.n):
        if dhat[u] < INF:
            if dhat[u] <= bound:
                left.add(u)
            elif dhat[u] < B:
                right.add(u)

    if 0 < len(left) < len(S):
        BMSSP_core(bound, left, G, dhat)

    if 0 < len(right) < len(S):
        BMSSP_core(B, right, G, dhat)


# ======================================
#   Novo BMSSP(n, edges, source)
# ======================================
def BMSSP(n, edges, source):
    G = Graph(n, edges)

    # inicializa distâncias
    dhat = {i: INF for i in range(n)}
    dhat[source] = 0.0

    # conjunto inicial contém apenas a fonte
    S = NodeSet([source])

    # busca ilimitada
    BMSSP_core(INF, S, G, dhat)

    return dhat

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
            dist = BMSSP(n, edges, source=0)
            dist = list(dist.values())
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
