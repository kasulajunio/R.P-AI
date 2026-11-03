# R.P AI

**Ferramentas locais em Python, com CLI, dados persistentes e diagnostico.**

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue) ![MIT](https://img.shields.io/badge/license-MIT-green) ![Version 0.2.0](https://img.shields.io/badge/version-0.2.0-blue)

> Uso livre sob MIT, inclusive comercial, preservando copyright e licenca. Software experimental, sem garantias adicionais, nos limites da lei. Venv nao e sandbox de seguranca. [LICENSE](LICENSE) · [Termos](TERMS.md).

## Escopo real

Notas SQLite, tarefas locais, busca, edicao, exportacao JSON, backup SQLite verificado, SHA-256, boot nao interativo e CLI de operacoes. Sem dependencias obrigatorias de terceiros. Ainda **nao ha inferencia/chat com modelo, cofre criptografado, motor de jogos ou tuneis**. Pastas preparadas nao equivalem a esses produtos.

Repositorio: https://github.com/kasulajunio/R.P-AI. Publicacao solicitada, ainda sujeita a revisao de privacidade do historico e confirmacao de visibilidade. Clone e ZIP exigem permissao enquanto privado. Nenhum badge acima afirma testes aprovados.

## Inicio rapido

Requer Python 3.10+ e Git previamente instalados. No Android, use Termux; Windows, PowerShell; Linux/macOS, Terminal.

```sh
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python rpa.py install
python rpa.py run note-add "Minha nota" --body "Texto local"
python rpa.py run note-list
python rpa.py status
```

Windows: use py -3 em lugar de python. Linux/macOS: use python3 se necessario. Termux: instale explicitamente Python e Git com pkg install python git; essa etapa usa internet. O boot nao executa apt-get/pkg, nao usa sudo e nao modifica pacotes globais.

[Instrucoes completas por sistema e ZIP](docs/TERMINALS.md) · [CLI detalhada](docs/PRODUCT_CLI.md). Android/Termux nao foi testado em aparelho real.

## Comandos de produto

| Comando | Acao implementada |
| --- | --- |
| install | Prepara estrutura, SQLite e venv; executa o Python do venv para verificar |
| run | Executa notas, tarefas, exportacao, backups, hash e diagnostico |
| update | Git pull fast-forward na main limpa do origin oficial, sem reinstalar dependencias |
| status | Versao, Python, sistema, commit, saude SQLite, existencia do venv e ultimo log |
| autoload | Gera template opt-in; nao registra nem ativa servicos automaticamente |

```sh
python rpa.py install --no-venv
python rpa.py run task-add "Revisar projeto"
python rpa.py run task-list
python rpa.py run db-check
python rpa.py run db-backup backup-01.sqlite3
python rpa.py run note-export notas-01.json
python rpa.py update
python rpa.py --version
python rpa.py --help
```

O workspace padrao do rpa e .core na pasta atual. Para compartilhar dados entre rpa, boot.py e engine.py, use --root .core antes do comando. A CLI legada engine.py tem outro padrao por compatibilidade. Instalar o pacote registra o comando literal rpa: [guia](docs/PRODUCT_CLI.md). Nao existe publicacao no PyPI anunciada.

## Seguranca e limites

- Update e uma operacao de rede explicita. Recusa alteracoes locais, branch diferente de main, ZIP e origin nao oficial; nao faz reset nem apaga dados para atualizar.
- O boot usa biblioteca padrao, sem baixar modelos, ML ou pacotes do sistema. Se venv faltar, use --no-venv para as ferramentas locais.
- Logs JSON ficam em .core/logs; registram resultado, tempo e tipo de erro, nao argumentos ou texto das notas. A ajuda e erros de sintaxe nao geram log operacional.
- Status consulta SQLite em modo somente leitura. Ainda gera seu proprio log. Um banco corrompido retorna falha, nao sucesso.
- Banco, notas, exportacoes e backups nao sao criptografados. Nao publique workspace, tokens, modelos restritos ou dados pessoais.
- Venv separa dependencias, mas nao isola codigo hostil nem garante seguranca do sistema.
- run nao chama main.py ficticio nem anuncia IA em execucao. Nao ha modelo instalado, inferencia, servico permanente ou atualizacao automatica por padrao.

## Testes e qualidade

```sh
python -m compileall -q official_core rpa.py autoload.py boot.py engine.py tests scripts
python -m unittest discover -s tests -v
python scripts/smoke.py
python scripts/metrics.py
python scripts/check_secrets.py
```

A matriz CI configura Linux/Windows/macOS Intel e Python 3.10/3.12. Confira os checks da revisao exata no PR antes de tratar como aprovado. A triagem de padroes no historico nao substitui auditoria. Nao ha validacao em Android ou GPU real.

## Documentacao

[CLI](docs/PRODUCT_CLI.md) · [Terminais](docs/TERMINALS.md) · [Comandos locais](docs/COMMANDS.md) · [Arquitetura](docs/ARCHITECTURE.md) · [IA local](docs/AI_LOCAL.md) · [Riscos](docs/RISKS.md) · [Changelog](CHANGELOG.md) · [Seguranca](SECURITY.md).
