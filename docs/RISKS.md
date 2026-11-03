# Riscos reais e controles

| Risco | Controle atual | O que ainda depende do operador |
| --- | --- | --- |
| Sobrescrever dados | Escrita exclusiva e preservacao de arquivos existentes | Backup e workspace dedicado |
| Escapar do workspace | Validacao de caminhos e recusa de symlinks/junctions detectaveis | Impedir escrita concorrente de terceiros e hardlinks maliciosos |
| Dependencia comprometida | Nucleo sem pacotes obrigatorios e sem downloads automaticos | Revisar Python, PATH, pacotes e sistema operacional |
| Execucao externa | Sem shell, timeout no diagnostico | Proteger o executavel nvidia-smi e PATH |
| Roubo de segredos | Avisos, gitignore e ausencia de telemetria | Nao colocar segredos no Git, notas ou Crypto_Vault |
| Perda de dados SQLite | Escrita parametrizada e transacoes | Backup consistente, disco saudavel e controle de acesso |
| Consumo de recursos | Limites de notas, listagem e hash | Espaco para venv, memoria e baterias |
| IA insegura | Nao instala modelos ou executa inferencia | Revisao humana, licencas e limites de hardware em extensoes |
| Rede exposta | Sem servidor ou tunel implementado, config desativada | Nao expor portas e obter autorizacao em futuras extensoes |
| Falsa sensacao de isolamento | Documentacao explicita | Usar VM, container configurado ou maquina dedicada quando necessario |
| Vazamento pelo CI | Somente codigo e dados sinteticos nos testes | Nao adicionar segredos a logs ou artifacts |

Nao existe ferramenta sem risco. Repositorio privado nao impede vazamento por colaboradores, clones, dispositivos ou permissoes inadequadas. gitignore nao remove arquivos ja versionados. Os termos nao autorizam uso ilegal e nao apagam responsabilidades previstas em lei.
