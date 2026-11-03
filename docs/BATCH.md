# Lote explicito do Forge

O script Bash recebido estava truncado e continha delimitadores de case fora de contexto. Os tamanhos listados nao eram comparados, nao havia SHA-256, erros eram mascarados e um arquivo tar.bz2 era tratado como executavel. Nao foi executado nem incorporado.

O projeto permanece R.P AI; a mencao E.P AI foi entendida como referencia ao mesmo projeto, sem renomear repositorio ou produto.

Uma unica execucao agora pode planejar ou instalar um lote aprovado:

```sh
python -m official_core.forge_batch plan jq
python -m official_core.forge_batch install jq --allow-network
```

Cada item e pre-validado offline antes de qualquer download. Uma ferramenta nao aprovada, como nmap no catalogo atual, bloqueia o lote inteiro nessa etapa sem baixar jq. Ha limite de 32 itens sem duplicatas. Sem consentimento explicito, install e rejeitado.

Cada instalacao delega ao Forge existente: versao fixa, HTTPS, plataforma/ABI, SHA-256, temporario, limite de tamanho e publicacao sem sobrescrita. O catalogo continua somente jq 1.8.2. Nao foram adicionados URLs ou tamanhos arbitrarios, nmap, APKs ou assets Android/Termux.

A instalacao e sequencial e nao e transacional: se houver falha depois de itens concluidos, eles permanecem instalados. O JSON informa partial/failed, itens concluidos e itens nao tentados; o processo retorna erro e interrompe o restante. Nao ha rollback, repeticao automatica nem execucao dos binarios baixados. system_available nao significa download ou validacao da versao de sistema.

Uma execucao nao significa uma unica conexao HTTP: cada arquivo e seus redirecionamentos podem exigir requisicoes separadas. Agrupar nao contorna ThrottlerException do servico remoto. Nenhum retry ou agendamento automatico foi criado.

Os testes usam rede simulada ou proibida. A aprovacao do CI nao comprova download real nem funcionamento no celular.
