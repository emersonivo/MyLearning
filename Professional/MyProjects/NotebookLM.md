**I. Introdução e Fundamentos do Protocolo Kerberos**
*   **Definição do Kerberos e Histórico:** Projeto Athena do MIT e evolução do protocolo.
*   **Arquitetura e Modelo de Confiança:** Funcionamento baseado no modelo de confiança de terceiros.
*   **Componentes Centrais:** Key Distribution Center (KDC), Authentication Service (AS) e Ticket Granting Service (TGS).
*   **Elementos Fundamentais:** Principals (Usuários e Serviços), Realms, Keytabs e Privilege Attribute Certificate (PAC).
*   **Dinâmica de Ingressos:** Emissão e uso do Ticket Granting Ticket (TGT) e Service Ticket (ST).
*   **O Fluxo de Autenticação Passo a Passo:**
    *   Etapa 1: AS-REQ / AS-REP (Troca Inicial e Pré-autenticação).
    *   Etapa 2: TGS-REQ / TGS-REP (Aquisição do Ingresso de Serviço).
    *   Etapa 3: AP-REQ / AP-REP (Troca Cliente-Servidor e Autenticação Mútua).
*   **Gerenciamento de Tempo:** Dependência de sincronização de relógios (Clock Skew) e uso do NTP.
*   **Kerberos vs. Outros Protocolos:** Comparativos estruturais contra NTLM, LDAP, OAuth, SAML e OpenID Connect.

**II. Criptografia, Delegação e Extensões Avançadas**
*   **Criptografia e Encriptação Suportada:** Implementações AES (128 e 256 bits), vulnerabilidade do RC4 e família DES legada.
*   **O Conceito de Delegação de Autenticação:** Como serviços agem em nome de clientes.
*   **Modelos de Delegação no Active Directory:** Não Restrita (Unconstrained), Restrita (Constrained) e Baseada em Recursos (RBCD).
*   **Evolução de Contas de Serviço:** Group Managed Service Accounts (gMSA) e Delegated Managed Service Accounts (dMSA).
*   **Autenticação Moderna (PKINIT):** Uso de Smartcards, Certificados baseados em PKI e chaves FIDO2 / Windows Hello.

**III. Administração de Sistemas Baseados em MIT Kerberos**
*   **Arquivos de Configuração do Sistema:** Diretrizes de localização e sintaxe.
    *   Estrutura do `krb5.conf`: Seções `[libdefaults]`, `[realms]`, `[domain_realm]`, `[capaths]`, `[plugins]` e `[dbmodules]`.
    *   Estrutura do `kdc.conf`: Seções `[kdcdefaults]`, `[realms]` e `[logging]`.
*   **Configuração de DNS no Ambiente Kerberos:** Mapeamento de Hostnames (TXT) e uso de Registros SRV para a localização de KDCs.
*   **Operações Globais no Banco de Dados (`kdb5_util` e `kdb5_ldap_util`):**
    *   Criação, destruição, extração para backups (Dump/Load) e geração de Stash Files.
    *   Configurações específicas com backend de diretório OpenLDAP.
*   **Gestão Diária de Banco de Dados e Entidades (`kadmin` e `kadmin.local`):**
    *   Criação, modificação, exclusão de Principals e reset de senhas.
    *   Listas de Controle de Acesso (ACL) pelo arquivo `kadm5.acl` e definição de Privilégios.
    *   Criação e aplicação de Políticas de Senha e Políticas de Tempo de Vida (Lifetimes).
*   **Servidores de Aplicação e Keytabs:**
    *   Gerenciamento e extração de chaves usando os comandos `ktadd` e `ktremove`.
    *   Mapeamento de portas de firewall recomendadas (Portas 88, 749, 464, 754) e acessos de comunicação.
*   **Autenticação Cross-Realm e Contas Especiais:** Estabelecimento de confiança mútua e renovação da chave `krbtgt` e da chave de histórico.

**IV. Kerberos no Windows Server, Active Directory e Cloud**
*   **Papel do Active Directory (AD):** Domain Controllers atuando nativamente como KDCs e gerenciando repositórios Kerberos.
*   **Relações de Confiança (Trusts):** Estabelecimento de relações Cross-Realm transitivas e não transitivas entre domínios ou florestas do AD.
*   **Gestão de Identidade Interoperável:** Single Sign-On (SSO) e SSPI versus implementações MIT/Unix com GSS-API.
*   **Extensão Híbrida e Nuvem (Microsoft Entra Kerberos):** Identidades exclusivas de nuvem e roteamento de autenticação híbrida.
*   **Fluxos de Nuvem:** Emissão de TGT de Nuvem (Cloud TGT), TGT Parcial On-Premises (OnPremTgt) e Primary Refresh Token (PRT).

**V. Ameaças de Segurança, Ataques e Mitigações**
*   **Roubo de Credenciais e Ataques de Extração Offline:**
    *   Kerberoasting: Exploração de SPNs e quebra offline de hashes RC4.
    *   AS-REP Roasting: Identificação e abuso de contas sem pré-autenticação.
*   **Falsificação e Abuso de Tickets (Ticket Forgery):**
    *   Golden Ticket: Comprometimento total da chave `krbtgt`.
    *   Silver Ticket: Falsificação de ticket de serviço específico.
    *   Pass-the-Ticket (PtT), Pass-the-Cache e Overpass-the-Hash: Reutilização de tickets extraídos da memória (Ex: LSASS).
*   **Exploração de Funcionalidades do Active Directory:**
    *   Abuso da Delegação Não Restrita (Unconstrained Delegation Abuse).
    *   DCSync, Dump da base `ntds.dit` e ataques de Skeleton Key (Malware local e senhas mestras).
    *   Desvio de Relação de Confiança Unidirecional (One-Way Trust Bypass) e Falsificação SAML (Golden SAML).
*   **Melhores Práticas e Estratégias de Mitigação:**
    *   Isolamento no grupo "Protected Users" e Hardening de Endpoints (ex: Credential Guard).
    *   Adoção impositiva de gMSAs/dMSAs em substituição de contas de serviços tradicionais.
    *   Desativação da encriptação RC4, exigência rigorosa de AES (128/256) e senhas longas (>25 caracteres).
    *   Aplicação de rodízio e dupla rotação periódica para a senha da conta `krbtgt` para invalidar Golden Tickets.

**VI. Resolução de Problemas (Troubleshooting) e Auditoria**
*   **Metodologia de Diagnóstico:** Checklist de resolução de problemas focando em falhas de comunicação, logs e credenciais.
*   **Auditoria Contínua e Monitoramento de Eventos (Event Viewer/SIEM):**
    *   Avaliação e monitoramento de falhas de Logon (Event IDs 4624, 4625, 4627).
    *   Solicitação de TGTs e falhas de pré-autenticação Kerberos (Event IDs 4768, 4771).
    *   Anomalias em solicitações de Service Tickets (Event ID 4769) apontando para indícios de PtT ou Kerberoasting.
*   **Diagnóstico e Soluções para Códigos de Erro Específicos:**
    *   Erros de Identificação (SPN duplicado/ausente): `KDC_ERR_S_PRINCIPAL_UNKNOWN` e `KDC_ERR_PRINCIPAL_NOT_UNIQUE`.
    *   Erros de Relógio (Clock Skew) e Encriptação: `KRB_AP_ERR_SKEW`, `KDC_ERR_ETYPE_NOTSUPP` e `KRB_AP_ERR_MODIFIED`.
*   **Ferramentas Práticas de Inspeção:** Utilização do Wireshark para captura de pacotes, comando nativo `klist` para diagnóstico e limpeza da cache de tickets, e correlacionadores de eventos.
*   **Problemas Frequentes:** Resolução de impasses associados a entradas DNS incorretas, falta de sincronização NTP e expiração inadvertida de Keytabs.