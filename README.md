# CJAS-Python_dados

# CRONOGRAMA 

Março - teste do App
- De 15 de Março a 15 de Abril  - pré inscrição e mídias 
- 17 de Maio a 15 de julho - inscrições intensivas 
- 16 de julho a 15 de agosto - ajustes finais e o povo que deixa pra ultima hora 
- 1 de agosto a 30 de agosto - possivel lista de espera 
- até 8 de Setembro - preparação final de suporte para outros comitês 
- 1 Setembro a 4 de outubro - corrida com logistica e programação com as informações ja fechadas








# CÓDIGOS NO GOOGLE COLAB


Link do google colab: https://developers.google.com/colab

-> Ao entrar no site logue com sua conta do google e coloque em criar notebook.
-> Ele vai criar um espaço de trabalho e salvar no seu DRIVE

- import pandas as pd  // importar a biblioteca pandas no collab
- df = pd.read_csv("/content/nomedocsv")  // para ele ler o csv no computador
- df.shape  // para ver o número de linhas e colunas no csv (no caso pode ser importante para ver quantas pessoas tem no sistema)
- df.info()  // para ver o tipo de dado que a caixa recebe (caso aconteça de alguém não conseguir colocar uma informação -- não sei se funciona 100%, sujeito a testes kkkk)
- df.describe()  // para acessar uma tabela com essa legenda:
cout: Contagem das linhas
mean: Calculo da média 
std: desvio padrão 
min: valor minimo 
quartis de 25%, 50%, 75%
max: Valor máximo
- df.columns  // para aparecer as colunas do csv (ver as informações que o usuário tem para preencher)
- 
