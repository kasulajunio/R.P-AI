# Changelog

Formato inspirado em Keep a Changelog. Versao segue SemVer. Entradas descrevem codigo, nao substituem evidencias de CI nem uma release publicada.

## 0.2.0 - em validacao

### Adicionado
- CLI rpa install, rpa run, rpa update e rpa autoload; alternativa python rpa.py sem pip.
- Boot offline detectando Linux, Windows, macOS e Termux, criando e verificando venv sem pip quando solicitado.
- Relatorios JSON locais por operacao, sem registrar texto de notas, argumentos ou saida bruta do Git.
- Templates opt-in de inicializacao para Linux/systemd do usuario, Termux:Boot e Windows/PowerShell.
- Atualizacao explicita somente no clone oficial, branch main limpa e fast-forward.
- Busca, leitura, edicao, exclusao confirmada e exportacao JSON de notas SQLite.
- Tarefas com conclusao e reabertura, verificacao SQLite e backup pela API nativa.
- Guia de terminais, exemplos, badges, matriz multiplataforma e verificacao de padroes de credenciais no historico.

### Alterado
- Licenca MIT por solicitacao expressa do titular; termos e instrucoes de contribuicao alinhados.
- Nome de distribuicao rp-ai-core e comando rpa; nomes anteriores continuam como aliases.

### Limites
- Autoload nao e ativado pelo instalador. Atualizacao no startup exige --auto-update.
- Nao ha inferencia de IA, cofre criptografado, jogos completos, tuneis, download de modelos ou instalacao automatica de pacotes do sistema.
- Android real e ativacao real de startup ainda nao validados; testes usam arquivos/templates e subprocessos locais.

## 0.1.0
- Fundacao modular de Fabio com cinco diretorios de expansao, menu/CLI, SQLite, SHA-256 e venv explicito.
- Controles de caminhos, preservacao de arquivos e CI offline em Linux, Windows e macOS.
