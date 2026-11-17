"""Regressoes do coletor com saidas sinteticas, sem executar benchmarks."""
import csv
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parent.parent
CAMPOS = ["versao", "escala", "n", "workers", "repeticao", "tempo_s",
          "pi_estimado", "dentro", "status_validacao"]


class Coletor(unittest.TestCase):
    def executar(self, finais="\n", modo="correto"):
        with tempfile.TemporaryDirectory(prefix="montecarlo-coletor-") as pasta:
            raiz = Path(pasta)
            for nome in ("scripts", "dados", "baseline"):
                (raiz / nome).mkdir()
            shutil.copyfile(RAIZ / "scripts/coletar.sh", raiz / "scripts/coletar.sh")
            texto = (RAIZ / "dados/gabarito.csv").read_text(encoding="utf-8")
            (raiz / "dados/gabarito.csv").write_bytes(texto.replace("\n", finais).encode())
            with (RAIZ / "dados/gabarito.csv").open(encoding="utf-8", newline="") as arquivo:
                gabarito = {r["n"]: r for r in csv.DictReader(arquivo)}
            programa = raiz / "baseline/02_montecarlo_pi"
            programa.write_text(
                "#!/usr/bin/env python3\n"
                "from pathlib import Path\nimport os, sys\n"
                f"gabarito = {gabarito!r}\n"
                "r = gabarito[sys.argv[1]]\n"
                "with Path('chamadas.txt').open('a') as f: f.write(sys.argv[1] + '\\n')\n"
                "modo = os.environ['COLETOR_TESTE_MODO']\n"
                "if modo == 'falha': sys.exit(42)\n"
                "n = '1' if modo == 'n_errado' else r['n']\n"
                "pi = '0.000000' if modo == 'pi_errado' else r['pi_estimado']\n"
                "dentro = '0' if modo == 'dentro_errado' else r['dentro']\n"
                "linha = f'n={n}  pi={pi}  dentro={dentro}  tempo=0.100000 s'\n"
                "print(linha)\n"
                "if modo == 'duplicado': print(linha)\n",
                encoding="utf-8",
            )
            programa.chmod(0o755)
            processo = subprocess.run(
                ["bash", "scripts/coletar.sh", "forte"], cwd=raiz,
                env=dict(os.environ, VERSOES="sequencial", OUT="dados/teste.csv",
                         COLETOR_TESTE_MODO=modo),
                capture_output=True, text=True, timeout=30,
            )
            with (raiz / "dados/teste.csv").open(newline="") as arquivo:
                leitor = csv.DictReader(arquivo)
                campos, linhas = leitor.fieldnames, list(leitor)
            chamadas = (raiz / "chamadas.txt").read_text().splitlines()
            return processo, campos, linhas, chamadas

    def conferir_valido(self, finais):
        processo, campos, linhas, chamadas = self.executar(finais)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertEqual(campos, CAMPOS)
        self.assertEqual(len(linhas), 9)
        self.assertTrue(all(r["status_validacao"] == "OK" for r in linhas))
        for n in ("10000000", "50000000", "100000000"):
            self.assertEqual(chamadas.count(n), 4)  # aquecimento + 3 repeticoes
            self.assertEqual([r["repeticao"] for r in linhas if r["n"] == n], ["1", "2", "3"])

    def test_gabarito_lf(self):
        self.conferir_valido("\n")

    def test_gabarito_crlf(self):
        self.conferir_valido("\r\n")

    def conferir_divergente(self, modo):
        processo, campos, linhas, _ = self.executar(modo=modo)
        self.assertNotEqual(processo.returncode, 0)
        self.assertEqual(campos, CAMPOS)
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["status_validacao"], "DIVERGENTE")
        self.assertIn("resultado divergente", processo.stderr)

    def test_n_incorreto(self):
        self.conferir_divergente("n_errado")

    def test_pi_incorreto(self):
        self.conferir_divergente("pi_errado")

    def test_dentro_incorreto(self):
        self.conferir_divergente("dentro_errado")

    def test_duas_linhas(self):
        processo, _, linhas, _ = self.executar(modo="duplicado")
        self.assertNotEqual(processo.returncode, 0)
        self.assertEqual(linhas, [])
        self.assertIn("exatamente 1 linha", processo.stderr)

    def test_falha_do_programa(self):
        processo, _, linhas, _ = self.executar(modo="falha")
        self.assertNotEqual(processo.returncode, 0)
        self.assertEqual(linhas, [])
        self.assertIn("falha ao executar", processo.stderr)


if __name__ == "__main__":
    unittest.main()
