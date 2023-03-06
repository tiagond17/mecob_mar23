# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

app_name = 'home'

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    
    path("consulta_por_data",views.consulta_por_data, name="consulta_por_data"),
    path("criar_cad_cliente",views.criar_cad_cliente, name="criar_cad_cliente"),
    path('criar_novo_cadastro_de_credito_e_debito', 
        views.criar_novo_cadastro_de_credito_e_debito,
        name="criar_novo_cadastro_de_credito_e_debito"
    ),
    path("criar_nova_taxa", views.criar_nova_taxa, name="criar_nova_taxa"),
    path("criar_novo_repasse_retido", 
        views.criar_novo_repasse_retido, 
        name="criar_novo_repasse_retido"
    ),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
