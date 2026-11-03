# R.P AI: uso livre, riscos e responsabilidade

Por solicitacao explicita do titular, o codigo original passa a ser disponibilizado sob a licenca MIT em LICENSE: uso pessoal e comercial, copia, modificacao e redistribuicao sao permitidos, preservando copyright e licenca. Nao ha cobranca do titular por esta copia. Isso nao proibe terceiros de comercializar copias sob MIT. Modelos, dependencias, marcas e componentes de terceiros possuem licencas proprias.

Este arquivo e um aviso explicativo, nao uma restricao adicional a MIT nem uma declaracao de que o programa obteve consentimento contratual. Mostrar uma mensagem ou rodar sem perguntas nao demonstra, por si, aceite juridico. Nenhum termo afasta direitos irrenunciaveis ou responsabilidades que nao possam ser excluidas pela lei aplicavel.

O operador deve respeitar a lei e autorizacoes sobre equipamentos, redes e dados, manter backups e conferir resultados. O software e experimental e pode apresentar falhas, incompatibilidade, perda de dados e consumo de disco, memoria e bateria. E fornecido no estado em que se encontra, sem garantias adicionais, nos limites legais.

O boot cria arquivos num workspace dedicado, banco SQLite e, por padrao, ambiente virtual. Nao usa sudo, nao instala pacotes globais, nao abre tuneis e nao baixa modelos ou bibliotecas de IA. Venv nao e sandbox. Banco, notas, exportacoes e backups nao sao criptografados. Crypto_Vault nao e um cofre pronto.

Python e Git precisam existir antes da execucao. Em sistemas sem o suporte venv/ensurepip, o boot falha claramente; --without-venv permite usar notas e tarefas sem ML. Nenhuma falha e apresentada como sucesso. O primeiro download de um modelo exigira internet ou transferencia de uma copia existente e deve respeitar a respectiva licenca. Esta versao ainda nao executa inferencia.

O nucleo nao implementa telemetria. GitHub e ambientes de CI seguem suas proprias politicas. Nao publique workspace, chaves, senhas, tokens, modelos restritos ou dados pessoais. Publicar um repositorio revela tambem historico e metadados dos commits; a revisao de privacidade precede a mudanca de visibilidade.
