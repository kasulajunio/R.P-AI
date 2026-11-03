# Contribuir com a R.P AI

Codigo desta revisao sob MIT: consulte LICENSE. Preserve avisos de autoria. Proponha mudancas por issue e pull request, descrevendo objetivo, compatibilidade e riscos. Nao ha transferencia automatica de autoria de contribuicoes.

Use Python 3.10+ e biblioteca padrao para o nucleo. Crie branch curta, adicione testes e atualize changelog e documentacao. Use dados sinteticos. Nunca inclua tokens, bancos pessoais, executaveis ou modelos.

Checklist: regressao offline, compilacao, smoke, checker de padroes de credenciais e seis jobs multiplataforma no commit atual; sem rede implicita, shell inseguro, sobrescrita de dados ou promessas alem do codigo. O checker nao substitui revisao de seguranca.

Inicializacao no boot permanece opt-in; nao crie servicos durante testes e nao execute templates no dispositivo de terceiros. Instalacao e atualizacao sao acoes diferentes.
