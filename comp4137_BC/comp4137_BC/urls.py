"""comp4137_BC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blockchain import views as Bblockchain

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get_chain', Bblockchain.get_chain, name="get_chain"),
    path('mine_block', Bblockchain.mine_block, name="mine_block"),
    path('add_transaction', Bblockchain.add_transaction, name="add_transaction"), #New
    path('is_valid', Bblockchain.is_valid, name="is_valid"), #New
    path('connect_node', Bblockchain.connect_node, name="connect_node"), #New
    path('replace_chain', Bblockchain.replace_chain, name="replace_chain"), #New
]