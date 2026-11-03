# Qual terminal usar?

Terminal e um aplicativo onde voce digita comandos. Nao e um servidor especial nem uma conta do R.P AI. O codigo roda na sua propria maquina. Nunca informe senhas a outra pessoa para instalar.

## Android: Termux

Use a distribuicao oficial do Termux indicada em https://termux.dev/ e consulte https://github.com/termux/termux-app#installation para instalacao suportada. Nao misture aplicativos/complementos de fontes diferentes. Nao precisa root.

No Termux, os comandos abaixo instalam Python e Git: isso baixa pacotes e usa armazenamento e internet. Depois a instalacao do projeto nao baixa modelos de IA.

```sh
pkg update
pkg install python git
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python engine.py --root .core init
python engine.py --root .core note-add "Primeira nota" --body "Meu texto"
python engine.py --root .core note-list
python engine.py --help
```

Enquanto o repositorio estiver privado, o clone acima so funciona com permissao do titular; apos a publicacao, nao precisa conta GitHub. Android/Termux ainda nao foi validado em aparelho real. O nucleo nao exige PyTorch ou GPU.

## Windows: PowerShell ou Windows Terminal

Instale Python 3.10+ de https://www.python.org/downloads/ e Git de https://git-scm.com/downloads. Abra PowerShell ou Windows Terminal.

```powershell
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
py -3 engine.py --root .core init
py -3 engine.py --root .core note-add "Primeira nota" --body "Meu texto"
py -3 engine.py --root .core note-list
py -3 engine.py --help
```

Nao e necessario ativar scripts PowerShell, mudar ExecutionPolicy ou executar como administrador. Caso py nao exista mas python esteja configurado, substitua py -3 por python.

## Linux: Terminal

Python 3.10+ e Git precisam estar instalados pelo gerenciador da sua distribuicao.

```sh
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python3 engine.py --root .core init
python3 engine.py --root .core doctor
python3 engine.py --help
```

## macOS: Terminal

Use Git e uma instalacao Python 3.10+ mantida pelo usuario; nao substitua o Python do sistema. Os comandos sao iguais aos do Linux. O ambiente virtual de IA e opcional e nao instala modelos.

## Baixar sem Git

Quando publico, abra a pagina do repositorio, escolha Code e Download ZIP. Extraia, abra o terminal dentro da pasta e execute os comandos Python correspondentes ao seu sistema. Um ZIP nao oferece git pull; baixe uma nova versao para atualizar. Enquanto privado, ate o ZIP exige autorizacao.

## Atualizar

Dentro da pasta clonada, use git status primeiro. Se voce nao alterou codigo e o diretorio de trabalho estiver limpo, git pull --ff-only atualiza sem criar merge automatico. Nao rode reset --hard para resolver problemas sem salvar alteracoes. Seus dados ficam no workspace .core e nao devem ser enviados ao GitHub.

## Desinstalar e dados

Nao existe servico em segundo plano ou desinstalador privilegiado. Antes de remover pastas, copie seu workspace ou rode db-backup. Backups e exportacoes desta versao NAO sao criptografados. Nunca publique .core, bancos, logs ou notas pessoais.
