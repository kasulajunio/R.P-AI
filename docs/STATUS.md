# R.P AI: estado verificavel

## Versao 0.2.0

A branch feat/official-foundation adiciona CLI rpa install/run/update/autoload, entrada boot.py, relatorios JSON e templates de startup opt-in para Linux, Termux e Windows. A licenca MIT foi adotada por solicitacao expressa do titular. Changelog e README descrevem instalacao, limites e compatibilidade.

Notas com leitura, busca, edicao e exclusao confirmada; tarefas persistentes com conclusao/reabertura; exportacao JSON sem sobrescrita; backup SQLite verificado pela API nativa; hash SHA-256; preparacao offline de ambiente: implementados.

Rpa install detecta sistema, prepara banco e workspace e verifica Python do venv sem instalar pip ou modelos. A CLI gera relatorio por operacao sem registrar dados de notas ou argumentos brutos. Atualizacao e explicita, usa Git/rede e recusa branch diferente de main, alteracoes locais ou origin diferente do oficial. Nao faz reset nem resolve conflitos.

Autoload gera arquivos, nao ativa servicos. Startup executa preparacao e verificacao SQLite e encerra. --auto-update permite pull no startup; nao e monitoramento continuo nem rollback automatico. Nenhum servico foi ativado no dispositivo do titular.

## Evidencia e CI

A fundacao do commit 1de393d31c8b52eaea73b6750d4a93e63b8d726d foi observada aprovada em seis jobs Linux, Windows e macOS Intel com Python 3.10/3.12. Isso nao prova a revisao atual. Consulte checks do commit exato no PR #1.

A CI atual inclui compilacao das entradas novas, regressao offline, criacao real de venv, subprocessos de boot/rpa/autoload, smoke, metricas e triagem de padroes de credenciais. Um job separado instala o pacote editavel com pip para verificar o comando rpa: esse job pode usar rede para ferramentas de build. Atualizacao por Git e testada com mocks, nao por download obrigatorio. Startup no sistema operacional nao e ativado pelos testes.

## Visibilidade e privacidade

O titular solicitou publicacao; o repositorio permanece privado enquanto se decide como tratar o e-mail pessoal no historico. Licenca MIT e visibilidade sao coisas diferentes. Nao houve acesso publico confirmado nesta revisao.

Checker de padroes no historico nao e auditoria nem prova de ausencia de segredos ou dados pessoais. Nao registra valores encontrados.

## Ainda nao pronto

Nao ha inferencia/chat com modelo, cofre criptografado, motor de jogos completo ou tuneis. Ainda nao validados em uso real: Android/Termux, GPU/CUDA e ativacao de boot/systemd/Agendador. macOS nao tem template de launchd. Relatorios nao possuem rotacao automatica. Notas, tarefas, bancos, JSON, backups e logs nao sao cifrados.
