# Chat local e miniapps HTML

A branch feat/official-foundation agora implementa chat HTTP com modelo Ollama local e criacao de miniapps HTML. Nao e APK, agente autonomo nem controle do Android.

## Uso sem modelo e sem download

Na pasta do projeto, execute:

```sh
python rpa.py app create meu-contador
python rpa.py app create minhas-tarefas --template todo
```

O JSON informa o caminho do index.html. Nada e aberto automaticamente. O contador tem +1, -1 e zerar; a lista e temporaria e perde itens ao recarregar. Arquivos existentes nao sao sobrescritos. Estes sao templates deterministas, nao criacao por IA.

## Modelo no Termux, suporte experimental

O pacote ollama existe no repositorio oficial termux-packages. Disponibilidade na instalacao, arquitetura, RAM livre, espaco e desempenho precisam ser verificados no aparelho real. Nao use sudo nem o instalador Linux no Android.

1. Antes de baixar, confira RAM e armazenamento. O modelo qwen2.5-coder:0.5b tem aproximadamente 398 MB de download, alem do pacote e dos recursos de execucao; isso nao e uma estimativa de RAM. E pequeno e pode errar bastante. Nao ha garantia de velocidade ou qualidade.
2. Instalacao explicita: `pkg install ollama`. Nao e executada pelo R.P AI.
3. Em uma sessao do Termux: `OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve`. Mantenha essa sessao aberta. Nao exponha em 0.0.0.0.
4. Em outra sessao, autorize o download executando `ollama pull qwen2.5-coder:0.5b`. O download usa internet.
5. Na pasta desta revisao do projeto: `python rpa.py chat`. Digite /sair para encerrar. Uma pergunta unica: `python rpa.py chat "Ola, quem e voce?"`.
6. Gerar por IA: `python rpa.py app create meu-app --prompt "Um contador com botao grande"`.

Depois do download, a inferencia usa o servidor local. O cliente Python so acessa 127.0.0.1:11434, ignora proxies de ambiente e recusa redirecionamentos. O backend e software separado: sua configuracao e outros processos locais nao sao auditados pelo R.P AI. Nenhuma API paga ou conta de modelo e configurada.

## Privacidade e limites

- Chat nao salva historico, prompts ou respostas em SQLite/logs do R.P AI. O historico recente fica na memoria ate sair; terminal e backend podem ter seus proprios registros.
- Sem acesso automatico a arquivos, notas, contatos, microfone ou senhas. Sem ferramentas, shell, instalacao de APK ou execucao de comandos do modelo.
- Criacao por IA envia somente o pedido digitado ao backend local e grava HTML nao cifrado no workspace. HTML incompleto e recusado. A existencia do arquivo NAO prova funcionamento.
- HTML do modelo e escapado em iframe sandbox sem same-origin, formularios ou popups, com CSP restritiva. Isso reduz riscos, nao e auditoria nem garantia de seguranca. Revise o codigo e nao forneca dados pessoais ao miniapp.
- Nenhum modelo, pacote ou servico e instalado/baixado/iniciado pelo comando install ou pelo status. Chat exige que o servidor e modelo existam.
- Timeout padrao 180s, ajustavel ate 600s. O historico e limitado e respostas podem ser truncadas pelo modelo.
- Modelos maiores opcionais: --model qwen2.5-coder:1.5b ou :3b, sempre com pull explicito e recursos suficientes. Nao interpretar seus downloads como autorizados pelo uso do padrao.

## Verificacao

Tests/test_assistant.py verifica protocolo com servidor HTTP sintetico, proxies, redirecionamento, erros, limites, privacidade e criacao de arquivos. Isso nao e prova de inferencia real.

O workflow Local AI verification baixa explicitamente Ollama oficial com SHA-256 fixo e o modelo 0.5b somente no runner Linux de CI. Executa inferencia real, gera HTML via modelo e testa os botoes do template contador em Chrome headless. Consulte o resultado do commit exato: adicionar workflow nao significa que ele passou. O comportamento do HTML gerado pelo modelo e Android/Termux real continuam nao comprovados ate teste especifico.

Prepare ai continua apenas preparando estrutura/venv sem instalar PyTorch ou modelos. Venv nao e sandbox de seguranca.
