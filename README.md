# R.P AI

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue) ![License MIT](https://img.shields.io/badge/License-MIT-green) ![Version 0.2.0](https://img.shields.io/badge/Version-0.2.0-orange)
[![CI](https://github.com/kasulajunio/R.P-AI/actions/workflows/ci.yml/badge.svg?branch=feat%2Fofficial-foundation)](https://github.com/kasulajunio/R.P-AI/actions)

Ferramentas locais de Fabio: notas e tarefas em SQLite, busca, edicao, exportacao, backup verificavel, hash e preparacao de ambientes. Python 3.10+, sem dependencias obrigatorias alem da biblioteca padrao. **Licenca MIT**, conforme pedido do titular.

Versao 0.2.0 em validacao. Nao e produto completo de IA nem certificacao empresarial: inferencia com modelo, cofre criptografado, motor de jogos e tuneis ainda nao existem. [O que funciona](docs/COMMANDS.md) · [Riscos](docs/RISKS.md).

## Acesso e download

O titular solicitou tornar o projeto publico. Nesta revisao o acesso permanece privado enquanto a exposicao do e-mail pessoal no historico e avaliada. A licenca MIT foi alterada independentemente da visibilidade. Depois da abertura, clone HTTPS e Download ZIP dispensam conta. Nunca use token publicado em comando ou issue.

## Inicio rapido

Com Python 3.10+ e Git, em Linux/macOS/Termux use python3 ou python; no Windows use py -3.

```sh
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python rpa.py install
python rpa.py run note-add "Primeira nota" --body "Texto local"
python rpa.py run note-list
python rpa.py run task-add "Revisar projeto"
python rpa.py run task-list
python rpa.py run db-check
```

O install detecta o sistema, cria o workspace .core, abre o banco e cria/verifica um venv **sem pip**, downloads, pacotes ML ou alteracoes no sistema. Falha retorna codigo diferente de zero e nao anuncia sucesso. O nucleo pode funcionar sem venv: `python rpa.py install --no-venv`. Nao execute como administrador/root.

## Comando unico rpa

Opcional: instale a CLI em um venv de desenvolvimento separado. A criacao com pip e a instalacao do pacote podem usar internet para obter ferramentas de build; nao fazem parte do boot offline.

```sh
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/rpa install
.venv/bin/rpa run note-list
.venv/bin/rpa update
```

No Windows use `.venv\Scripts\python.exe -m pip install -e .` e `.venv\Scripts\rpa.exe`. Com o venv no PATH, use apenas **rpa install**, **rpa run**, **rpa update**. Alternativa sem pip: `python rpa.py`. Nenhum pacote foi publicado no PyPI.

Update usa rede e faz somente fast-forward em main limpa, com origin oficial. Recusa alteracoes locais, outras branches e repositorios; nao resolve conflitos, executa reset, reinstala dependencias ou apaga dados. ZIP nao usa update. Reveja changelog antes de atualizar.

## Terminais por sistema

- **Android:** Termux, obtido conforme [fontes oficiais](https://github.com/termux/termux-app#installation). Execute `pkg update`, `pkg install python git` e os comandos de clone acima. Esses dois primeiros comandos usam internet. Termux real ainda nao foi validado.
- **Windows:** PowerShell/Windows Terminal com [Python](https://www.python.org/downloads/) e [Git](https://git-scm.com/downloads/). Substitua python por `py -3`. Nao precisa alterar ExecutionPolicy para executar arquivos Python.
- **Linux/macOS:** Terminal com Python 3.10+ e Git. Prefira `python3`. Instale ferramentas do sistema de forma explicita conforme sua distribuicao; o boot nao chama apt/brew.

[Guia completo de instalacao, ZIP e atualizacao](docs/TERMINALS.md).

## Notas, tarefas e backup

```sh
python rpa.py run note-search "Texto"
python rpa.py run note-get 1
python rpa.py run note-update 1 --title "Revisada"
python rpa.py run note-export notas.json
python rpa.py run task-done 1
python rpa.py run task-done 1 --reopen
python rpa.py run db-backup backup-01.sqlite3
python rpa.py run sha256 README.md
```

IDs sao exemplos. Exportacoes e backups ficam dentro do workspace, sem sobrescrita. Notas, tarefas, logs e backups **nao sao criptografados**. Tarefas nao enviam notificacoes. Exclusao exige --confirm. [Referencia completa](docs/COMMANDS.md).

## Logs e relatorios

Cada operacao da CLI rpa gera .core/logs/ID.json com comando, resultado, duracao, UTC e tipo de falha. Nao registra corpo de notas, argumentos, credenciais ou saida bruta de Git. Relatorios nao saem do dispositivo. Permissoes POSIX restritas quando disponiveis; no Windows dependem das ACLs locais. Sem rotacao automatica nesta versao, revise arquivos antigos manualmente.

## Boot e autoload opcionais

```sh
python boot.py
python rpa.py autoload --platform termux
python rpa.py autoload --platform linux
```

Autoload gera template **sem ativa-lo**. Inicializacao padrao faz preparacao local e verifica SQLite; nao mantem processo em loop. Para autorizar Git/rede a cada startup, gere com --auto-update. Nao e atualizacao em tempo real. Linux/systemd, Termux:Boot e Windows/PowerShell possuem instrucoes em [AUTOLOAD.md](docs/AUTOLOAD.md); macOS ainda nao tem template. Nada e ativado automaticamente no celular do titular.

## Arquitetura e limites

`official_core/engine.py`: caminhos e estrutura; `services.py`: SQLite/servicos; `bootstrap.py`: ambiente offline; `launcher.py`: comandos rpa e relatorios; `cli.py`: ferramentas de dados; `autoload.py`: startup opt-in. Pastas modulares sao pontos de expansao. Venv nao e sandbox. Detectar nvidia-smi nao valida CUDA. Crypto_Vault nao e cofre. Nenhum modelo e baixado.

Nomes anteriores official_core, MasterEngine, Fabio_Official_Core, rp-ai e fabio-core foram preservados por compatibilidade. .core e o workspace padrao da nova CLI rpa; a CLI antiga continua usando Fabio_Official_Core. Use --root antes do comando para selecionar o mesmo workspace.

## Qualidade

```sh
python -m compileall -q official_core engine.py rpa.py boot.py autoload.py tests scripts
python -m unittest discover -s tests -v
python scripts/smoke.py
python scripts/metrics.py
python scripts/check_secrets.py
```

CI em Linux, Windows e macOS Intel com Python 3.10/3.12. Consulte checks do commit atual: um badge verde anterior nao prova a revisao seguinte. Android/GPU e ativacao real de startup ainda nao validados. O checker examina padroes conhecidos no historico, nao e auditoria nem detector completo de dados pessoais.

## Documentacao e contribuicao

[Changelog](CHANGELOG.md) · [Guia](docs/USAGE.md) · [Comandos](docs/COMMANDS.md) · [Autoload](docs/AUTOLOAD.md) · [Arquitetura](docs/ARCHITECTURE.md) · [IA](docs/AI_LOCAL.md) · [Status](docs/STATUS.md) · [Seguranca](SECURITY.md) · [Contribuir](CONTRIBUTING.md) · [Termos](TERMS.md) · [MIT](LICENSE).

Contribuicoes por PR com testes, limites claros e sem dados privados. Codigo e documentacao sob MIT; bibliotecas/modelos de terceiros conservam licencas proprias. Sem garantia nos limites da lei. Aviso no boot nao e aceite juridico automatico.
