# R.P AI

Ferramentas locais em Python de Fabio (`kasulajunio`): notas SQLite, busca, edicao, tarefas, exportacao JSON, backup verificavel, hash de arquivos e preparacao de ambiente virtual. Python 3.10+, sem dependencias obrigatorias alem da biblioteca padrao.

**Nao e uma suite de IA pronta.** Chat/inferencia com modelo, cofre criptografado, motor de jogos e tuneis ainda faltam. Os cinco diretorios sao pontos de expansao, nao implementacoes completas. Veja [funcoes reais](docs/COMMANDS.md) e [limites](docs/RISKS.md).

## Download e acesso

O titular solicitou publicacao. O acesso continua privado nesta revisao: o historico de commits inclui e-mail pessoal e requer decisao de privacidade antes da abertura. Nao compartilhe tokens para contornar isso. Depois da publicacao, clone HTTPS e Download ZIP nao exigirao conta. Este aviso deve ser atualizado junto da visibilidade.

## Qual terminal usar?

- Android: **Termux**, pelas fontes indicadas no [projeto oficial](https://github.com/termux/termux-app#installation).
- Windows: **PowerShell** ou **Windows Terminal**, com Python e Git instalados.
- Linux: aplicativo **Terminal**, com Python e Git.
- macOS: aplicativo **Terminal**, com Python 3.10+ e Git.

[Instalacao por sistema, ZIP e atualizacao](docs/TERMINALS.md). Android/Termux ainda nao foi validado em aparelho real.

### Android / Termux

Os primeiros comandos baixam pacotes e usam internet e armazenamento. Nao exigem root. O clone exige permissao enquanto o repositorio estiver privado.

```sh
pkg update
pkg install python git
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python engine.py --root .core init
python engine.py --root .core note-add "Minha nota" --body "Texto local"
python engine.py --root .core note-list
python engine.py --help
```

### Windows / PowerShell

Instale [Python](https://www.python.org/downloads/) e [Git](https://git-scm.com/downloads/). Nao precisa mudar ExecutionPolicy nem executar como administrador.

```powershell
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
py -3 engine.py --root .core init
py -3 engine.py --root .core note-add "Minha nota" --body "Texto local"
py -3 engine.py --help
```

### Linux / macOS

Com Python 3.10+ e Git instalados:

```sh
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python3 engine.py --root .core init
python3 engine.py --root .core doctor
python3 engine.py --help
```

## Fazer trabalho real

Troque python por python3 ou py -3 conforme seu sistema. Coloque --root antes do comando. Os IDs 1 sao exemplos de workspace novo; use os IDs retornados no seu caso.

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
```

Exportacoes e backups ficam dentro do workspace, sem sobrescrever arquivos existentes. **Nao sao criptografados.** Tarefas nao enviam notificacoes nem executam automacoes. Exclusao de nota exige --confirm e esta documentada em [todos os comandos](docs/COMMANDS.md).

## IA e demais modulos

```sh
python engine.py --root .core prepare ai --venv
python engine.py --root .core prepare db
python engine.py --root .core modules
```

Preparar IA cria o ambiente virtual quando solicitado e um teste que informa se PyTorch existe; nao instala PyTorch nem executa um modelo. Venv nao e sandbox de seguranca. Detectar nvidia-smi nao valida CUDA. Crypto_Vault nao e cofre e nao deve receber senhas, chaves ou seeds. Rede permanece desativada.

Nome anterior: Fabio Official Core. O pacote official_core, a classe MasterEngine e a pasta padrao Fabio_Official_Core foram preservados por compatibilidade. O comando opcional do pacote e rp-ai; executar diretamente os arquivos nao exige pip install.

## Testes

```sh
python -m unittest discover -s tests -v
python scripts/smoke.py
python scripts/metrics.py
python scripts/check_secrets.py
```

A CI compila, testa regressao, verifica historico por padroes de segredos e executa fluxo real offline, incluindo venv e SQLite, em Linux, Windows e macOS Intel com Python 3.10/3.12. Veja os checks do commit atual. Android e GPU reais nao foram validados. Busca por padroes nao substitui auditoria nem detecta todos os dados pessoais.

## Documentacao e direitos

[Guia](docs/USAGE.md) · [Comandos](docs/COMMANDS.md) · [Terminais](docs/TERMINALS.md) · [IA](docs/AI_LOCAL.md) · [Arquitetura](docs/ARCHITECTURE.md) · [Riscos](docs/RISKS.md) · [Status](docs/STATUS.md) · [Termos](TERMS.md) · [Seguranca](SECURITY.md) · [Licenca](LICENSE).

A licenca proprietaria atual foi preservada. Disponibilizar codigo nao equivale a escolher MIT ou autorizar redistribuicao comercial. Termos de publicacao devem ser alinhados antes da liberacao.
