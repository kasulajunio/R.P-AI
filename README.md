# R.P AI

> **Uso livre sob MIT**, inclusive comercial, com preservacao de copyright e licenca. Software experimental, sem garantias adicionais, nos limites da lei. O operador responde pelo proprio uso; este aviso nao elimina direitos irrenunciaveis nem cria aceite automatico. [Licenca](LICENSE) · [Termos e riscos](TERMS.md).

Ferramentas Python locais de Fabio: notas SQLite com leitura, busca, edicao e exclusao confirmada; tarefas persistentes; exportacao JSON; backup SQLite verificado; SHA-256 e boot nao interativo. Python 3.10+, biblioteca padrao, sem dependencias obrigatorias de terceiros.

**Nao e uma suite de IA concluida.** Ainda faltam inferencia/chat com modelo real, cofre criptografado, motor de jogos e tuneis. Preparar pastas nao implementa esses recursos.

## Qual terminal?

- Android: **Termux**, pelas fontes do [projeto oficial](https://github.com/termux/termux-app#installation). Nao precisa root.
- Windows: **PowerShell** ou **Windows Terminal**, com Python 3.10+ e Git instalados.
- Linux: **Terminal**, com Python e Git.
- macOS: **Terminal**, com Python 3.10+ e Git.

[Guia completo por sistema, ZIP e atualizacao](docs/TERMINALS.md). Android/Termux ainda nao foi validado em aparelho real.

## Download e boot

O titular solicitou publicacao. O repositorio permanece privado ate concluir a revisao de privacidade do historico; enquanto privado, clone e ZIP exigem permissao. A publicacao deve ser confirmada antes de anunciar download aberto.

### Android / Termux

Os dois primeiros comandos baixam Python e Git e usam internet e armazenamento. Depois o boot funciona sem rede e nao instala pacotes no sistema.

```sh
pkg update
pkg install python git
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python boot.py
python engine.py --root .core note-add "Minha nota" --body "Texto local"
python engine.py --root .core note-list
```

### Windows / PowerShell

Instale [Python](https://www.python.org/downloads/) e [Git](https://git-scm.com/downloads/), sem precisar alterar ExecutionPolicy.

```powershell
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
py -3 boot.py
py -3 engine.py --root .core note-list
```

### Linux / macOS

Com Python 3.10+ e Git instalados:

```sh
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python3 boot.py
python3 engine.py --root .core doctor
```

## O que o boot realmente faz

Detecta Linux, macOS, Windows, Android ou Termux sem despejar variaveis de ambiente. Exibe os termos, cria estrutura e banco locais, prepara o ambiente virtual de IA e executa o Python dele para verificar. Preserva arquivos existentes, retorna erro quando falha e nao pede confirmacoes interativas.

Nao usa apt no Windows, sudo, shell=True ou instalacao global. Python precisa estar instalado para executar qualquer script Python. Se venv/ensurepip estiver ausente, consulte as instrucoes do seu sistema ou use --without-venv para as ferramentas sem ML. Nao existe aceite automatico, servico de fundo ou inicializacao junto do aparelho. Venv nao e sandbox de seguranca.

```sh
python boot.py --root .core
python boot.py --root .core --without-venv
python boot.py --root .core --run note-list
python boot.py --help
```

## Comandos funcionais

Use python3 no Linux/macOS se necessario e py -3 no Windows. Os IDs 1 sao exemplos de workspace novo; use os IDs retornados no seu caso.

```sh
python engine.py --root .core note-get 1
python engine.py --root .core note-search "Texto"
python engine.py --root .core note-update 1 --title "Nota revisada"
python engine.py --root .core note-export notas.json
python engine.py --root .core task-add "Revisar projeto"
python engine.py --root .core task-list
python engine.py --root .core task-done 1
python engine.py --root .core task-done 1 --reopen
python engine.py --root .core db-check
python engine.py --root .core db-backup backup-01.sqlite3
python engine.py sha256 README.md
python engine.py --help
```

[Todos os comandos e limites](docs/COMMANDS.md). Exportacoes e backups ficam dentro do workspace e nao sobrescrevem arquivos existentes. Nao sao criptografados. Tarefas sao registros locais, sem lembretes ou automacoes. A busca usa substring SQLite, nao IA.

## IA local: estado honesto

O boot esta conectado a preparacao do modulo AI_Local_Engine, nao a um modelo. Nao baixa PyTorch ou pesos e nao executa inferencia. Baixar requer internet ou transferir um arquivo ja existente; depois, um runtime e modelo compativeis podem permitir inferencia offline, ainda nao implementada nesta versao. Venv separa dependencias, nao isola codigo hostil. Detectar nvidia-smi nao valida CUDA.

O pacote official_core, a classe MasterEngine e a pasta padrao Fabio_Official_Core foram preservados por compatibilidade. O boot usa .core por padrao; especifique --root .core na CLI para acessar os mesmos dados.

## Testes

```sh
python -m compileall -q official_core boot.py engine.py tests scripts
python -m unittest discover -s tests -v
python scripts/smoke.py
python scripts/metrics.py
```

CI: Linux, Windows e macOS Intel, Python 3.10/3.12. Valida regressao e fluxo offline com venv real, persistencia, backup, exportacao e comandos. Confirme o commit atual nos checks. Nao houve teste em aparelho Android ou GPU real.

## Documentacao

[Terminais](docs/TERMINALS.md) · [Comandos](docs/COMMANDS.md) · [Arquitetura](docs/ARCHITECTURE.md) · [IA](docs/AI_LOCAL.md) · [Riscos](docs/RISKS.md) · [Status](docs/STATUS.md) · [Seguranca](SECURITY.md).
