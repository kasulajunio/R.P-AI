# Inicializacao opcional no dispositivo

Nenhum comando desta conversa ativa o boot do seu celular ou PC. Os templates sao arquivos locais; ativacao e desativacao sao feitas no dispositivo pelo titular. Nao use root/admin. Nao ative em dispositivos de terceiros.

## Base

```sh
python autoload.py --root .core
```

Prepara nucleo e venv e verifica SQLite, sem rede. Sai ao terminar; nao e servidor nem monitor continuo. `--no-venv` evita venv em ambientes sem suporte. `--auto-update` autoriza Git/rede antes do boot. Se update falhar, startup para e retorna falha, preservando dados; pode haver falta de rede durante o boot. Nao aceita conflitos, worktree alterada, branch diferente de main ou origin diferente do oficial.

## Android / Termux:Boot

Instale Termux e Termux:Boot por fontes compativeis indicadas nos projetos oficiais. Abra Termux:Boot uma vez para habilitar seu receptor conforme sua documentacao. Mantenha o clone em armazenamento privado do Termux, nao em /sdcard: permissao de execucao e venv podem falhar no armazenamento compartilhado.

```sh
python rpa.py autoload --platform termux
mkdir -p ~/.termux/boot
cp -n .core/Autoload/rp-ai-termux.sh ~/.termux/boot/rp-ai.sh
chmod 700 ~/.termux/boot/rp-ai.sh
```

O script usa caminhos absolutos do Python, clone e workspace. Use `--auto-update` ao gerar somente se quiser Git/rede no startup. Modelos nao sao baixados. O Android pode impedir execucao por restricoes de bateria. Nao foi testado em aparelho real. Desativar: remova somente ~/.termux/boot/rp-ai.sh, preservando dados do projeto.

## Linux com systemd do usuario

```sh
python rpa.py autoload --platform linux
mkdir -p ~/.config/systemd/user
cp -n .core/Autoload/rp-ai.service ~/.config/systemd/user/rp-ai.service
systemctl --user daemon-reload
systemctl --user enable rp-ai.service
systemctl --user start rp-ai.service
systemctl --user status rp-ai.service
```

Isto inicia na sessao do usuario, nao garante inicializacao antes do login. Nao habilita linger. Para parar futuras inicializacoes: `systemctl --user disable rp-ai.service`; remova somente o arquivo de unidade criado e rode daemon-reload. Nao use sudo. A ativacao real nao faz parte da CI.

## Windows

```powershell
py -3 rpa.py autoload --platform windows
```

O template .core/Autoload/rp-ai.ps1 usa caminhos absolutos. Abra o Agendador de Tarefas e crie tarefa no logon do seu usuario, sem privilegios elevados. Programa: powershell.exe; argumentos: `-NoProfile -NonInteractive -File C:\CAMINHO\.core\Autoload\rp-ai.ps1` (coloque o caminho do arquivo entre aspas se contiver espacos). Politica local pode bloquear scripts; nao use Bypass nem altere politica da empresa para contornar. Alternativa: agende diretamente python.exe com autoload.py --root e caminhos absolutos. Para desativar, desabilite somente a tarefa criada. Validacao real no Agendador ainda pendente.

## Atualizacao e manutencao

Por padrao nao ha auto-update. Para gerar template com permissao explicita: `python rpa.py autoload --platform linux --auto-update`, ou outra plataforma suportada. O comando nao sobrescreve templates existentes; revise e preserve a versao antiga antes de gerar em novo workspace. Nao ha rollback automatico nem instalacao de dependencias novas. Atualizar codigo implica confiar nas mudancas do repositorio oficial.

Se mover clone, Python ou workspace, regenere/revise caminhos antes de reativar. Backups e logs sao locais e nao cifrados. Veja README para diagnostico e limites. macOS ainda sem template de launchd.
