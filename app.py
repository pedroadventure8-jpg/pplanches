import streamlit as st
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import io

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Comandas - PP Lanches", page_icon="🧾", layout="centered")

st.title("🧾 Gerador de Comandas (58mm)")
st.subheader("Pastelaria & Pizzaria PP Lanches")
st.caption("Tel: (88) 99905-0790 | Delivery & Balcão")

# 2. Base de Dados do Cardápio Completo (Preços P e G)
CARDAPIO = {
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

# Controle de Numeração da Comanda na sessão
if "num_comanda_seq" not in st.session_state:
    st.session_state.num_comanda_seq = 101

# 3. Formulário do Atendimento
st.markdown("---")
col_info1, col_info2 = st.columns(2)

with col_info1:
    num_comanda = st.number_input("Nº da Comanda", min_value=1, value=st.session_state.num_comanda_seq, step=1)
    tipo_pedido = st.selectbox("Tipo de Pedido", ["DELIVERY", "BALCÃO", "MESA"])
    nome_cliente = st.text_input("Nome do Cliente", value="João Silva")

with col_info2:
    telefone_cliente = st.text_input("Telefone", value="(88) 99888-1234")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito"])
    taxa_entrega = st.number_input("Taxa de Entrega (R$)", min_value=0.0, value=5.00, step=1.0) if tipo_pedido == "DELIVERY" else 0.0

endereco_cliente = st.text_input("Endereço Completo", value="Rua Principal, 123 - Centro") if tipo_pedido == "DELIVERY" else ""

st.markdown("### 🍕 Itens do Pedido")

if "itens_pedido" not in st.session_state:
    st.session_state.itens_pedido = []

col_item1, col_item2, col_item3 = st.columns([2, 1, 1])
with col_item1:
    sabor_sel = st.selectbox("Escolha o Pastel", list(CARDAPIO.keys()))
with col_item2:
    tam_sel = st.radio("Tamanho", ["P", "G"], horizontal=True)
with col_item3:
    qtd_sel = st.number_input("Qtd", min_value=1, value=1, step=1)

obs_sel = st.text_input("Observação do Item (opcional)", value="")

if st.button("➕ Adicionar Item ao Pedido", use_container_width=True):
    preco_unit = CARDAPIO[sabor_sel][tam_sel]
    st.session_state.itens_pedido.append({
        "sabor": sabor_sel,
        "tamanho": tam_sel,
        "quantidade": qtd_sel,
        "preco_unit": preco_unit,
        "total_item": preco_unit * qtd_sel,
        "obs": obs_sel
    })
    st.success(f"Adicionado: {qtd_sel}x {sabor_sel} ({tam_sel})")

# Tabela com itens selecionados
if st.session_state.itens_pedido:
    st.table([
        {
            "Qtd": item["quantidade"],
            "Item": f"{item['sabor']} ({item['tamanho']})",
            "Obs": item["obs"],
            "Unit.": f"R$ {item['preco_unit']:.2f}",
            "Total": f"R$ {item['total_item']:.2f}"
        }
        for item in st.session_state.itens_pedido
    ])
    
    if st.button("🗑️ Limpar Todos os Itens"):
        st.session_state.itens_pedido = []
        st.rerun()

# 4. Cálculo de Totais e Troco
subtotal = sum(item["total_item"] for item in st.session_state.itens_pedido)
total_geral = subtotal + taxa_entrega

st.markdown("---")
col_tot1, col_tot2 = st.columns(2)
with col_tot1:
    st.markdown(f"**Subtotal:** R$ {subtotal:.2f}")
    if tipo_pedido == "DELIVERY":
        st.markdown(f"**Taxa de Entrega:** R$ {taxa_entrega:.2f}")
    st.markdown(f"### **TOTAL A PAGAR: R$ {total_geral:.2f}**")

valor_pago = total_geral
troco = 0.0

with col_tot2:
    if forma_pagamento == "Dinheiro":
        valor_pago = st.number_input("Valor Recebido em Dinheiro (R$)", min_value=total_geral, value=max(total_geral, 50.0), step=5.0)
        troco = valor_pago - total_geral
        st.markdown(f"### **TROCO: R$ {troco:.2f}**")

# 5. Geração do PDF Térmico 58mm
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
    style_num_comanda = ParagraphStyle('NUM', fontName='Helvetica-Bold', fontSize=11, alignment=TA_CENTER, leading=13)
    style_right = ParagraphStyle('R1', fontName='Helvetica', fontSize=7.5, alignment=TA_RIGHT, leading=9.5)
    style_right_bold = ParagraphStyle('R2', fontName='Helvetica-Bold', fontSize=8.5, alignment=TA_RIGHT, leading=10.5)
    style_obs = ParagraphStyle('O1', fontName='Helvetica-Oblique', fontSize=6.5, leading=8)

    elements = [
        Paragraph("PP LANCHES", style_header),
        Paragraph("PASTELARIA & PIZZARIA", style_sub),
        Paragraph("Tel: (88) 99905-0790", style_center),
        HRFlowable(width="100%", thickness=0.8, color=HexColor('#000000'), spaceBefore=2, spaceAfter=3),
        Paragraph(f"<b>Nº DA COMANDA: #{num_comanda:04d}</b>", style_num_comanda),
        Paragraph(f"<b>TIPO:</b> {tipo_pedido}", style_left),
        HRFlowable(width="100%", thickness=0.5, color=HexColor('#000000'), spaceBefore=2, spaceAfter=2),
        Paragraph(f"<b>Cliente:</b> {nome_cliente}", style_left),
        Paragraph(f"<b>Tel:</b> {telefone_cliente}", style_left)
    ]

    if tipo_pedido == "DELIVERY" and endereco_cliente:
        elements.append(Paragraph(f"<b>Endereço:</b> {endereco_cliente}", style_left))

    elements.append(HRFlowable(width="100%", thickness=0.8, color=HexColor('#000000'), spaceBefore=3, spaceAfter=3))

    # Tabela de Itens
    table_data = [[Paragraph("<b>QTD ITEM</b>", style_left), Paragraph("<b>TOTAL</b>", style_right)]]
    for item in st.session_state.itens_pedido:
        linha_item = f"{item['quantidade']}x {item['sabor']} ({item['tamanho']})"
        table_data.append([
            Paragraph(linha_item, style_left),
            Paragraph(f"R$ {item['total_item']:.2f}", style_right)
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

    # Totais
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

    # Forma de Pagamento e Troco
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

if st.session_state.itens_pedido:
    pdf_buffer = gerar_pdf_comanda()
    if st.download_button(
        label="📄 Baixar Comanda para Impressão (58mm)",
        data=pdf_buffer,
        file_name=f"comanda_{num_comanda:04d}.pdf",
        mime="application/pdf",
        use_container_width=True
    ):
        st.session_state.num_comanda_seq += 1
