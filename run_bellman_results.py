import csv
import glob
import os
import math
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

def bellman_ford(n, edges, source=0):
    """
    Implementação padrão do Bellman-Ford sem ciclos negativos
    (assumimos pesos não negativos para seu trabalho).
    Retorna lista dist[0..n-1] com as distâncias mínimas.
    """
    dist = [math.inf] * n
    dist[source] = 0.0

    # relaxa todas as arestas n-1 vezes
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break

    # se você quiser detectar ciclos negativos, faria mais uma passada aqui
    return dist

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
    folder_out = "results_bellman"

    pattern = os.path.join(folder_in, "*.csv")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"Nenhum CSV encontrado em '{folder_in}'.")
        return

    # novo: arquivo de tempos
    os.makedirs(folder_out, exist_ok=True)
    tempos_path = os.path.join(folder_out, "tempos_bellman.csv")
    with open(tempos_path, "w", newline="", encoding="utf-8") as f_tempos:
        wtempo = csv.writer(f_tempos)
        wtempo.writerow(["arquivo", "n_vertices", "n_arestas", "tempo_segundos"])

        print("Processando grafos com Bellman-Ford...")
        for path in files:
            n, edges = load_graph_from_csv(path)
            if n == 0:
                print(f"[AVISO] Grafo vazio em {os.path.basename(path)}, ignorando.")
                continue

            inicio = time.perf_counter()  # início da medição
            dist = bellman_ford(n, edges, source=0)
            fim = time.perf_counter()     # fim da medição
            elapsed = fim - inicio

            # nome de saída: results_bellman/bellman_<nome_do_arquivo_original>
            base_name = os.path.basename(path)
            out_name = f"bellman_{base_name}"
            out_path = os.path.join(folder_out, out_name)

            save_distances_to_csv(out_path, dist)

            # grava tempo no CSV de tempos
            wtempo.writerow([base_name, n, len(edges), f"{elapsed:.6f}"])

            print(f"  - {base_name}: {n} vértices, {len(edges)} arestas, tempo={elapsed:.6f}s -> salvo em {out_name}")

    print("Concluído. Resultados em:", folder_out)
    print("Tempos em:", tempos_path)

if __name__ == "__main__":
    main()
