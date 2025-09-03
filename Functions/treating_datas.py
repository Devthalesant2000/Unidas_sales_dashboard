import pandas as pd
import requests
import streamlit as st


def treating_data(df):

    meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
    }

    unidad_df = df.copy()

    unidad_df_columns = ['Title','Cliente (Restored)','Current phase',
                        'Data de Faturamento','Representante','Representante Secundário',
                        'Etiquetas','Itens do Pedido','CNPJ emissor de NF ','Prazo de Pagamento',
                        'Tipo de NF ','Número da NF ','Valor Faturado']

    unidad_df = unidad_df[unidad_df_columns]

    unidad_df = unidad_df.rename(columns={'Title':'Cliente',
                                        'Current phase':'Fase_do_pedido',
                                        'Data de Faturamento':'Data_do_pedido',
                                        'Cliente (Restored)':'CNPJ_cliente',
                                        'Etiquetas':'Empresa',
                                        'Itens do Pedido':'Produtos',
                                        'CNPJ emissor de NF ':'CNPJ_empresa',
                                        'Número da NF':'Nota_fiscal'})

    unidad_df['Data_do_pedido'] = pd.to_datetime(unidad_df['Data_do_pedido'])
    unidad_df['Mès_num'] = unidad_df['Data_do_pedido'].dt.month
    unidad_df['Mês_do_pedido'] = unidad_df['Mès_num'].map(meses)
    unidad_df['Data_do_pedido'] = unidad_df['Data_do_pedido'].dt.strftime("%d/%m/%y")

    unidad_df = unidad_df.sort_values(by='Mès_num')

    unidad_df['Prazo de Pagamento'] = unidad_df['Prazo de Pagamento'].replace('Outros (Descrever e justificar)','Outros')


    return unidad_df