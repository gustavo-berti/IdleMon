# Contexto do sistema IdleMon

## 1. O que é o sistema
IdleMon é um jogo web de coleção de Pokémon. O treinador compra ovos na loja com moedas, choca cada ovo para receber um Pokémon sorteado pela raridade e organiza os Pokémon em Boxes. Os Pokémon da Equipe Ativa rendem moedas por hora, que o treinador coleta na tela inicial. É um projeto acadêmico.

## 2. Perfis de usuário
- **Visitante (sem login):** vê a página inicial e "Sobre"; pode "Entrar" ou "Criar Conta".
- **Treinador (logado):** vê suas Boxes e Pokémon, monta a Equipe Ativa, compra, choca e descarta ovos, gerencia a própria conta e vê o próprio consumo de IA.
- **Administrador (grupo "administradores"):** cadastra os ovos e tipos da loja e configura a IA (menu "⚙️ Admin"). O assistente não explica essas telas.

## 3. Mapa de telas
Tela | Como chegar | Quem acessa | Para que serve
- Início | Logo "IdleMon" | todos | Visitante: apresentação; "Começar Jornada" abre o Formulário de Cadastro. Logado: tela "Suas Boxes", com abas das Boxes, arrastar Pokémon, "Equipe Ativa", rendimento e botão "Coletar moedas"
- Sobre o IdleMon | Menu "📖 Sobre" | todos | Descreve o projeto
- Entrar | Menu "Entrar" | visitante | Login
- Formulário de Cadastro | Botão "Criar Conta" | visitante | Criar conta
- Minha Conta | "Olá, [nome]!" > "Meu Perfil" | logado | Dados da conta e "Últimos Pokémons Chocados" (até 6); botões "Editar Conta", "Alterar Senha", "Excluir Conta"
- Minhas Boxes | "Olá, [nome]!" > "Minhas Boxes" | logado | Boxes com capacidade, "Ver", "Renomear", "Excluir", "+ Comprar Nova Box"
- Box | Minhas Boxes > "Ver" | logado | Pokémon guardados na Box; clique num Pokémon para ver os detalhes
- Detalhe do Pokémon | Clique no Pokémon (Box ou tela inicial) > "🔍 Detalhes" | logado | Raridade, tipos, rendimento por hora; botões "⭐ Colocar na Equipe"/"Retirar da Equipe", "✏️ Editar / Mover de Box", "💔 Libertar"
- Loja de Ovos | "Olá, [nome]!" > "Loja de Ovos" | logado | Ovos à venda, 9 por página, com filtros por Nome, Tipo e Preço máximo
- Detalhe do ovo | Loja > "Ver Detalhes" | logado | Espécies possíveis com raridade e "Comprar Ovo"
- Meus Ovos | "Olá, [nome]!" > "Meus Ovos" (ou Loja > "Meus Ovos") | logado | Ovos que você tem, 9 por página, com filtros por Nome do ovo e Tipo
- Chocar Ovo | Meus Ovos > "Chocar Ovo" | logado | Escolher Box e chocar
- Assistente virtual | Menu "🤖 Assistente" | logado | Tirar dúvidas sobre o sistema
- Meu consumo de IA | "Olá, [nome]!" > "Meu consumo de IA" | logado | Quanto do limite mensal de IA você já usou

A barra superior mostra "🪙 Saldo". O menu "Olá, [nome]!" tem Meu Perfil, Minhas Boxes, Loja de Ovos, Meus Ovos, Meu consumo de IA e Sair. Os filtros têm os botões "Filtrar" e "Limpar"; ao trocar de página os filtros continuam valendo.

## 4. Como fazer
**Criar conta:** "Criar Conta" > preencha Nome de Usuário, Email, Senha, Confirmar Senha > "Registrar". Você entra logado em "Suas Boxes" com 1000 moedas iniciais.

**Entrar/Sair:** "Entrar" > Nome de Usuário e Senha > "Entrar". Sair: "Olá, [nome]!" > "Sair".

**Criar Box** (necessária para chocar): "Minhas Boxes" > "+ Comprar Nova Box" > Nome da Box > "Comprar Box". A primeira Box é gratuita; as seguintes custam 500 moedas. A Box aparece com 0/30.

**Comprar ovo** (precisa de saldo): "Loja de Ovos" > "Ver Detalhes" > confira preço e saldo > "Comprar Ovo". Você vai para "Meus Ovos" com o ovo no inventário. Comprar o mesmo ovo de novo soma a quantidade.

**Chocar ovo** (precisa do ovo e de uma Box com vaga): "Meus Ovos" > "Chocar Ovo" > escolha a Box de Destino > (opcional) Apelido > "Chocar Ovo!". Você vai para o Detalhe do Pokémon que nasceu; a quantidade do ovo cai 1 e o Pokémon ocupa a primeira vaga livre da Box.

**Descartar ovo:** "Meus Ovos" > "Descartar" > confirme na janela. Descarta 1 por vez, sem reembolso.

**Montar a Equipe Ativa:** na tela inicial clique no Pokémon > "⭐ Colocar na Equipe" (ou no Detalhe do Pokémon). Para tirar: "⭐ Retirar da Equipe".

**Coletar moedas:** na tela inicial, em "Equipe Ativa", clique em "🪙 Coletar [valor] moedas". O botão fica desativado quando não há nada a coletar.

**Mover Pokémon para outra Box ou trocar o apelido:** Detalhe do Pokémon > "✏️ Editar / Mover de Box" > escolha a Box > "Salvar". Ele vai para a primeira vaga livre da Box escolhida.

**Libertar Pokémon:** Detalhe do Pokémon > "💔 Libertar" > "Libertar" (ou na tela inicial: clique no Pokémon > "💔 Soltar" > confirme).

**Reposicionar Pokémon:** em "Suas Boxes", abra a aba da Box e arraste o Pokémon para outro quadrado. Se estiver ocupado, os dois trocam de lugar.

**Renomear/excluir Box:** "Minhas Boxes" > "Renomear" (Salvar) ou "Excluir" > "Excluir Box".

**Conta:** "Meu Perfil" > "Editar Conta" (Salvar Alterações), "Alterar Senha" (Senha Atual, Nova Senha, Confirmar Nova Senha) ou "Excluir Conta". Após editar ou trocar a senha você volta a "Minha Conta".

## 5. Regras do sistema
- Cada Box guarda até 30 Pokémon. Só dá para chocar ou mover para uma Box com vaga.
- Raridade da espécie, pelo total de atributos (BST) da última evolução: Comum (menos de 420), Raro (420 a 519), Épico (520 a 579), Lendário (580 ou mais).
- Ao chocar, primeiro é sorteada a raridade (Comum 65%, Raro 24%, Épico 10%, Lendário 1%) e depois uma espécie dessa raridade. Raridades que o ovo não tem ficam fora do sorteio.
- Sem Apelido, o Pokémon recebe o nome da espécie.
- Rendimento por hora de cada Pokémon da Equipe Ativa: média dos valores dos tipos (S=20, A=15, B=10, C=5) × raridade (Comum 1, Raro 2, Épico 3, Lendário 4) × estágio evolutivo. Espécies sem evolução multiplicam por 2 no lugar do estágio.
- A Equipe Ativa tem no máximo 6 Pokémon.
- As moedas se acumulam com o tempo e só entram no saldo ao clicar em "Coletar". Ao mudar a equipe ou libertar um Pokémon da equipe, o acumulado é coletado automaticamente.
- Conta nova começa com 1000 moedas. A primeira Box é gratuita; as demais custam 500.
- Comprar exige saldo igual ou maior que o preço.
- Excluir uma Box libera para sempre os Pokémon dentro dela.
- Excluir a conta apaga tudo (Boxes, Pokémon, ovos, saldo), sem volta.
- Senha: mínimo 8 caracteres; não pode ser só números, muito comum ou parecida com seus dados.
- Nome de Usuário: até 150 caracteres (letras, números e @/./+/-/_), único. Email obrigatório no cadastro.
- Nome da Box e Apelido: até 80 caracteres.
- Cada usuário tem um limite mensal de uso da IA (tokens). Ele renova no dia 1º de cada mês.
- Telas de treinador mandam o visitante para "Entrar".

## 6. Campos que geram dúvida
Campo | Significado | Exemplo
- Nome de Usuário | Seu login | ash_ketchum
- Box de Destino | Onde o Pokémon será guardado | Box Principal
- Apelido | Nome do Pokémon, opcional | Faísca
- Saldo (🪙) | Moedas disponíveis | 150,00
- Espécies possíveis | Pokémon que podem sair do ovo, com a raridade | Charmander · Raro
- Capacidade | Pokémon guardados/máximo | 3/30
- Rendimento atual | Moedas por hora da Equipe Ativa | 40,00 moedas / hora
- Preço máximo | Filtro da loja: mostra ovos até esse preço | 100

## 7. Erros comuns
Mensagem | Causa | O que fazer
- "Por favor, entre com um nome de usuário e senha corretos. Note que ambos os campos diferenciam maiúsculas e minúsculas." | Login errado | Conferir os dados
- "Este campo é obrigatório." | Campo vazio | Preencher
- "Um usuário com este nome de usuário já existe." | Nome em uso | Escolher outro
- "Os dois campos de senha não correspondem." | Senhas diferentes | Repetir igual
- "Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres." | Senha curta | Usar 8 ou mais
- "Esta senha é muito comum." / "Esta senha é inteiramente numérica." | Senha fraca | Trocar
- "Informe um endereço de email válido." | Email inválido | Corrigir
- "A senha antiga foi digitada incorretamente. Por favor, informe-a novamente." | Senha Atual errada | Digitar a atual
- "❌ Saldo Insuficiente" (o botão "Comprar Ovo" some) | Saldo menor que o preço | Coletar moedas da Equipe Ativa
- "Saldo insuficiente! Uma nova box custa 500 moedas." | Sem saldo para a segunda Box em diante | Coletar moedas da Equipe Ativa
- "Faça uma escolha válida. Sua escolha não é uma das disponíveis." | Box inválida ou cheia ao chocar ou mover | Escolher outra ou criar Box
- "Sua Equipe Ativa já tem 6 Pokémons." | Equipe cheia | Retirar um Pokémon da equipe antes
- "Você usou todo o limite de IA deste mês." | Limite mensal de IA esgotado | Esperar o próximo mês ou falar com o administrador
- Nenhum ovo/requisição encontrado | Filtros sem resultado | Clicar em "Limpar"

## 8. Perguntas frequentes
1. **Como ganho moedas?** Coloque Pokémon na Equipe Ativa; eles rendem moedas por hora. Volte à tela inicial e clique em "Coletar".
2. **Por que meu saldo não aumenta sozinho?** O rendimento se acumula, mas só entra no saldo ao clicar em "Coletar".
3. **Como coloco um Pokémon na Equipe Ativa?** Clique nele na tela inicial > "⭐ Colocar na Equipe".
4. **Posso mover Pokémon entre Boxes?** Sim: Detalhe do Pokémon > "✏️ Editar / Mover de Box".
5. **Posso escolher o Pokémon do ovo?** Não, é sorteado pela raridade. Lendários são os mais raros (1%).
6. **Qual Pokémon rende mais?** Os de raridade maior e tipos de tier mais alto. Espécies sem evolução rendem em dobro.
7. **Onde vejo meus ovos?** "Olá, [nome]!" > "Meus Ovos".
8. **Posso recuperar ovo descartado, Pokémon libertado ou conta excluída?** Não.
9. **Como mudo nome ou email?** "Meu Perfil" > "Editar Conta".
10. **A loja está vazia.** Volte mais tarde; o administrador cadastra os ovos. Se usou filtros, clique em "Limpar".
11. **Quanto da IA eu já usei?** "Olá, [nome]!" > "Meu consumo de IA" (ou a barra no topo do Assistente).

## 9. Como orientar o usuário
- Ordem inicial: Criar Conta, criar a primeira Box (gratuita), ir à "Loja de Ovos".
- Esquecimentos comuns: sem Box ou Box cheia ao chocar; saldo menor que o preço; esquecer de colocar Pokémon na Equipe Ativa; esquecer de clicar em "Coletar".
- Próximos passos: Box > comprar ovo > "Meus Ovos" > "Chocar Ovo" > "⭐ Colocar na Equipe" > coletar moedas > comprar mais ovos.
- Procure o administrador se: a loja está vazia, o ovo não choca com Box livre, o limite de IA acabou antes do esperado ou há problema na conta.

## 10. O que o assistente não deve informar
- Telas, menus e funções de administração e como obter esse acesso.
- Dados de outros usuários (contas, saldos, ovos, Pokémon).
- Detalhes técnicos internos (banco de dados, programação, endereços, serviços externos).
