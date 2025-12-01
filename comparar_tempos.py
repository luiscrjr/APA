import csv

def carregar_tempos(path):
    """
    Lê um arquivo de tempos no formato:
    arquivo,n_vertices,n_arestas,tempo_segundos
    e retorna um dicionário:
    { "nome_arquivo.csv": (n_vertices, n_arestas, tempo) }
    """
    dados = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # pula cabeçalho
        for row in reader:
            if not row or len(row) < 4:
                continue
            arquivo = row[0]
            n = int(row[1])
            m = int(row[2])
            t = float(row[3])
            dados[arquivo] = (n, m, t)
    return dados

def main():
    # caminhos dos arquivos de tempos gerados pelos outros scripts
    path_bf = "results_bellman/tempos_bellman.csv"
    path_dj = "results_dijkstra/tempos_dijkstra.csv"
    path_bm = "results_BMSSP/tempos_BMSSP.csv"  # <- NOVO

    tempos_bf = carregar_tempos(path_bf)
    tempos_dj = carregar_tempos(path_dj)
    try:
        tempos_bm = carregar_tempos(path_bm)
    except FileNotFoundError:
        # se o arquivo ainda não existir, segue sem BMSSP
        tempos_bm = {}

    # arquivo de saída com comparação
    out_path = "comparacao_tempos.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow([
            "arquivo",
            "n_vertices",
            "n_arestas",
            "tempo_bellman",
            "tempo_dijkstra",
            "razao_bf_sobre_dj",
            "tempo_bmssp",             # <- NOVO
            "razao_bf_sobre_bmssp",    # <- NOVO
            "razao_bmssp_sobre_dj"     # <- NOVO
        ])

        # percorre só arquivos que existem nos dois (BF e Dijkstra)
        for arquivo in sorted(tempos_bf.keys()):
            if arquivo not in tempos_dj:
                continue

            n_bf, m_bf, t_bf = tempos_bf[arquivo]
            n_dj, m_dj, t_dj = tempos_dj[arquivo]

            # por segurança, assume n/m iguais (deveriam ser)
            n = n_bf
            m = m_bf

            # razão de tempo: quanto Bellman-Ford é mais lento que Dijkstra
            if t_dj > 0:
                razao_bf_dj = t_bf / t_dj
            else:
                razao_bf_dj = 0.0

            # ---- NOVO: BMSSP ----
            t_bm = None
            if arquivo in tempos_bm:
                n_bm, m_bm, t_bm = tempos_bm[arquivo]
            # se não tiver BMSSP para esse arquivo, deixamos vazio nas colunas novas

            if t_bm is not None:
                t_bm_str = f"{t_bm:.6f}"
                if t_bm > 0:
                    razao_bf_bm = t_bf / t_bm
                else:
                    razao_bf_bm = 0.0

                if t_dj > 0:
                    razao_bm_dj = t_bm / t_dj
                else:
                    razao_bm_dj = 0.0

                razao_bf_bm_str = f"{razao_bf_bm:.2f}"
                razao_bm_dj_str = f"{razao_bm_dj:.2f}"
            else:
                # sem dado de BMSSP para esse grafo
                t_bm_str = ""
                razao_bf_bm_str = ""
                razao_bm_dj_str = ""

            writer.writerow([
                arquivo,
                n,
                m,
                f"{t_bf:.6f}",
                f"{t_dj:.6f}",
                f"{razao_bf_dj:.2f}",
                t_bm_str,
                razao_bf_bm_str,
                razao_bm_dj_str
            ])

    print(f"Arquivo de comparação gerado: {out_path}")

if __name__ == "__main__":
    main()
