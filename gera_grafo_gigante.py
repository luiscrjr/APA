import csv
import os
import random

def generate_big_grid(rows, cols, max_weight=10, bidirectional=False):
    """
    Gera um grafo em grade rows x cols.
    Cada vértice (r,c) vira um id = r*cols + c.
    Arestas para direita e para baixo (e opcionalmente para cima/esquerda).
    """
    edges = []
    def vid(r, c):
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            u = vid(r, c)
            # direita
            if c + 1 < cols:
                v = vid(r, c + 1)
                w = random.randint(1, max_weight)
                edges.append((u, v, w))
                if bidirectional:
                    edges.append((v, u, random.randint(1, max_weight)))
            # baixo
            if r + 1 < rows:
                v = vid(r + 1, c)
                w = random.randint(1, max_weight)
                edges.append((u, v, w))
                if bidirectional:
                    edges.append((v, u, random.randint(1, max_weight)))
    return edges

def save_graph_csv(path, edges):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["u", "v", "w"])
        for u, v, wt in edges:
            w.writerow([u, v, wt])

def main():
    # ajuste aqui o tamanho da grade:
    rows = 400
    cols = 400
    bidirectional = False  # pode testar True também, fica mais denso

    edges = generate_big_grid(rows, cols, max_weight=10, bidirectional=bidirectional)
    n = rows * cols
    m = len(edges)
    print(f"Grafo gerado: n={n}, m={m}")

    path = os.path.join("graphs", f"grid_{rows}x{cols}.csv")
    save_graph_csv(path, edges)
    print("Salvo em:", path)

if __name__ == "__main__":
    main()
