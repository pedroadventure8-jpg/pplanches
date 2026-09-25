import streamlit as st
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import io

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Comandas - PP Lanches", layout="wide")

# CSS Personalizado para Interface Visual Intuitiva
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-title { font-size: 26px; font-weight: 800; letter-spacing: 1px; margin: 0; color: #ffffff; }
    .header-sub { font-size: 14px; color: #94a3b8; margin-top: 4px; }
    
    .step-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05);
    }
    .step-badge {
        display: inline-block;
        background-color: #0284c7;
        color: #ffffff;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    .preview-card {
        background-color: #f1f5f9;
        border-left: 4px solid #0284c7;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .preview-title { font-size: 13px; font-weight: 700; color: #334155; }
    .preview-val { font-size: 18px; font-weight: 800; color: #0f172a; }
    
    .total-box {
        background: #0f172a;
        color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
        margin-top: 15px;
    }
    .total-title { font-size: 13px; text-transform: uppercase; color: #94a3b8; font-weight: 600; }
    .total-amount { font-size: 28px; font-weight: 800; color: #38bdf8; margin: 4px 0; }
    
    .troco-box {
        background: #064e3b;
        color: #ffffff;
        padding: 14px;
        border-radius: 8px;
        text-align: center;
        margin-top: 10px;
    }
    .troco-amount { font-size: 22px; font-weight: 800; color: #34d399; }
</style>
""", unsafe_allow_html=True)

# Cabeçalho da Aplicação
st.markdown("""
<div class="header-box">
    <div class="header-title">PASTELARIA E PIZZARIA PP LANCHES</div>
    <div class="header-sub">SISTEMA DE EMISSÃO DE COMANDAS E CONTROLE DE CAIXA | TEL: (88) 99905-0790</div>
</div>
""", unsafe_allow_html=True)

# Base de Dados do Cardápio
PASTEIS = {
    "4 queijos": {"P": 17.00, "G": 20.00}, "5 queijos": {"P": 18.00, "G": 21.00},
    "À moda da casa": {"P": 17.00, "G": 19.00}, "À moda do Chef": {"P": 17.00, "G": 19.00},
    "Americano": {"P": 16.00, "G": 18.00}, "Bacon": {"P": 16.00, "G": 20.00},
    "Bacon crocante": {"P": 16.00, "G": 19.00}, "Calabresa": {"P": 16.00, "G": 19.00},
    "Calabresa catupiry": {"P": 16.00, "G": 19.00}, "Campestre": {"P": 17.00, "G": 19.00},
    "Carne de Sol": {"P": 19.00, "G": 23.00}, "Carne de sol c/ cheddar": {"P": 19.00, "G": 23.00},
    "Carne moída": {"P": 15.00, "G": 18.00}, "Catarina": {"P": 16.00, "G": 19.00},
    "Charmoso": {"P": 18.00, "G": 21.00}, "Cheddar": {"P": 16.00, "G": 18.00},
    "Chester": {"P": 16.00, "G": 18.00}, "Chinês": {"P": 17.00, "G": 20.00},
    "Crocante": {"P": 16.00, "G": 19.00}, "Espanhol": {"P": 17.00, "G": 19.00},
    "Frango": {"P": 16.00, "G": 18.00}, "Frango catupiry": {"P": 16.00, "G": 18.00},
    "Frango cheddar": {"P": 16.00, "G": 18.00}, "Imperial": {"P": 18.00, "G": 20.00},
    "Italiano": {"P": 16.00, "G": 18.00}, "Mexicano": {"P": 16.00, "G": 18.00},
    "Milho": {"P": 16.00, "G": 19.00}, "Milho com bacon": {"P": 17.00, "G": 19.00},
    "Misto": {"P": 15.00, "G": 18.00}, "Mistão": {"P": 17.00, "G": 19.00},
    "Mistão catupiry": {"P": 18.00, "G": 20.00}, "Mistão cheddar": {"P": 18.00, "G": 20.00},
    "Nápolis": {"P": 17.00, "G": 20.00}, "Nordestino": {"P": 20.00, "G": 23.00},
    "Pastel Rei": {"P": 17.00, "G": 20.00}, "Paulista": {"P": 16.00, "G": 19.00},
    "Pizza": {"P": 16.00, "G": 18.00}, "Portuguesa": {"P": 17.00, "G": 19.00},
    "PP lanches": {"P": 18.00, "G": 20.00}, "Presunto": {"P": 16.00, "G": 18.00},
    "Queijo": {"P": 16.00, "G": 19.00}, "Super tudão": {"P": 20.00, "G": 22.00},
    "Toscano": {"P": 16.00, "G": 18.00}, "Tradicional": {"P": 16.00, "G": 18.00},
    "Tropical": {"P": 16.00, "G": 19.00}, "Tudão": {"P": 18.00, "G": 20.00}
}

PIZZA_PRECOS = {
    "P4 (4 fatias)": 35.00,
    "M8 (8 fatias)": 40.00,
    "G10 (10 fatias)": 47.00,
    "GG12 (12 fatias)": 52.00
}

PIZZA_SABORES = [
    "4 Queijos", "À Moda da Casa", "Atum", "Bacon", "Calabresa",
    "Calabresa c/ Catupiry", "Carne de Sol", "Carne de Sol c/ Catupiry",
    "Chicken Cheddar", "Frango c/ Catupiry", "Lombinho", "Margarita",
    "Mussarela", "Napolitana", "Palmito", "Paulista", "Pepperoni",
    "Portuguesa", "Sertaneja", "Stroganoff Frango", "Toscana"
]

PIZZA_BORDAS = {
    "Sem Borda": 0.00,
    "Borda Catupiry": 5.00,
    "Borda Cheddar": 5.00
}

# Inicialização de Sessão
if "num_comanda_seq" not in st.session_state:
    st.session_state.num_comanda_seq = 101
if "itens_pedido" not in st.session_state:
    st.session_state.itens_pedido = []
if "historico_pedidos" not in st.session_state:
    st.session_state.historico_pedidos = []

tab_caixa, tab_historico = st.tabs(["Emissão de Comandas", "Histórico de Vendas"])

with tab_caixa:
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        # ETAPA 1: ATENDIMENTO
        st.markdown("""
        <div class="step-card">
            <span class="step-badge">Passo 1</span>
            <h4 style="margin: 0 0 12px 0; color: #0f172a;">Dados do Atendimento</h4>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            num_comanda = st.number_input("Número da Comanda", min_value=1, value=st.session_state.num_comanda_seq, step=1)
            tipo_pedido = st.selectbox("Tipo de Atendimento", ["DELIVERY", "BALCÃO", "MESA"])
            nome_cliente = st.text_input("Nome do Cliente", value="Cliente Balcão")
        
        with c2:
            telefone_cliente = st.text_input("Telefone", value="(88) 99000-0000")
            forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito"])
            taxa_entrega = st.number_input("Taxa de Entrega (R$)", min_value=0.0, value=5.00 if tipo_pedido == "DELIVERY" else 0.0, step=1.0)
        
        if tipo_pedido == "DELIVERY":
            endereco_cliente = st.text_input("Endereço Completo de Entrega", value="Rua Central, 100")
        else:
            endereco_cliente = ""
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ETAPA 2: ADICIONAR PRODUTOS
        st.markdown("""
        <div class="step-card">
            <span class="step-badge">Passo 2</span>
            <h4 style="margin: 0 0 12px 0; color: #0f172a;">Adicionar Produtos ao Pedido</h4>
        """, unsafe_allow_html=True)
        
        categoria = st.radio("Selecione a Categoria", ["Pastel", "Pizza", "Bebida"], horizontal=True)
        
        if categoria == "Pastel":
            col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
            with col_p1:
                sabor_p = st.selectbox("Sabor do Pastel", list(PASTEIS.keys()))
            with col_p2:
                tam_p = st.radio("Tamanho", ["P", "G"], horizontal=True)
            with col_p3:
                qtd_p = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_p")
                
            obs_p = st.text_input("Observação (ex: sem cebola)", key="obs_p")
            unit_val = PASTEIS[sabor_p][tam_p]
            tot_val = unit_val * qtd_p
            
            st.markdown(f"""
            <div class="preview-card">
                <div class="preview-title">Pastel {sabor_p} ({tam_p}) x {qtd_p}</div>
                <div class="preview-val">Subtotal Item: R$ {tot_val:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Pastel ao Carrinho", use_container_width=True):
                st.session_state.itens_pedido.append({
                    "tipo": "Pastel",
                    "descricao": f"Pastel {sabor_p} ({tam_p})",
                    "quantidade": qtd_p,
                    "preco_unit": unit_val,
                    "total": tot_val,
                    "obs": obs_p
                })
                st.success("Pastel adicionado com sucesso.")

        elif categoria == "Pizza":
            col_z1, col_z2 = st.columns([1.5, 1])
            with col_z1:
                tam_z = st.selectbox("Tamanho da Pizza", list(PIZZA_PRECOS.keys()))
            with col_z2:
                borda_z = st.selectbox("Borda Recheada", list(PIZZA_BORDAS.keys()))
                
            max_sabores = 4 if "GG12" in tam_z else 3
            qtd_sabores = st.number_input(f"Quantidade de Sabores (máx {max_sabores})", min_value=1, max_value=max_sabores, value=1, step=1)
            
            cols_s = st.columns(qtd_sabores)
            sabores_escolhidos = []
            for i, col_s in enumerate(cols_s):
                with col_s:
                    sb = st.selectbox(f"Sabor {i+1}", PIZZA_SABORES, key=f"pizza_sabor_{i}")
                    sabores_escolhidos.append(sb)
            
            qtd_z = st.number_input("Quantidade de Pizzas", min_value=1, value=1, step=1, key="qtd_z")
            obs_z = st.text_input("Observação da Pizza", key="obs_z")
            
            preco_base = PIZZA_PRECOS[tam_z]
            preco_borda = PIZZA_BORDAS[borda_z]
            unit_z = preco_base + preco_borda
            tot_z = unit_z * qtd_z
            
            desc_sabores = " / ".join(sabores_escolhidos)
            desc_completa = f"Pizza {tam_z} [{desc_sabores}]"
            if borda_z != "Sem Borda":
                desc_completa += f" c/ {borda_z}"
                
            st.markdown(f"""
            <div class="preview-card">
                <div class="preview-title">{desc_completa} x {qtd_z}</div>
                <div class="preview-val">Subtotal Item: R$ {tot_z:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Pizza ao Carrinho", use_container_width=True):
                st.session_state.itens_pedido.append({
                    "tipo": "Pizza",
                    "descricao": desc_completa,
                    "quantidade": qtd_z,
                    "preco_unit": unit_z,
                    "total": tot_z,
                    "obs": obs_z
                })
                st.success("Pizza adicionada com sucesso.")

        elif categoria == "Bebida":
            col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
            with col_b1:
                nome_b = st.text_input("Nome da Bebida", value="Coca-Cola 2L")
            with col_b2:
                unit_b = st.number_input("Preço Unitário (R$)", min_value=0.0, value=12.00, step=1.0)
            with col_b3:
                qtd_b = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_b")
                
            obs_b = st.text_input("Observação (ex: bem gelada)", key="obs_b")
            tot_b = unit_b * qtd_b
            
            st.markdown(f"""
            <div class="preview-card">
                <div class="preview-title">Bebida: {nome_b} x {qtd_b}</div>
                <div class="preview-val">Subtotal Item: R$ {tot_b:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Bebida ao Carrinho", use_container_width=True):
                st.session_state.itens_pedido.append({
                    "tipo": "Bebida",
                    "descricao": f"Bebida: {nome_b}",
                    "quantidade": qtd_b,
                    "preco_unit": unit_b,
                    "total": tot_b,
                    "obs": obs_b
                })
                st.success("Bebida adicionada com sucesso.")
                
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # ETAPA 3: RESUMO E FECHAMENTO
        st.markdown("""
        <div class="step-card">
            <span class="step-badge">Passo 3</span>
            <h4 style="margin: 0 0 12px 0; color: #0f172a;">Itens no Carrinho</h4>
        """, unsafe_allow_html=True)
        
        if not st.session_state.itens_pedido:
            st.info("Nenhum produto adicionado ao pedido ainda.")
        else:
            for idx, item in enumerate(st.session_state.itens_pedido):
                col_i1, col_i2 = st.columns([3.5, 1])
                with col_i1:
                    st.write(f"**{item['quantidade']}x {item['descricao']}** - R$ {item['total']:.2f}")
                    if item['obs']:
                        st.caption(f"Obs: {item['obs']}")
                with col_i2:
                    if st.button("Remover", key=f"del_{idx}"):
                        st.session_state.itens_pedido.pop(idx)
                        st.rerun()
                st.divider()
                
            if st.button("Esvaziar Carrinho"):
                st.session_state.itens_pedido = []
                st.rerun()
                
        subtotal = sum(item["total"] for item in st.session_state.itens_pedido)
        total_geral = subtotal + taxa_entrega
        
        st.markdown(f"""
        <div class="total-box">
            <div class="total-title">Total Final a Pagar</div>
            <div class="total-amount">R$ {total_geral:.2f}</div>
            <div style="font-size: 12px; color: #94a3b8;">Subtotal: R$ {subtotal:.2f} | Taxa: R$ {taxa_entrega:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        valor_pago = total_geral
        troco = 0.0
        
        if forma_pagamento == "Dinheiro":
            st.write("")
            valor_pago = st.number_input("Valor Recebido do Cliente (R$)", min_value=total_geral, value=max(total_geral, 50.0), step=5.0)
            troco = valor_pago - total_geral
            st.markdown(f"""
            <div class="troco-box">
                <div style="font-size: 11px; text-transform: uppercase;">Troco a Devolver</div>
                <div class="troco-amount">R$ {troco:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # GERAÇÃO DO PDF TÉRMICO
        def gerar_pdf_comanda():
            buffer = io.BytesIO()
            width = 58 * mm
            height = 240 * mm
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
                linha = f"{item['quantidade']}x {item['descricao']}"
                table_data.append([
                    Paragraph(linha, style_left),
                    Paragraph(f"R$ {item['total']:.2f}", style_right)
                ])
                if item['obs']:
                    table_data.append([
                        Paragraph(f"&nbsp;&nbsp;* {item['obs']}", style_obs),
                        Paragraph("", style_right)
                    ])

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

            totals_data = [
                [Paragraph("Subtotal:", style_left), Paragraph(f"R$ {subtotal:.2f}", style_right)]
            ]
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
                elements.append(Paragraph(f"<b>Valor Recebido:</b> R$ {valor_pago:.2f}", style_left))
                elements.append(Paragraph(f"<b>TROCO:</b> R$ {troco:.2f}", style_left_bold))

            elements.append(Spacer(1, 4))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#000000'), spaceBefore=2, spaceAfter=2))
            elements.append(Paragraph("Obrigado pela preferência!", style_center))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        st.write("")
        if st.session_state.itens_pedido:
            pdf_bytes = gerar_pdf_comanda()
            if st.download_button(
                label="Baixar Comanda em PDF (58mm)",
                data=pdf_bytes,
                file_name=f"comanda_{num_comanda:04d}.pdf",
                mime="application/pdf",
                use_container_width=True
            ):
                st.session_state.historico_pedidos.append({
                    "comanda": num_comanda,
                    "cliente": nome_cliente,
                    "tipo": tipo_pedido,
                    "total": total_geral,
                    "pagamento": forma_pagamento
                })
                st.session_state.num_comanda_seq += 1
                st.success("Comanda gerada e adicionada ao histórico de vendas.")

        st.markdown("</div>", unsafe_allow_html=True)

with tab_historico:
    st.subheader("Histórico de Vendas da Sessão")
    if not st.session_state.historico_pedidos:
        st.info("Nenhuma comanda emitida nesta sessão ainda.")
    else:
        st.dataframe(st.session_state.historico_pedidos, use_container_width=True)
