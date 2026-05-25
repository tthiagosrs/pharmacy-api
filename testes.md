# Documento de Estratégia de Testes — FarmaOS

**Projeto:** FarmaOS  
**Autor:** Thiago Soares  
**Professor:** Adrian Ferreira Ramos  
**Disciplina:** Arquitetura de Software / Desenvolvimento Web/Mobile III

---

## Funcionalidades Testadas

1. Autenticação de usuários
2. Registro de novo usuário
3. Disponibilidade e saúde da API

---

## 1. Autenticação de Usuários

**Regras de negócio**

- O usuário precisa de email e senha válidos para acessar o sistema
- A senha deve ter no mínimo 6 caracteres
- Login bem-sucedido retorna um token JWT usado nas demais rotas
- Cada usuário tem um cargo (balconist, pharmacist, manager) que define suas permissões

---

### CT-01 — Login com credenciais válidas

**Tipo:** Integração  
**Cenário:** positivo

**Pré-condição:** usuário cadastrado com email `thiago@farmaos.com` e senha `123456`

**Entrada:**
```json
{ "email": "thiago@farmaos.com", "password": "123456" }
```

**Resultado esperado:** status 200 com `access_token` na resposta

**Resultado obtido:**
```json
{ "access_token": "eyJ...", "user_id": "uuid", "email": "thiago@farmaos.com" }
```

---

### CT-02 — Login com senha incorreta

**Tipo:** Integração  
**Cenário:** negativo

**Pré-condição:** usuário cadastrado no sistema

**Entrada:**
```json
{ "email": "thiago@farmaos.com", "password": "senhaerrada" }
```

**Resultado esperado:** status 401 com mensagem de erro

**Resultado obtido:**
```json
{ "detail": "Email ou senha inválidos" }
```

---

## 2. Registro de Novo Usuário

**Regras de negócio**

- O email deve ser único — não é possível cadastrar dois usuários com o mesmo email
- Os campos `name` e `role` são obrigatórios
- Ao criar o usuário, um trigger no banco insere automaticamente os dados na tabela `profiles`
- Valores padrão são usados se `name` ou `role` não forem informados (`Sem nome` e `balconist`)

---

### CT-03 — Registro com dados válidos

**Tipo:** Integração  
**Cenário:** positivo

**Pré-condição:** email não cadastrado no sistema

**Entrada:**
```json
{
  "email": "maria@farmaos.com",
  "password": "senha123",
  "name": "Maria Silva",
  "role": "pharmacist"
}
```

**Resultado esperado:** status 200 com `user_id` na resposta e registro criado em `profiles`

**Resultado obtido:**
```json
{ "message": "Usuário cadastrado com sucesso", "user_id": "uuid", "email": "maria@farmaos.com" }
```

---

### CT-04 — Registro com email já existente

**Tipo:** Integração  
**Cenário:** negativo

**Pré-condição:** email `thiago@farmaos.com` já cadastrado

**Entrada:**
```json
{
  "email": "thiago@farmaos.com",
  "password": "outrasenha",
  "name": "Outro Usuario",
  "role": "balconist"
}
```

**Resultado esperado:** status 400 informando que o email já está em uso

**Resultado obtido:**
```json
{ "detail": "User already registered" }
```

---

## 3. Disponibilidade e Saúde da API

**Regras de negócio**

- A API deve estar sempre disponível para receber requisições do Flutter
- O endpoint `/health` retorna status `ok` enquanto a API estiver operacional
- O Kubernetes realiza verificação de saúde via Liveness Probe no `/health` a cada 30 segundos — se não responder, o pod é reiniciado automaticamente

---

### CT-05 — Health check em produção

**Tipo:** E2E  
**Cenário:** positivo

**Pré-condição:** cluster K3s rodando com pods em status Running

**Entrada:** `GET http://146.190.75.199/health`

**Resultado esperado:** status 200

**Resultado obtido:**
```json
{ "status": "ok", "database": "connected" }
```

---

### CT-06 — Resiliência com pods parados

**Tipo:** E2E  
**Cenário:** negativo

**Pré-condição:** cluster K3s rodando normalmente

**Procedimento:**
1. Deletar todos os pods da API: `kubectl delete pods -l app=farmaos-api`
2. Acessar `GET http://146.190.75.199/health` imediatamente
3. Aguardar 30 segundos e acessar novamente

**Resultado esperado (etapa 2):** status 502 ou 503  
**Resultado esperado (etapa 3):** status 200 — Kubernetes recriou os pods automaticamente

---

## Resumo

| ID | Funcionalidade | Tipo | Cenário |
|---|---|---|---|
| CT-01 | Autenticação | Integração | Positivo |
| CT-02 | Autenticação | Integração | Negativo |
| CT-03 | Registro de usuário | Integração | Positivo |
| CT-04 | Registro de usuário | Integração | Negativo |
| CT-05 | Saúde da API | E2E | Positivo |
| CT-06 | Saúde da API | E2E | Negativo |

---

## Tipos de Teste utilizados

**Unitário:** testa uma função isolada sem dependências externas. Não aplicado nesta versão pois as funcionalidades dependem diretamente do Supabase.

**Integração:** testa a comunicação entre componentes. Nos testes CT-01 a CT-04, verifica se a API FastAPI processa as requisições corretamente e se comunica com o Supabase Auth.

**E2E:** testa o fluxo completo do sistema. Nos testes CT-05 e CT-06, percorre o caminho inteiro: cliente, Ingress, Nginx, FastAPI e resposta final.
