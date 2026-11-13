"""Regressao: uma nova coleta nao pode sobrescrever registros existentes."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PASTA = Path(__file__).resolve().parent


class PreservacaoDosRegistros(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (PASTA / ".build").mkdir(exist_ok=True)

    def executar(self, saida):
        return subprocess.run(
            [sys.executable, str(PASTA / "verificar.py"),
             "--saida", str(saida), "--seq", str(PASTA / ".build/inexistente"),
             "--unit", str(PASTA / ".build" / ("testar_jump.exe" if sys.platform == "win32" else "testar_jump"))],
            capture_output=True, text=True, timeout=30,
        )

    def test_diretorio_existente_preserva_registros(self):
        temporarios = PASTA / ".build"
        with tempfile.TemporaryDirectory(dir=temporarios, prefix="preservacao-") as pasta:
            destino = Path(pasta)
            anteriores = {
                "ambiente.json": b'{"registro": "anterior"}\n',
                "corretude.csv": b"registro,anterior\n1,preservar\n",
                "medicoes.csv": b"tempo_s\n0.123456\n",
            }
            for nome, conteudo in anteriores.items():
                (destino / nome).write_bytes(conteudo)
            processo = self.executar(destino)
            for nome, conteudo in anteriores.items():
                self.assertEqual((destino / nome).read_bytes(), conteudo, nome)
            self.assertEqual(processo.returncode, 2, processo.stderr)
            self.assertEqual({p.name for p in destino.iterdir()}, set(anteriores))

    def test_arquivo_existente_nao_e_substituido(self):
        with tempfile.TemporaryDirectory(dir=PASTA / ".build", prefix="preservacao-") as pasta:
            destino = Path(pasta) / "arquivo.csv"
            destino.write_bytes(b"preservar\n")
            processo = self.executar(destino)
            self.assertEqual(processo.returncode, 2, processo.stderr)
            self.assertEqual(destino.read_bytes(), b"preservar\n")


if __name__ == "__main__":
    unittest.main()
