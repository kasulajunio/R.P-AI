# Comandos do R.P AI 0.2.0

Referência conferida no [commit 8c378b7](https://github.com/kasulajunio/R.P-AI/tree/8c378b7691979ca151c5a5aea0ed7ae010ba57ff), especialmente `official_core/console.py`, `launcher.py`, `cli.py`, `bootstrap.py` e `forge_command.py`. Revisões posteriores podem diferir.

**Não cole o guia inteiro para executar.** São exemplos independentes. Use a pasta que contém `rpa.py`, um Python 3.10 ou superior e um ambiente virtual ativo. `ID` é um marcador: substitua pelo número retornado ao criar ou listar a nota/tarefa. Nomes de arquivos e textos são exemplos.

## 1. Alpine no Acode

Os comandos `apk` usam rede e instalam pacotes no ambiente Alpine. Não são comandos do Termux nativo. Execute apenas se quiser instalar esses pacotes.

```sh
apk add --no-cache python3 git ripgrep fd
```

Para obter exatamente o código de referência em uma pasta nova, escolha um nome de destino que ainda não exista:

```sh
git clone --branch feat/official-foundation https://github.com/kasulajunio/R.P-AI.git R.P-AI-guia
cd R.P-AI-guia
git checkout --detach 8c378b7691979ca151c5a5aea0ed7ae010ba57ff
python3 -m venv .venv
. .venv/bin/activate
python rpa.py --help
```

Isso reproduz uma revisão antiga para referência; não inclui correções posteriores. Se já tem o projeto e o venv, não precisa baixar nem criar tudo novamente. Neste Alpine, `python3` fornece venv. Não é necessário instalar `py3-venv`. Esse commit declara `dependencies=[]` no `pyproject.toml` e não possui `requirements.txt`: não use `pip install -r requirements.txt`.

Para sair de um venv ativo: `deactivate`. Antes da ativação essa função não existe.

## 2. Ajuda, instalação e diagnóstico

```sh
python rpa.py --help
python rpa.py --version
python rpa.py install
python rpa.py install --no-venv
python rpa.py status
python rpa.py run
python rpa.py run doctor
python rpa.py run modules
python rpa.py run init
python -m official_core --help
```

- `install`: prepara o núcleo, banco e venv interno. Não instala pacotes do sistema nem modelos.
- `--no-venv`: prepara sem criar o venv interno.
- `status`: informa configuração, banco e estado do ambiente; pode escrever relatório local.
- `run` sem operação equivale a executar `doctor`.
- `modules`: lista os módulos. `init`: prepara a estrutura.
- `python -m official_core --help` mostra a ajuda dos comandos locais; para executar operações mantendo o workspace padrão do produto, prefira `python rpa.py run ...`.

Ajuda por operação, por exemplo:

```sh
python rpa.py run note-add --help
python rpa.py forge --help
python rpa.py autoload --help
```

## 3. Notas

```sh
python rpa.py run note-add "Minha nota" --body "Texto da nota"
python rpa.py run note-list --limit 20
python rpa.py run note-get ID
python rpa.py run note-search "palavra" --limit 20
python rpa.py run note-update ID --title "Novo título" --body "Novo texto"
python rpa.py run note-export "notas-01.json"
```

No update é possível fornecer só `--title` ou só `--body`. O export exige um nome `.json` novo; não sobrescreve arquivos existentes.

**Exclusão real: execute somente se quiser apagar a nota indicada.**

```sh
python rpa.py run note-delete ID --confirm
```

## 4. Tarefas locais

```sh
python rpa.py run task-add "Testar o projeto"
python rpa.py run task-list --state open --limit 20
python rpa.py run task-list --state done --limit 20
python rpa.py run task-list --state all --limit 50
python rpa.py run task-done ID
python rpa.py run task-done ID --reopen
```

`task-done` conclui; `--reopen` reabre. São registros locais, sem notificações automáticas.

## 5. Banco, backup e integridade

```sh
python rpa.py run db-check
python rpa.py run db-backup "backup-01.sqlite3"
python rpa.py run sha256 rpa.py
```

Backup exige um nome `.sqlite3` novo e não sobrescreve backups existentes. SHA-256 verifica integridade, não criptografa. O banco dessa revisão não é criptografado.

## 6. Preparação de módulos

```sh
python rpa.py run prepare ai
python rpa.py run prepare ai --venv
python rpa.py run prepare crypto
python rpa.py run prepare db
python rpa.py run prepare gaming
python rpa.py run prepare network
```

O argumento `module` também aceita `1`, `2`, `3`, `4` ou `5`; consulte `run modules` para os nomes. `--venv` pede a criação do ambiente de IA, sem bibliotecas de machine learning nem modelos. Preparar estruturas não implementa esses produtos.

## 7. Forge

Ferramentas do catálogo: `jq`, `rg` e `fd`. A disponibilidade depende de sistema, arquitetura, libc e ferramentas nativas já instaladas. Não aceita URLs arbitrárias nem repositórios como nome de ferramenta.

Planos, sem downloads:

```sh
python rpa.py forge plan rg fd
python rpa.py forge plan jq
python rpa.py forge plan jq rg fd
```

Instalações explícitas, autorizando rede quando houver um arquivo aprovado para o alvo:

```sh
python rpa.py forge install rg fd --allow-network
python rpa.py forge install jq --allow-network
```

Diretório opcional e independente de `--root`, exemplo de plano:

```sh
python rpa.py forge plan rg fd --directory "$HOME/.rpa/bin"
```

Não há garantia de arquivo aprovado para todo alvo. Em Android/Termux, ferramentas nativas são exigidas nesses caminhos; o Forge não instala APKs nem acessa a Play Store.

### Recuperação testada para o Alpine no Acode

Com o commit original e o ambiente identificado como Android, instale as ferramentas nativas do Alpine, se ainda não estiverem instaladas:

```sh
apk add --no-cache ripgrep fd
python rpa.py forge plan rg fd
command -v rg fd
rg --version
fd --version
```

O resultado esperado para ambos é `system_available` e `downloaded=false`. Nesse caso não precisa de `forge install`. Os executáveis do apk ficam em `/usr/bin`, não em `~/.rpa/bin`. Não remova variáveis do Android para forçar downloads Linux incompatíveis, nem apague o workspace para corrigir isso.

[Evidência: execução 41733667718](https://github.com/kasulajunio/R.P-AI/actions/runs/41733667718). O teste reproduziu o bloqueio antes dos pacotes e confirmou a recuperação depois, em Alpine 3.21, ARM aarch64 e Python 3.12.16, com `ANDROID_ROOT` sintético. Não equivale a executar o Acode real nem a validar todo o Android.

## 8. Update

```sh
python rpa.py --source . update
```

**Usa rede.** Só aceita o clone oficial, na branch `main`, limpo e com atualização fast-forward. Não atualiza uma pasta extraída de ZIP nem a revisão destacada do passo de reprodução deste guia. Na situação atual, a main contém a documentação de entrada, enquanto o código está na branch de desenvolvimento: não troque de branch esperando que update instale o código.

## 9. Modelos de inicialização

```sh
python rpa.py autoload --platform linux
python rpa.py autoload --platform termux
python rpa.py autoload --platform windows
```

São modelos gerados; não ativam serviços. Escolha só a plataforma pretendida. A opção `--auto-update` autoriza atualização pela rede quando o modelo for executado, por exemplo:

```sh
python rpa.py autoload --platform linux --auto-update
```

Gerar um modelo não comprova inicialização automática no Acode ou em outro dispositivo.

## 10. Entradas alternativas

```sh
python boot.py --help
python boot.py
python boot.py --no-venv
python boot.py --without-venv
python boot.py --run note-list
python autoload.py --help
python autoload.py
python autoload.py --no-venv
```

`boot.py` prepara o núcleo e faz diagnóstico; `--run` encaminha uma operação local depois da preparação. `--without-venv` é alias de `--no-venv`. `autoload.py` faz uma execução de instalação e checagem do banco, não um loop em segundo plano.

`autoload.py --auto-update` tenta atualizar pela rede antes de instalar e checar; tem as mesmas restrições de clone e branch do update. Não é adequado à cópia destacada ou ZIP deste guia.

## 11. Opções de caminhos

No produto, o padrão de dados e relatórios é `.core`. Defina `--root` antes da operação, não depois de `run`:

```sh
python rpa.py --root .core status
python rpa.py --root .core run note-list
python rpa.py --source . status
python boot.py --root .core --run note-list
python autoload.py --root .core --source . --no-venv
```

`--source` identifica a raiz do código para status, update e modelos. `--root` identifica dados; não muda o diretório dos binários do Forge.

## Limites desta revisão

- Não há comando `chat` ou `ask`, inferência ou modelo instalado pelo R.P AI.
- Venv não é sandbox; um diretório chamado Crypto_Vault não é um cofre criptografado.
- Um ZIP não contém `.git`: `commit=null` no status não prova falha do download.
- Não compartilhe tokens, códigos de autenticação ou `hosts.yml`.
- Conferir comandos no código não significa que todos foram executados em todos os sistemas. O teste Alpine citado valida apenas o cenário descrito.
