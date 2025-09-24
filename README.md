# Formula 1 Data Analytics 🏎️📊

Dashboard interativo de análise de dados históricos da Fórmula 1 (1950-2024), desenvolvido em **Streamlit**. Explore estatísticas de pilotos, equipes e circuitos, visualize vitórias, recordes e rankings de forma intuitiva e interativa.

---

## Principais Funcionalidades

- **Filtros dinâmicos** por ano, piloto, equipe e circuito
- **Abas interativas**: Pilotos, Equipes/Construtores, Circuitos
- **Gráficos interativos** com Plotly (barras, linhas, mapas)
- **Estatísticas detalhadas**: vitórias, títulos, recordes de volta, nacionalidades e muito mais
- **Mapa dos circuitos** com localização geográfica
- **Evolução histórica** de conquistas e recordes

---

## Como executar localmente

1. **Clone o repositório**
    ```bash
    git clone https://github.com/n4oji/f1-data-analytics.git
    cd f1-data-analytics
    ```

2. **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

3. **Execute o aplicativo Streamlit**
    ```bash
    streamlit run src/app.py
    ```

4. Acesse `http://localhost:8501` no seu navegador.

**Obs:** Os arquivos de dados CSV devem estar na pasta `/data` conforme já estruturado no projeto.

---

## Deploy Online

Você pode experimentar este dashboard online, sem instalar nada, através do [Streamlit Community Cloud](https://streamlit.io/cloud):

> **https://n4oji-f1-data-analytics-srcapp-foynp5.streamlit.app/**

---

## Estrutura do Projeto

```
.
├── data/            # Arquivos CSV com os dados da F1
├── src/
│   └── app.py       # Código principal do dashboard Streamlit
├── utils/           # Funções auxiliares (ex: cores, bandeiras)
├── requirements.txt # Dependências do projeto
└── README.md
```

---

## Requisitos

- Python 3.8+
- Streamlit
- Plotly
- Pandas

---

## Contribuição

Contribuições são bem-vindas! Sinta-se livre para abrir issues ou pull requests.

---

## Contato

Feito por [n4oji](https://github.com/n4oji)  
Dúvidas, sugestões ou feedback? Entre em contato pelo GitHub!

---

> *Este projeto é para fins educacionais e de portfólio. Não é afiliado à Fórmula 1.*
