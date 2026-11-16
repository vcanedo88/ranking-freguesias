"""Gera g12.html (só os 52 interestaduais) a partir de g12-classicos.html (os 66), que é a página mestre.

Uso: edite g12-classicos.html e rode  python3 scripts/paginas_g12.py
As duas páginas usam o mesmo código; muda só a fonte de dados (data/g12_* x data/g12c_*) e os textos.
"""
import os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *x: os.path.join(RAIZ, *x)


def rep(s, a, b):
    assert a in s, "texto não encontrado: " + a[:80]
    return s.replace(a, b)


def nav(cur):
    abas = [("index.html", "Clássicos locais", "loc"), ("g12.html", "G12", "g12"), ("g12-classicos.html", "G12 com clássicos", "g12c")]
    return ('  <nav class="abas" aria-label="Rankings">'
            + "".join(f'<a href="{h}"' + (' aria-current="page"' if k == cur else "") + f">{t}</a>" for h, t, k in abas)
            + "</nav>\n")


def main():
    m = open(P("g12-classicos.html"), encoding="utf-8").read()
    navre = re.compile(r'  <nav class="abas".*?</nav>\n', re.S)
    g = navre.sub(nav("g12"), m, count=1)
    g = g.replace("'g12c_", "'g12_")
    g = rep(g, "<title>Ranking das Freguesias · G12 com clássicos</title>", "<title>Ranking das Freguesias · G12</title>")
    g = rep(g, "<em>Freguesias</em> · G12 com clássicos</h1>", "<em>Freguesias</em> · G12</h1>")
    g = rep(g, 'content="Índice de Freguesia dos 66 confrontos entre os 12 grandes', 'content="Índice de Freguesia dos 52 confrontos interestaduais entre os 12 grandes')
    g = rep(g, "dos 66 confrontos entre os 12 grandes, clássicos locais incluídos · jogos até", "dos 52 confrontos interestaduais entre os 12 grandes · jogos até")
    g = rep(g, "<h2>Ranking dos 66 confrontos</h2>", "<h2>Ranking dos 52 confrontos interestaduais</h2>")
    g = rep(g, "Todos os confrontos entre os 12 grandes, nos últimos 30 jogos oficiais de cada um.",
            'Os confrontos entre grandes de estados diferentes, nos últimos 30 jogos oficiais de cada um. Os clássicos locais ficam na aba "G12 com clássicos".')
    g, n = re.subn(r'      <div class="ctl"><span class="rot">Confrontos</span>.*?</div>\n      </div>\n', "", g, count=1, flags=re.S)
    assert n == 1
    g = rep(g, "Aproveitamento ponderado de cada clube contra os outros 11 grandes, somando os 11 confrontos (30 jogos de cada, mesmos pesos).",
            "Aproveitamento ponderado de cada clube contra os grandes de outros estados, somando os seus confrontos (mesmos pesos). "
            "Os clubes do Rio e de São Paulo têm 8 adversários (240 jogos no recorte de 30); os de Minas e do Rio Grande do Sul, 10 (300 jogos).")
    g = g.replace("índice contra os outros 11 · ", "índice contra os grandes de outros estados · ")
    g = rep(g, "O índice do clube soma os 11 confrontos de cada um.", "O índice do clube soma os seus confrontos contra os grandes de outros estados.")
    g = rep(g, "Os clássicos locais aqui usam 30 jogos; a aba dos clássicos mantém 50. Por isso o mesmo clássico pode ter índices diferentes nas duas abas. ",
            'Os clássicos locais ficam fora desta aba; na aba "G12 com clássicos" eles entram com 30 jogos (a aba dos clássicos locais mantém 50). ')
    g = rep(g, 'Nos interestaduais, 30 jogos cobrem 9 a 21 anos; nos clássicos locais, com os estaduais, de 5 a 10 anos (veja "Jogos desde").',
            'Nos interestaduais, 30 jogos cobrem de 9 a 21 anos (veja "Jogos desde"): os anos de Série B esticam a janela.')
    open(P("g12.html"), "w", encoding="utf-8").write(g)
    print("g12.html gerado a partir de g12-classicos.html")


if __name__ == "__main__":
    main()
