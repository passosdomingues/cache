import matplotlib.pyplot as plt

# arquivos de entrada
arquivos = {
    "Ocupação 0.80": "ocupacao_800.dat",
    "Ocupação 0.90": "ocupacao_900.dat",
    "Ocupação 0.95": "ocupacao_950.dat",
    "Ocupação 0.999": "ocupacao_999.dat",
}

for titulo, nome_arquivo in arquivos.items():
    tempos = []
    EN = []
    EW = []

    # leitura manual
    with open(nome_arquivo, "r") as f:
        for linha in f:
            partes = linha.strip().split()
            if len(partes) != 3:
                continue
            t, en, ew = map(float, partes)
            tempos.append(t)
            EN.append(en)
            EW.append(ew)

    # plota
    plt.figure()
    plt.plot(tempos, EN, label="E[N]")
    plt.plot(tempos, EW, label="E[W]")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Valor")
    plt.title(titulo)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

