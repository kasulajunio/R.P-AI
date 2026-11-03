# Forge integrado ao rpa

```sh
rpa forge plan jq
rpa forge install jq --allow-network
```

Sem instalar o pacote, use python rpa.py forge plan jq ou python rpa.py forge install jq --allow-network. A interface standalone python -m official_core.forge permanece disponivel.

O primeiro comando produz JSON de diagnostico/plano, sem rede, execucao de binario, workspace ou relatorio. O segundo autoriza rede explicitamente e delega ao mesmo motor restrito: catalogo fixo, HTTPS, SHA-256, compatibilidade de plataforma e publicacao sem sobrescrita. Install apenas instala; nao executa o binario nem altera PATH global.

--directory escolhe o diretorio privado, padrao ~/.rpa/bin. Ele independe de --root, usado pelo nucleo para banco/logs. Esse comando nao cria relatorio no workspace para preservar plan estritamente somente leitura.

## Limites deliberados

Nao aceita argumento usuario/repositorio arbitrario, nao consulta releases/latest e nao tenta corrigir qualquer falha de apt. O nucleo nao roda apt. Ferramenta desconhecida ou ABI nao aprovada retorna erro sem download. jq ja instalado pelo sistema pode ser utilizado. Android/Termux nao possuem asset aprovado nesta revisao; nao ha promessa de download funcional nesses aparelhos.

O case Bash corrompido foi substituido por roteamento Python e nao foi incorporado ao produto. Interface de automacao e controles completos: docs/FORGE.md. O modo API run(..., repair=True) permanece opt-in; falha de execucao nao dispara novo download.

Testes test_forge_cli.py cobrem roteamento, autorizacao, plano sem rede/escrita, repositorio arbitrario, desconhecidos, ABI Termux e o entrypoint Python real. Downloads de binarios sao simulados nos testes. A validacao de CI nao comprova execucao de jq real ou validacao no celular.
