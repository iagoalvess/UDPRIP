# UDPRIP: Implementação e Desafios

**Integrantes:**
* Vitor Moreira Ramos de Rezende
* Iago da Silva Rodrigues Alves

---

## Resumo do Projeto
O segundo trabalho prático da disciplina de Redes teve como objetivo implementar um sistema de roteamento dinâmico baseado no protocolo RIP sobre UDP. O projeto simula um ambiente de rede com múltiplos roteadores permitindo a troca de mensagens de atualização de rotas. Toda a estrutura foi desenvolvida em Python, com foco em simular o comportamento de protocolos reais de roteamento.

A implementação foca nos seguintes pilares:
* Comunicação entre roteadores usando UDP.
* Algoritmo de roteamento RIP com split horizon.
* Atualização periódica das rotas.
* Detecção de falhas e expiração de rotas.
* Suporte a múltiplos caminhos com o mesmo custo (load balancing).
* Interface de linha de comando para simulação em tempo real.

Cada roteador executa em instâncias independentes e se comunica via mensagens UDP, trocando periodicamente suas tabelas de roteamento com os vizinhos.

---

## Arquitetura do Sistema
Cada instância do roteador roda de forma independente, comunicando-se com os demais exclusivamente via pacotes UDP. O módulo central da aplicação é representado pela classe `Gateway`, que gerencia:
* A tabela de roteamento.
* A tabela de vizinhos.
* A lógica de envio e recepção de mensagens.
* A interface de comando.

O script principal `router.py` inicia o roteador, passando o IP, período de atualização e, opcionalmente, um arquivo de startup com comandos iniciais.

---

## Funcionalidades Principais

### 1. Gerenciamento de Vizinhos
* Adicionar vizinhos: com IP e custo.
* Remover vizinhos: via comando.
* Detectar vizinhos inativos: usando contadores de tempo.

### 2. Roteamento Dinâmico (RIP)
* Atualizações periódicas.
* Split horizon: rotas não são anunciadas de volta ao remetente.
* Tabela de roteamento dinâmica, com custo e próximo(s) salto(s).

### 3. Balanceamento de Carga (Ponto Extra)
Quando múltiplos caminhos com custo mínimo estão disponíveis para um destino, todos são armazenados. Na escolha do próximo salto, um caminho aleatório entre os disponíveis é selecionado, promovendo o balanceamento natural do tráfego.

### 4. Simulação de Trajeto (Trace)
Comando `trace <ip>` permite visualizar o caminho até um destino com base na tabela de roteamento, útil para validar o funcionamento e a convergência da rede.

---

## Interface de Comando
O sistema possui uma interface de comandos via terminal que permite:

```bash
add <ip> <peso>     # Adiciona vizinho  
del <ip>            # Remove vizinho  
trace <ip>          # Exibe trajeto até o destino 
````

Essa interface facilita os testes em tempo real e a visualização da convergência da rede.

---

## Protocolo de Mensagens UDP
As mensagens trocadas entre os roteadores são objetos JSON enviados via UDP. Todas as mensagens contêm campos comuns:
* `"type"`: Identifica o tipo da mensagem (ex: `"update"`, `"data"`, `"trace"`, `"absent"`).
* `"source"`: Endereço IP do roteador que originou a mensagem.
* `"destination"`: Endereço IP do roteador destino da mensagem.

**Estruturas específicas por tipo de mensagem:**
* **Mensagem de Atualização (`"update"`)**:
    * `"distances"`: Um dicionário onde as chaves são endereços IP de destino e os valores são os custos para alcançar esses destinos a partir do roteador `source`.

* **Mensagem de Dados (`"data"`)**:
    * `"payload"`: O conteúdo da mensagem a ser entregue ao destino final.

* **Mensagem de Rastreamento (`"trace"`)**:
    * `"routers"`: Uma lista de endereços IP, acumulando os IPs dos roteadores pelos quais a mensagem passou. Inicialmente contém apenas o IP da origem do `trace`.

* **Mensagem de Destino Inalcançável (`"absent"`) [Ponto Extra]**:
    * Enviada de volta ao remetente original de uma mensagem `"data"` ou `"trace"` quando o destino final não pode ser alcançado.

---

## Desafios e Soluções Adotadas

### 1. Múltiplos Próximos Saltos:
* **Desafio:** Adaptar a tabela de roteamento para armazenar e gerenciar múltiplos caminhos de mesmo custo para um destino.
* **Solução:** A estrutura `self.routes` na `RoutingTable` foi projetada para que cada entrada de destino possa ter uma lista `next_hops`, onde cada item é uma tupla `(proximo_salto, aprendido_de)`. O método `update_route` foi modificado para popular corretamente essa lista.

### 2. Expiração de Vizinhos e Rotas:
* **Desafio:** Implementar um mecanismo robusto para detectar vizinhos inativos e remover rotas que se tornaram inválidas.
* **Solução:** O `Gateway` mantém um dicionário `self.last_update` que armazena o horário da última mensagem de atualização recebida de cada vizinho. No `periodic_update_loop`, o método `_expire_routes` verifica se algum vizinho não enviou uma atualização por um tempo. Se sim, o vizinho é considerado inativo, e todas as rotas aprendidas através dele são removidas usando `routing_table.remove_routes_from()`. A lista `received_update_from` ajuda a identificar quais vizinhos enviaram atualizações dentro do ciclo de expiração atual.

---

## Testes Realizados
Os testes foram conduzidos simulando múltiplos roteadores em execução local (em diferentes portas ou IPs locais) e interconectando-os para formar diversas topologias com pesos de link variados. As principais funcionalidades e cenários testados incluíram:
* Convergência da Rede: Observação da estabilização das tabelas de roteamento após o início dos roteadores ou mudanças na topologia.
* Mudança Dinâmica da Topologia: Adição (`add`) e remoção (`del`) de vizinhos em tempo real e verificação da adaptação das rotas.
* Balanceamento de Carga: Configuração de caminhos com custos iguais para um mesmo destino e verificação de que o tráfego (simulado via `trace` ou observando as escolhas de próximo salto) poderia usar qualquer um dos caminhos.
* Expiração de Rotas: Desativação de um roteador e observação da remoção automática das rotas associadas nos roteadores restantes após o período de expiração.
* Comando `trace`: Teste extensivo do comando para diferentes destinos, incluindo destinos alcançáveis, inalcançáveis e o próprio roteador, verificando a precisão dos caminhos reportados.
* Comunicação de Dados e Mensagens `absent`: Verificação do encaminhamento de mensagens `"data"` e o recebimento correto de mensagens `"absent"` quando um destino era inalcançável.

---

## Contribuição das Ferramentas de IA
As ferramentas de Inteligência Artificial foram empregadas como um recurso de apoio valioso durante o desenvolvimento do projeto, principalmente para:
* Depuração e Análise de Lógica: Auxílio na identificação de erros sutis na lógica de atualização de rotas, condições de corrida potenciais e no comportamento do algoritmo de vetor de distância.
* Refinamento de Estruturas de Dados: Sugestões para otimizar ou clarificar a estrutura da tabela de roteamento, especialmente para acomodar os múltiplos próximos saltos.
* Implementação de Mecanismos (ex: Split Horizon): Discussão de abordagens e revisão do código para garantir que o split horizon estivesse corretamente implementado na construção das mensagens de atualização.
* Elaboração e Revisão de Documentação: Assistência na organização das ideias, escrita de explicações claras sobre os componentes do sistema e os algoritmos, e revisão geral do texto para garantir coesão, clareza e padronização técnica.

---

## Conclusão
O desenvolvimento do projeto UDPRIP proporcionou uma compreensão aprofundada e prática dos princípios de roteamento dinâmico, especificamente o funcionamento do algoritmo de vetor de distância e os desafios inerentes a protocolos como o RIP. A simulação da troca de mensagens de rota sobre UDP, a necessidade de lidar com a convergência da rede, a detecção de falhas (expiração de rotas), e a implementação de mecanismos como split horizon e balanceamento de carga foram aspectos cruciais do aprendizado.

A complexidade adicional introduzida pela implementação dos requisitos de múltiplos caminhos e expiração de rotas tornaram o projeto uma experiência de aprendizado completa e desafiadora, solidificando os conceitos teóricos de redes de computadores.

---

## Execução do Projeto
```bash
python3 router.py <ip> <periodo> [arquivo_startup] [porta]
```

* ip: IP local do roteador (simulado).
* periodo: intervalo em segundos entre as atualizações de rota.
* arquivo_startup: (opcional) arquivo com comandos iniciais (add/del).
* porta: (opcional) porta UDP (default: 55151).