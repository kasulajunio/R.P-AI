# Correcao dos identificadores de miniapps

A execucao 41738722418 falhou no contador de passo dois. O pedido exigia output id=value, mas o modelo gerou p id=counter. O DOM registrou failed:initial. Nao foi uma falha comprovada de Alpine ou da aritmetica.

A geracao agora verifica IDs declarados como id=valor no pedido, exigindo ocorrencia unica no HTML. Tipos output/button/input/textarea/select/canvas explicitamente associados tambem sao conferidos. Comentarios, strings em scripts e conteudo inerte de template nao satisfazem o contrato.

Se o modelo desrespeitar esse contrato, recebe uma unica nova tentativa com o pedido original e os erros objetivos. O prazo restante e compartilhado entre as duas chamadas. Se repetir a falha, nenhum app e salvo. Respostas incompletas e erros de rede continuam falhando sem repeticao cega.

O JSON informa generation_attempts: zero para template, um ou dois para modelo. Essa verificacao e estatica: nao executa JavaScript, nao garante comportamento e nao modifica functional_tested=false. Sandbox do iframe, CSP, ausencia de abertura automatica e protecao contra sobrescrita foram preservados.

Os testes originais de navegador permanecem inalterados. O workflow Miniapp contract regression executa a suite completa e duas rodadas dos quatro casos de IA real. Consulte o commit e a conclusao efetivos antes de considerar aprovado. Nenhuma alteracao no celular real.
