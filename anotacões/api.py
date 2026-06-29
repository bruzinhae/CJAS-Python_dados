import requests
import pandas as pd
from bs4 import BeautifulSoup


BASE_URL = "https://backend.cometogether.ar"

SEARCH_URL = f"{BASE_URL}/admin/participant/search"


class ComeTogetherAPI:

    def __init__(self):
        self.session = requests.Session()

    ###############################################################
    # LOGIN
    ###############################################################

    def login(self, email, password):
        """
        IMPLEMENTAR DEPOIS.
        Ainda precisamos descobrir qual endpoint o sistema usa.
        """

        # Exemplo (será alterado depois)

        # self.session.get(BASE_URL + "/login")

        # self.session.post(
        #     BASE_URL + "/login",
        #     data={
        #         "email": email,
        #         "password": password
        #     }
        # )

        pass

    ###############################################################
    # Remove HTML
    ###############################################################

    @staticmethod
    def limpar(html):

        if html is None:
            return ""

        return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

    ###############################################################
    # Busca uma página
    ###############################################################

    def buscar_pagina(self, start=0, length=500):

        payload = {

            "draw": 1,

            "start": start,

            "length": length,

            "search[value]": "",

            "search[regex]": "false",

            "totalEntryCount": ""

        }

        resposta = self.session.post(

            SEARCH_URL,

            data=payload,

            headers={
                "X-Requested-With": "XMLHttpRequest"
            }

        )

        resposta.raise_for_status()

        return resposta.json()

    ###############################################################
    # Busca todos participantes
    ###############################################################

    def buscar_participantes(self):

        participantes = []

        start = 0

        length = 500

        while True:

            json = self.buscar_pagina(start, length)

            linhas = json["data"]

            if len(linhas) == 0:
                break

            for row in linhas:

                participantes.append({

                    "regiao": self.limpar(row[1]),

                    "nome": self.limpar(row[2]),

                    "sobrenome": self.limpar(row[3]),

                    "estaca": self.limpar(row[4]),

                    "ala": self.limpar(row[5]),

                    "status": self.limpar(row[6]),

                    "data_inscricao": self.limpar(row[7]),

                    "checkin": self.limpar(row[8])

                })

            start += length

            print(f"{len(participantes)} participantes carregados...")

        return pd.DataFrame(participantes)


###############################################################
# Função usada pelo Streamlit
###############################################################

def carregar_dados():

    api = ComeTogetherAPI()

    # depois será:
    # api.login(email, senha)

    df = api.buscar_participantes()

    return df