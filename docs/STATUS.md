# R.P AI: status verificavel

A fundacao do commit 1de393d31c8b52eaea73b6750d4a93e63b8d726d passou nos seis jobs Linux, Windows e macOS Intel, Python 3.10/3.12. Uma revisao anterior nao comprova aprovacao da revisao atual: consulte sempre os checks do commit exato.

A ampliacao inclui notas com busca, leitura, edicao e exclusao confirmada; tarefas persistentes com conclusao e reabertura; exportacao JSON sem sobrescrita; backup SQLite verificado pela API nativa; instrucoes por terminal e boot nao interativo com venv real.

O boot detecta sistemas sem despejar variaveis de ambiente, prepara o workspace, verifica o Python do venv e pode chamar comandos locais. Nao usa sudo, shell=True ou instalacao global. Exibe termos, sem fingir consentimento automatico. Falhas retornam erro. Nao roda como servico de fundo.

O titular autorizou uso livre para qualquer finalidade; a licenca vigente foi alterada para MIT, incluindo uso comercial e redistribuicao com preservacao de aviso e licenca. Os avisos antigos de licenca proprietaria nao regem a revisao atual.

O repositorio permanece privado ate a decisao informada sobre o e-mail presente nos metadados historicos. Nao houve publicacao aberta confirmada. Alterar a licenca nao altera a visibilidade no GitHub.

O checker examina blobs do historico alcancavel para alguns padroes de credenciais. Nao e auditoria nem prova de ausencia de segredos ou dados pessoais.

Ainda nao implementado: inferencia/chat com modelo, cofre criptografado, motor de jogos e tuneis. Ainda nao validado: Android/Termux em aparelho real e GPU/CUDA. Notas, tarefas, bancos, JSON e backups nao sao cifrados.
