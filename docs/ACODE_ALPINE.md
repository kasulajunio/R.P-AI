# Acode com Alpine Linux

O log do titular mostra Alpine 3.21 aarch64, Python 3.12.16 e commit 8c378b7. Install e status funcionam. Forge exige rg/fd nativos quando o ambiente e identificado como Android. Variaveis herdadas como ANDROID_ROOT podem causar essa identificacao, sem provar ABI bionic. O workflow Acode Alpine ARM native recovery reproduz esse caminho com ANDROID_ROOT sintetico. Nao equivale a executar Acode ou validar o dispositivo.

## Recuperacao no commit original

Dentro da pasta que contem rpa.py, os comandos abaixo instalam pacotes nativos do Alpine e usam rede. O projeto nao os instala automaticamente. Nao apagar o workspace.

```sh
apk add --no-cache ripgrep fd
python rpa.py forge plan rg fd
```

O plano deve apresentar system_available para rg e fd, ambos downloaded=false. Nao remover ANDROID_ROOT para forcar downloads Linux nem substituir musl por glibc. O catalogo original nao oferece rg musl aarch64 aprovado, portanto alterar so a identificacao nao resolve todos os alvos.

## Outros pontos

- O commit declara dependencies=[] em pyproject.toml; nao existe requirements.txt. Os comandos de teste rodam diretamente do fonte.
- python3 fornece venv neste Alpine; nao instalar py3-venv.
- deactivate so existe como funcao depois de ativar um venv. Sua ausencia antes da ativacao nao e falha.
- O ZIP nao contem .git; commit=null nao significa download falho.
- Install prepara o nucleo. Nesse commit nao baixa nem executa modelo de IA.
- Nao publicar hosts.yml, tokens ou codigos de autenticacao. O token do log esta mascarado. Verificar isolamento antes de guardar credenciais persistentes em armazenamento compartilhado.

O sucesso anterior de Alpine 3.22 x86_64 em outra revisao nao prova compatibilidade desta combinacao. Conferir o resultado do workflow especifico.
