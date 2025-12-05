# Distributed Chat System — FastAPI + WebSockets + HTTP Relay + Docker

Este projeto implementa um **sistema de chat distribuído** composto por dois serviços independentes que:

- Aceitam conexões WebSocket de clientes (navegadores);
- Troc​am mensagens entre si através de HTTP (`/relay`);
- Replicam mensagens recebidas localmente e vindas do outro serviço;
- São executados em containers Docker distintos;
- Demonstram, na prática, diversos **conceitos fundamentais de Redes de Computadores**.

O sistema foi desenvolvido como material prático para a disciplina de **Redes de Computadores**, permitindo observar:

- Tráfego WebSocket (camada de aplicação);
- Tráfego HTTP entre containers (relay);
- Encapsulamento e comunicação entre processos isolados (containers);
- Operação cliente-servidor distribuída;
- Propagação de mensagens ponto-a-ponto.

---

## Arquitetura Geral

```
┌──────────────────────────────┐            ┌──────────────────────────────┐
│        Service A (8000)      │ <──HTTP──> │        Service B (8001)      │
│  - Conexões WebSocket        │            │  - Conexões WebSocket        │
│  - Broadcast local           │            │  - Broadcast local           │
│  - Envia mensagens ao B      │            │  - Envia mensagens ao A      │
└──────────────────────────────┘            └──────────────────────────────┘
             ▲                                              ▲
             │                                              │
             │ WebSocket                                    │ WebSocket
             │                                              │
       ┌──────────────┐                             ┌──────────────┐
       │ Navegador 1  │                             │ Navegador 2  │
       └──────────────┘                             └──────────────┘
```

---

## Funcionalidades do Sistema

### 1. Comunicação WebSocket com clientes  

Cada serviço aceita múltiplas conexões WebSocket simultâneas.  
Quando um cliente envia uma mensagem:

- Ele vê **apenas sua própria mensagem** (`You:`)
- Os demais clientes conectados ao mesmo serviço recebem a mensagem formatada.

Implementação:  
`connection_manager.py` → `broadcast(skip=websocket)`

---

### 2. Comunicação entre serviços via HTTP (`/relay`)

Quando Service A recebe uma mensagem:

1. Mostra aos seus próprios clientes;
2. Envia um POST para Service B:

```http
POST http://serviceB:8000/relay
{
  "message": "Client #261: teste"
}
```

Service B recebe via:

```python
@router.post("/relay")
async def relay(msg: RelayMessage):
    await manager.broadcast(msg.message)
```

Assim replicamos **todas as mensagens** entre os serviços.

---

### 3. Frontend com auto-conexão

O arquivo `index.html` se conecta automaticamente ao WebSocket do serviço atual:

```js
const host = window.location.host;
const wsUrl = `ws://${host}/ws/${clientId}`;
```

Sem necessidade de digitar o endpoint manualmente.

---

### 4. Docker Compose com dois serviços isolados

`docker-compose.yml` define dois containers:

- `serviceA` → porta 8000
- `serviceB` → porta 8001

Cada serviço recebe:

- `SERVICE_NAME=A|B`
- `PEER_URL=http://serviceB:8000/relay` (ou inverso)

Isso garante comunicação isolada e bidirecional.

---

## Conceitos de Redes Aplicados

Este projeto demonstra, na prática, vários conceitos fundamentais estudados em redes:

---

### 1. **Modelo Cliente–Servidor**

Cada navegador é um **cliente WebSocket**, enquanto `serviceA` e `serviceB` são servidores independentes.

---

### 2. **Sockets TCP (WebSockets)**

WebSockets utilizam TCP em conexão persistente:

- Handshake inicial HTTP  
- Upgrade para WebSocket  
- Troca de frames binários/texto  

Permite comunicação **full-duplex**.

---

### 3. **Comunicação entre processos distribuídos**

Os containers se comunicam usando HTTP interno:

```
serviceA → serviceB : POST /relay
```

Demonstra:

- DNS interno do Docker (`serviceB`)
- Comunicação entre hosts isolados

---

### 4. **Modelo OSI / TCP-IP**

| Camada (OSI)        | Componente |
|---------------------|------------|
| Aplicação           | WebSocket, HTTP, FastAPI |
| Transporte          | TCP |
| Rede                | Docker Bridge |
| Enlace              | Virtual Ethernet |
| Física              | Abstraída |

---

### 5. **Isolamento e rede virtual (Docker Bridge)**

Cada serviço roda em container isolado, comunicando-se via ponte virtual.

---

### 6. **Broadcast controlado**

O servidor envia mensagens para todos, exceto o remetente:

```
broadcast(msg, skip=websocket)
```

---

## Como executar

### 1. Subir containers

```bash
docker-compose up -d --build
```

### 2. Acessar serviços

- http://localhost:8000 → Service A  
- http://localhost:8001 → Service B  

Abra duas abas para ver a replicação em tempo real.

---

## Monitorar tráfego de rede

### WebSocket

DevTools → Network → WS

### HTTP Relay

Wireshark/TCPDump:

```
tcp.port == 8000 || tcp.port == 8001
```

---

## Conclusão

Esse projeto foi desenvolvido para ilustrar conceitos essenciais de Redes de Computadores através de uma aplicação prática e interativa. Alunos participantes:

- João Pedro Barboza
- Guilherme Brito
- Daniel Fernandes
- Higor Souza
