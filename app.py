import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# 1. Criar dados de exemplo
df = pd.DataFrame({
    "Categoria": ["A", "B", "C", "D"],
    "Valor": [10, 20, 30, 40]
})

# 2. Criar gráfico
fig = px.bar(df, x="Categoria", y="Valor", title="Exemplo de Dashboard")

# 3. Inicializar o app
app = dash.Dash(__name__)

# 4. Definir layout
app.layout = html.Div(children=[
    html.H1("Meu Primeiro Dashboard em Python"),
    dcc.Graph(
        id="grafico-exemplo",
        figure=fig
    )
])

# 5. Rodar servidor
if __name__ == "__main__":
    app.run(debug=True)

