# HISTÓRIAS DE USUÁRIO - CETPVPFLIX

## 🎬 Projeto: Catálogo de Séries e Filmes

### **História 1: Autenticação e Visualização do Catálogo**
**Como** usuário do sistema  
**Quero** fazer login na plataforma  
**Para que** eu possa acessar o catálogo completo de filmes e séries com suas avaliações  

**Critérios de Aceitação:**
- [ ] Sistema de login/registro funcional
- [ ] Página principal exibe catálogo de filmes e séries
- [ ] Cada item mostra: título, poster, avaliação média, gênero
- [ ] Filtros por: gênero, ano, tipo (filme/série)
- [ ] Busca por título
- [ ] Paginação para grandes listas

---

### **História 2: Sistema de Avaliações**
**Como** usuário logado  
**Quero** avaliar filmes e séries  
**Para que** eu possa expressar minha opinião e ajudar outros usuários  

**Critérios de Aceitação:**
- [ ] Sistema de avaliação de 1 a 5 estrelas
- [ ] Comentários opcionais junto com a avaliação
- [ ] Exibição da média de avaliações dos usuários
- [ ] Impossibilidade de avaliar o mesmo conteúdo múltiplas vezes
- [ ] Edição/exclusão da própria avaliação

---

### **História 3: Lista Pessoal/Favoritos**
**Como** usuário logado  
**Quero** adicionar filmes e séries à minha lista pessoal  
**Para que** eu possa organizar meu conteúdo favorito  

**Critérios de Aceitação:**
- [ ] Botão "Adicionar aos Favoritos" em cada item
- [ ] Página "Minha Lista" mostrando favoritos
- [ ] Remoção de itens da lista pessoal
- [ ] Contador de itens na lista pessoal
- [ ] Status visual indicando se o item já está na lista

---

### **História 4: Solicitação de Conteúdo**
**Como** usuário logado  
**Quero** solicitar filmes/séries que não estão no catálogo  
**Para que** a plataforma possa expandir seu acervo  

**Critérios de Aceitação:**
- [ ] Formulário para sugerir novo conteúdo
- [ ] Campos: título, tipo (filme/série), ano, justificativa
- [ ] Lista de solicitações pendentes
- [ ] Status da solicitação (pendente/aprovada/rejeitada)
- [ ] Notificação quando solicitação for processada

---

### **História 5: Detalhes do Conteúdo**
**Como** usuário  
**Quero** ver informações detalhadas de filmes/séries  
**Para que** eu possa tomar decisões informadas sobre o que assistir  

**Critérios de Aceitação:**
- [ ] Página de detalhes com: sinopse, elenco, direção, trailers
- [ ] Galeria de imagens
- [ ] Lista de avaliações e comentários de outros usuários
- [ ] Informações técnicas (duração, ano, gêneros)
- [ ] Recomendações de conteúdo similar
- [ ] Integração com dados da TMDB API

## 🎨 **Especificações de Design**
- **Paleta de cores:** Branco, Preto, Laranja
- **Páginas:** Login, Catálogo Geral, Minha Lista, Detalhes do Item, Perfil
- **Responsivo:** Funcional em desktop e mobile