import streamlit as st
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import io
import datetime
import pandas as pd

# Título e Configuração da Página
st.set_page_config(page_title="Gestao de Comandas - PP Lanches", layout="centered")

st.title("PP Lanches - Sistema de Comandas (58mm)")
st.caption("Pastelaria & Pizzaria PP Lanches | Tel: (88) 99905-0790")

# 1. Base de Dados do Cardápio
CARDAPIO_PASTEIS = {
    "4 queijos": {"P": 17.00, "G": 20.00},
    "5 queijos": {"P": 18.00, "G": 21.00},
    "À moda da casa": {"P": 17.00, "G": 19.00},
    "À moda do Chef": {"P": 17.00, "G": 19.00},
    "Americano": {"P": 16.00, "G": 18.00},
    "Bacon": {"P": 16.00, "G": 20.00},
    "Bacon crocante": {"P": 16.00, "G": 19.00},
    "Calabresa": {"P": 16.00, "G": 19.00},
    "Calabresa catupiry": {"P": 16.00, "G": 19.00},
    "Campestre": {"P": 17.00, "G": 19.00},
    "Carne de Sol": {"P": 19.00, "G": 23.00},
    "Carne de sol c/ cheddar": {"P": 19.00, "G": 23.00},
    "Carne moída": {"P": 15.00, "G": 18.00},
    "Catarina": {"P": 16.00, "G": 19.00},
    "Charmoso": {"P": 18.00, "G": 21.00},
    "Cheddar": {"P": 16.00, "G": 18.00},
    "Chester": {"P": 16.00, "G": 18.00},
    "Chinês": {"P": 17.00, "G": 20.00},
    "Crocante": {"P": 16.00, "G": 19.00},
    "Espanhol": {"P": 17.00, "G": 19.00},
    "Frango": {"P": 16.00, "G": 18.00},
    "Frango catupiry": {"P": 16.00, "G": 18.00},
    "Frango cheddar": {"P": 16.00, "G": 18.00},
    "Imperial": {"P": 18.00, "G": 20.00},
    "Italiano": {"P": 16.00, "G": 18.00},
    "Mexicano": {"P": 16.00, "G": 18.00},
    "Milho": {"P": 16.00, "G": 19.00},
    "Milho com bacon": {"P": 17.00, "G": 19.00},
    "Misto": {"P": 15.00, "G": 18.00},
    "Mistão": {"P": 17.00, "G": 19.00},
    "Mistão catupiry": {"P": 18.00, "G": 20.00},
    "Mistão cheddar": {"P": 18.00, "G": 20.00},
    "Nápolis": {"P": 17.00, "G": 20.00},
    "Nordestino": {"P": 20.00, "G": 23.00},
    "Pastel Rei": {"P": 17.00, "G": 20.00},
    "Paulista": {"P": 16.00, "G": 19.00},
    "Pizza": {"P": 16.00, "G": 18.00},
    "Portuguesa": {"P": 17.00, "G": 19.00},
    "PP lanches": {"P": 18.00, "G": 20.00},
    "Presunto": {"P": 16.00, "G": 18.00},
    "Queijo": {"P": 16.00, "G": 19.00},
    "Super tudão": {"P": 20.00, "G": 22.00},
    "Toscano": {"P": 16.00, "G": 18.00},
    "Tradicional": {"P": 16.00, "G": 18.00},
    "Tropical": {"P": 16.00, "G": 19.00},
    "Tudão": {"P": 18.00, "G": 20.00}
}

PRECOS_PIZZA_TAMANHO = {
    "P4 (4 fatias)": 35.00,
    "M8 (8 fatias)": 40.00,
    "G10 (10 fatias)": 47.00,
    "GG12 (12 fatias)": 52.00
}

SABORES_PIZZA = [
    "Muçarela", "Calabresa", "Margarita", "Frango c/ Catupiry",
    "Carne de Sol c/ Catupiry", "Sertaneja", "4 Queijos", "5 Queijos",
    "Bacon", "Portuguesa", "Napolitana", "Toscana", "Atum", "Palmito",
    "Lombinho", "Vegetariana", "Pepperoni", "Chocolate", "Laka", "Prestígio", "Banana c/ Canela"
]

BORDAS_PIZZA = {
    "Sem Borda": 0.00,
    "Borda Catupiry": 5.00,
    "Borda Cheddar": 5.00
}

# Inicialização de Session State
if "historico_pedidos" not in st.session_state:
    st.session_state.historico_pedidos = []

if "num_comanda_seq" not in st.session_state:
    st.session_state.num_comanda_seq = 101

if "itens_pedido" not in st.session_state:
    st.session_state.itens_pedido = []

# Tentar Conexão com Google Sheets se configurado em st.secrets
use_gsheets = False
gsheets_conn = None

try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        from streamlit_gsheets import GSheetsConnection
        gsheets_conn = st.connection("gsheets", type=GSheetsConnection)
        use_gsheets = True
except Exception:
    use_gsheets = False

# Abas Principais
tab_emissao, tab_historico, tab_config = st.tabs(["Nova Comanda", "Histórico de Vendas", "Configuração Google Sheets"])

with tab_emissao:
    st.subheader("1. Dados do Atendimento")
    col1, col2 = st.columns(2)
    with col1:
        num_comanda = st.number_input("Número da Comanda", min_value=1, value=st.session_state.num_comanda_seq, step=1)
        tipo_pedido = st.selectbox("Tipo de Pedido", ["BALCÃO", "DELIVERY", "MESA"])
        nome_cliente = st.text_input("Nome do Cliente", value="Cliente")
    with col2:
        telefone_cliente = st.text_input("Telefone", value="")
        forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito"])
        taxa_entrega = st.number_input("Taxa de Entrega (R$)", min_value=0.0, value=5.00 if tipo_pedido == "DELIVERY" else 0.0, step=1.0) if tipo_pedido == "DELIVERY" else 0.0

    endereco_cliente = st.text_input("Endereço Completo", value="") if tipo_pedido == "DELIVERY" else ""

    st.markdown("---")
    st.subheader("2. Adicionar Produtos ao Pedido")

    categoria = st.radio("Categoria do Item", ["Pastel", "Pizza", "Bebida"], horizontal=True)

    if categoria == "Pastel":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sabor_p = st.selectbox("Sabor do Pastel", list(CARDAPIO_PASTEIS.keys()))
        with c2:
            tam_p = st.radio("Tamanho", ["P", "G"], horizontal=True)
        with c3:
            qtd_p = st.number_input("Quantidade", min_value=1, value=1, step=1)

        obs_p = st.text_input("Observação (ex: sem cebola, extra milho)", value="", key="obs_p")
        preco_unit = CARDAPIO_PASTEIS[sabor_p][tam_p]
        st.info(f"Valor Unitário: R$ {preco_unit:.2f} | Subtotal Item: R$ {(preco_unit * qtd_p):.2f}")

        if st.button("Adicionar Pastel", use_container_width=True):
            st.session_state.itens_pedido.append({
                "categoria": "Pastel",
                "item": f"Pastel {sabor_p} ({tam_p})",
                "quantidade": qtd_p,
                "preco_unit": preco_unit,
                "total_item": preco_unit * qtd_p,
                "obs": obs_p
            })
            st.success("Pastel adicionado ao pedido!")

    elif categoria == "Pizza":
        c1, c2 = st.columns(2)
        with c1:
            tam_pizza = st.selectbox("Tamanho da Pizza", list(PRECOS_PIZZA_TAMANHO.keys()))
            sabor_pizza_1 = st.selectbox("Sabor 1", SABORES_PIZZA)
            meio_a_meio = st.checkbox("Pizza Meio a Meio?")
            sabor_pizza_2 = st.selectbox("Sabor 2", SABORES_PIZZA) if meio_a_meio else ""
        with c2:
            borda_pizza = st.selectbox("Borda Recheada", list(BORDAS_PIZZA.keys()))
            qtd_pizza = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_piz")

        obs_pizza = st.text_input("Observação da Pizza", value="", key="obs_piz")

        preco_base = PRECOS_PIZZA_TAMANHO[tam_pizza]
        preco_borda = BORDAS_PIZZA[borda_pizza]
        preco_unit_pizza = preco_base + preco_borda

        nome_item_pizza = f"Pizza {tam_pizza} - {sabor_pizza_1}"
        if meio_a_meio and sabor_pizza_2:
            nome_item_pizza += f" / {sabor_pizza_2}"
        if borda_pizza != "Sem Borda":
            nome_item_pizza += f" ({borda_pizza})"

        st.info(f"Valor Unitário: R$ {preco_unit_pizza:.2f} | Subtotal Item: R$ {(preco_unit_pizza * qtd_pizza):.2f}")

        if st.button("Adicionar Pizza", use_container_width=True):
            st.session_state.itens_pedido.append({
                "categoria": "Pizza",
                "item": nome_item_pizza,
                "quantidade": qtd_pizza,
                "preco_unit": preco_unit_pizza,
                "total_item": preco_unit_pizza * qtd_pizza,
                "obs": obs_pizza
            })
            st.success("Pizza adicionada ao pedido!")

    elif categoria == "Bebida":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            nome_bebida = st.text_input("Descrição da Bebida (ex: Coca-Cola 2L, Suco Laranja)", value="Coca-Cola 2L")
        with c2:
            preco_bebida = st.number_input("Preço Unitário (R$)", min_value=0.0, value=12.00, step=1.0)
        with c3:
            qtd_bebida = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_beb")

        obs_bebida = st.text_input("Observação (ex: gelada, sem gelo)", value="", key="obs_beb")

        st.info(f"Valor Unitário: R$ {preco_bebida:.2f} | Subtotal Item: R$ {(preco_bebida * qtd_bebida):.2f}")

        if st.button("Adicionar Bebida", use_container_width=True):
            st.session_state.itens_pedido.append({
                "categoria": "Bebida",
                "item": f"Bebida: {nome_bebida}",
                "quantidade": qtd_bebida,
                "preco_unit": preco_bebida,
                "total_item": preco_bebida * qtd_bebida,
                "obs": obs_bebida
            })
            st.success("Bebida adicionada ao pedido!")

    st.markdown("---")
    st.subheader("3. Resumo e Fechamento do Pedido")

    if st.session_state.itens_pedido:
        df_itens = pd.DataFrame(st.session_state.itens_pedido)
        st.dataframe(df_itens[["quantidade", "item", "obs", "preco_unit", "total_item"]], use_container_width=True)

        if st.button("Limpar Todos os Itens do Pedido"):
            st.session_state.itens_pedido = []
            st.rerun()

        subtotal = sum(i["total_item"] for i in st.session_state.itens_pedido)
        total_geral = subtotal + taxa_entrega

        st.markdown("---")
        c_tot1, c_tot2 = st.columns(2)

        with c_tot1:
            st.write(f"Subtotal dos Itens: R$ {subtotal:.2f}")
            if tipo_pedido == "DELIVERY":
                st.write(f"Taxa de Entrega: R$ {taxa_entrega:.2f}")
            st.markdown(f"### TOTAL A PAGAR: R$ {total_geral:.2f}")

        valor_pago = total_geral
        troco = 0.0

        with c_tot2:
            if forma_pagamento == "Dinheiro":
                valor_pago = st.number_input("Valor Recebido em Dinheiro (R$)", min_value=total_geral, value=max(total_geral, 50.0), step=5.0)
                troco = valor_pago - total_geral
                st.markdown(f"### TROCO: R$ {troco:.2f}")

        # Gerar PDF 58mm
        def gerar_pdf_58mm():
            buffer = io.BytesIO()
            width = 58 * mm
            height = 250 * mm
            margin = 2.5 * mm
            usable_w = width - (2 * margin)

            doc = SimpleDocTemplate(
                buffer, pagesize=(width, height),
                leftMargin=margin, rightMargin=margin,
                topMargin=margin, bottomMargin=margin
            )

            styles = getSampleStyleSheet()
            style_header = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER, leading=14)
            style_sub = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER, leading=10)
            style_center = ParagraphStyle('C1', fontName='Helvetica', fontSize=7, alignment=TA_CENTER, leading=9)
            style_left = ParagraphStyle('L1', fontName='Helvetica', fontSize=7.5, leading=9.5)
            style_left_bold = ParagraphStyle('L2', fontName='Helvetica-Bold', fontSize=8, leading=10)
            style_num = ParagraphStyle('NUM', fontName='Helvetica-Bold', fontSize=11, alignment=TA_CENTER, leading=13)
            style_right = ParagraphStyle('R1', fontName='Helvetica', fontSize=7.5, alignment=TA_RIGHT, leading=9.5)
            style_right_bold = ParagraphStyle('R2', fontName='Helvetica-Bold', fontSize=8.5, alignment=TA_RIGHT, leading=10.5)
            style_obs = ParagraphStyle('O1', fontName='Helvetica-Oblique', fontSize=6.5, leading=8)

            elements = [
                Paragraph("PP LANCHES", style_header),
                Paragraph("PASTELARIA & PIZZARIA", style_sub),
                Paragraph("Tel: (88) 99905-0790", style_center),
                HRFlowable(width="100%", thickness=0.8, color=HexColor('#000000'), spaceBefore=2, spaceAfter=3),
                Paragraph(f"<b>Nº DA COMANDA: #{num_comanda:04d}</b>", style_num),
                Paragraph(f"<b>TIPO:</b> {tipo_pedido}", style_left),
                HRFlowable(width="100%", thickness=0.5, color=HexColor('#000000'), spaceBefore=2, spaceAfter=2),
                Paragraph(f"<b>Cliente:</b> {nome_cliente}", style_left),
                Paragraph(f"<b>Tel:</b> {telefone_cliente}", style_left)
            ]

            if tipo_pedido == "DELIVERY" and endereco_cliente:
                elements.append(Paragraph(f"<b>Endereço:</b> {endereco_cliente}", style_left))

            elements.append(HRFlowable(width="100%", thickness=0.8, color=HexColor('#000000'), spaceBefore=3, spaceAfter=3))

            table_data = [[Paragraph("<b>QTD ITEM</b>", style_left), Paragraph("<b>TOTAL</b>", style_right)]]
            for item in st.session_state.itens_pedido:
                linha = f"{item['quantidade']}x {item['item']}"
                table_data.append([Paragraph(linha, style_left), Paragraph(f"R$ {item['total_item']:.2f}", style_right)])
                if item['obs']:
                    table_data.append([Paragraph(f"&nbsp;&nbsp;* {item['obs']}", style_obs), Paragraph("", style_right)])

            t_items = Table(table_data, colWidths=[usable_w * 0.72, usable_w * 0.28])
            t_items.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))
            elements.append(t_items)

            elements.append(HRFlowable(width="100%", thickness=0.8, color=HexColor('#000000'), spaceBefore=3, spaceAfter=3))

            totals_data = [[Paragraph("Subtotal:", style_left), Paragraph(f"R$ {subtotal:.2f}", style_right)]]
            if tipo_pedido == "DELIVERY":
                totals_data.append([Paragraph("Taxa Entrega:", style_left), Paragraph(f"R$ {taxa_entrega:.2f}", style_right)])
            totals_data.append([Paragraph("<b>TOTAL A PAGAR:</b>", style_left_bold), Paragraph(f"<b>R$ {total_geral:.2f}</b>", style_right_bold)])

            t_tot = Table(totals_data, colWidths=[usable_w * 0.55, usable_w * 0.45])
            t_tot.setStyle(TableStyle([
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))
            elements.append(t_tot)

            elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#000000'), spaceBefore=3, spaceAfter=3))
            elements.append(Paragraph(f"<b>Forma de Pagto:</b> {forma_pagamento}", style_left))
            if forma_pagamento == "Dinheiro":
                elements.append(Paragraph(f"<b>Recebido:</b> R$ {valor_pago:.2f}", style_left))
                elements.append(Paragraph(f"<b>TROCO:</b> R$ {troco:.2f}", style_left_bold))

            elements.append(Spacer(1, 4))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#000000'), spaceBefore=2, spaceAfter=2))
            elements.append(Paragraph("Obrigado pela preferência!", style_center))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_bytes = gerar_pdf_58mm()

        if st.download_button(
            label="Baixar Comanda para Impressão (58mm)",
            data=pdf_bytes,
            file_name=f"comanda_{num_comanda:04d}.pdf",
            mime="application/pdf",
            use_container_width=True
        ):
            # Registrar Venda
            agora_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resumo_itens = "; ".join([f"{i['quantidade']}x {i['item']}" for i in st.session_state.itens_pedido])

            novo_registro = {
                "DataHora": agora_str,
                "Comanda": f"#{num_comanda:04d}",
                "Tipo": tipo_pedido,
                "Cliente": nome_cliente,
                "Telefone": telefone_cliente,
                "Itens": resumo_itens,
                "Subtotal": subtotal,
                "Taxa": taxa_entrega,
                "Total": total_geral,
                "Pagamento": forma_pagamento,
                "Troco": troco
            }

            # Salvar em Session State
            st.session_state.historico_pedidos.append(novo_registro)

            # Salvar no Google Sheets se habilitado
            if use_gsheets and gsheets_conn is not None:
                try:
                    df_existente = gsheets_conn.read()
                    df_novo = pd.concat([df_existente, pd.DataFrame([novo_registro])], ignore_index=True)
                    gsheets_conn.update(data=df_novo)
                    st.toast("Pedido salvo na planilha do Google Sheets com sucesso!")
                except Exception as e:
                    st.warning(f"Salvo localmente. Erro ao gravar no Google Sheets: {e}")

            # Incrementar comanda e limpar itens
            st.session_state.num_comanda_seq += 1
            st.session_state.itens_pedido = []
            st.rerun()

    else:
        st.info("Nenhum item adicionado ao pedido ainda.")

with tab_historico:
    st.subheader("Relatório de Vendas e Histórico")

    # Carregar dados
    df_historico = pd.DataFrame()

    if use_gsheets and gsheets_conn is not None:
        try:
            df_historico = gsheets_conn.read()
            st.success("Conectado ao Google Sheets (Dados síncronos na nuvem)")
        except Exception:
            df_historico = pd.DataFrame(st.session_state.historico_pedidos)
    else:
        df_historico = pd.DataFrame(st.session_state.historico_pedidos)

    if not df_historico.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        total_vendas = df_historico["Total"].sum() if "Total" in df_historico.columns else 0.0
        qtd_pedidos = len(df_historico)
        ticket_medio = total_vendas / qtd_pedidos if qtd_pedidos > 0 else 0.0

        col_m1.metric("Faturamento Total", f"R$ {total_vendas:.2f}")
        col_m2.metric("Total de Pedidos", f"{qtd_pedidos}")
        col_m3.metric("Ticket Médio", f"R$ {ticket_medio:.2f}")

        st.markdown("---")
        st.dataframe(df_historico, use_container_width=True)

        csv = df_historico.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Relatório Completo em CSV",
            data=csv,
            file_name="historico_vendas_pp_lanches.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhuma venda registrada ainda.")

with tab_config:
    st.subheader("Como Conectar o Google Sheets (Histórico Permanente)")
    st.markdown("""
    Para garantir que o histórico **nunca apague** ao reiniciar a página, você pode conectar uma planilha do Google Sheets gratuita:

    1. Crie uma planilha no seu Google Drive com o nome **PP_Lanches_Vendas**.
    2. No Streamlit Community Cloud, vá em **Settings > Secrets** do seu aplicativo.
    3. Cole as credenciais da sua conta de serviço no seguinte formato:

    ```toml
    [connections.gsheets]
    spreadsheet = "https://docs.google.com/spreadsheets/d/SUA_PLANILHA_AQUI/edit"
    type = "service_account"
    project_id = "..."
    private_key_id = "..."
    private_key = "..."
    client_email = "..."
    client_id = "..."
    ```

    Após salvar os Secrets, o sistema começará a gravar e ler todos os pedidos diretamente do seu Google Sheets de forma automática!
    """)
