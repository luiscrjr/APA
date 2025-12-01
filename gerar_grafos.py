import csv
import os
import random

# garante reprodutibilidade dos pesos
random.seed(42)

def write_edges_to_csv(path, edges):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["u", "v", "w"])
        for u, v, w in edges:
            writer.writerow([u, v, w])

def generate_chain_graph(n, max_weight=10):
    """Grafo em cadeia: 0->1->2->...->(n-1)"""
    edges = []
    for u in range(n - 1):
        w = random.randint(1, max_weight)
        edges.append((u, u + 1, w))
    return edges

def generate_random_graph(n, m, max_weight=10):
    """Grafo aleatório dirigido sem laços e sem arestas duplicadas."""
    edges = set()
    # evita tentar criar mais arestas do que o possível
    max_possible = n * (n - 1)
    m = min(m, max_possible)

    while len(edges) < m:
        u = random.randrange(0, n)
        v = random.randrange(0, n)
        if u == v:
            continue
        if (u, v) in edges:
            continue
        w = random.randint(1, max_weight)
        edges.add((u, v, w))
    return list(edges)

def generate_grid_graph(rows, cols, max_weight=10, bidirectional=True):
    """
    Grelha (grid) rows x cols.
    Cada célula (r,c) vira um vértice id = r*cols + c.
    Arestas para direita e para baixo (e opcionalmente para cima/esquerda).
    """
    edges = []
    def vid(r, c):
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            u = vid(r, c)
            # para direita
            if c + 1 < cols:
                v = vid(r, c + 1)
                w = random.randint(1, max_weight)
                edges.append((u, v, w))
                if bidirectional:
                    edges.append((v, u, random.randint(1, max_weight)))
            # para baixo
            if r + 1 < rows:
                v = vid(r + 1, c)
                w = random.randint(1, max_weight)
                edges.append((u, v, w))
                if bidirectional:
                    edges.append((v, u, random.randint(1, max_weight)))
    return edges

def main():
    folder = "graphs"

    # 1) Grafos em cadeia (bons para "melhor caso" de Bellman-Ford com early-stop)
    chains = [
        ("chain_n10.csv", 10),
        ("chain_n50.csv", 50),
        ("chain_n100.csv", 100),
    ]
    for name, n in chains:
        edges = generate_chain_graph(n)
        write_edges_to_csv(os.path.join(folder, name), edges)

    # 2) Grafos esparsos (m ≈ 2n)
    sparse_configs = [
        ("sparse_n30_m60.csv", 30, 60),
        ("sparse_n50_m100.csv", 50, 100),
        ("sparse_n80_m160.csv", 80, 160),
    ]
    for name, n, m in sparse_configs:
        edges = generate_random_graph(n, m)
        write_edges_to_csv(os.path.join(folder, name), edges)

    # 3) Grafos densidade média (m um pouco maior)
    medium_configs = [
        ("medium_n30_m120.csv", 30, 120),
        ("medium_n60_m240.csv", 60, 240),
        ("medium_n100_m400.csv", 100, 400),
    ]
    for name, n, m in medium_configs:
        edges = generate_random_graph(n, m)
        write_edges_to_csv(os.path.join(folder, name), edges)

    # 4) Grafos densos (m bem grande)
    dense_configs = [
        ("dense_n20_m200.csv", 20, 200),
        ("dense_n40_m600.csv", 40, 600),
        ("dense_n60_m1200.csv", 60, 1200),
    ]
    for name, n, m in dense_configs:
        edges = generate_random_graph(n, m)
        write_edges_to_csv(os.path.join(folder, name), edges)

    # 5) Grafos em grade (grid), bons para testes de caminho "geográfico"
    grids = [
        ("grid_5x5.csv", 5, 5),
        ("grid_8x8.csv", 8, 8),
        ("grid_10x10.csv", 10, 10),
    ]
    for name, rows, cols in grids:
        edges = generate_grid_graph(rows, cols)
        write_edges_to_csv(os.path.join(folder, name), edges)

    print(f"Arquivos gerados na pasta '{folder}'.")

if __name__ == "__main__":
    main()
