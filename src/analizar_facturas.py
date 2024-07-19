import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import locale
from datetime import datetime
import io
import json

def load_data(file):
    file_extension = file.name.split('.')[-1].lower()
    if file_extension == 'csv':
        df = pd.read_csv(file)
    elif file_extension == 'jsonl':
        json_list = [json.loads(line) for line in file]
        df = pd.DataFrame(json_list)
    else:
        st.error(f"Unsupported file format: {file_extension}")
        return None

    df['Date'] = pd.to_datetime(df['Date'])
    df['TotalAmount'] = pd.to_numeric(df['TotalAmount'], errors='coerce')
    df['VATTotal'] = pd.to_numeric(df['VATTotal'], errors='coerce')
    
    return df

def create_report(df, language='en'):
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8' if language == 'es' else 'en_US.UTF-8')
    
    titles = {
        'en': {
            'main': 'Invoice Analysis Report',
            'total_expenses': 'Total Expenses',
            'expenses_by_month': 'Expenses by Month',
            'expenses_by_company': 'Expenses by Company',
            'historical_trends': 'Historical Trends',
            'vat_analysis': 'VAT Analysis',
        },
        'es': {
            'main': 'Informe de Análisis de Facturas',
            'total_expenses': 'Gastos Totales',
            'expenses_by_month': 'Gastos por Mes',
            'expenses_by_company': 'Gastos por Empresa',
            'historical_trends': 'Tendencias Históricas',
            'vat_analysis': 'Análisis del IVA',
        }
    }


    # Total Expenses
    total_expenses = df['TotalAmount'].sum()
    
    # Expenses by Month
    monthly_expenses = df.groupby(df['Date'].dt.to_period('M'))['TotalAmount'].sum().reset_index()
    monthly_expenses['Date'] = monthly_expenses['Date'].dt.to_timestamp()
    
    # Expenses by Company
    company_expenses = df.groupby('Issuer')['TotalAmount'].sum().sort_values(ascending=True)
    
    # Historical Trends (Monthly aggregate total and per brand)
    historical_trends = df.groupby([df['Date'].dt.to_period('M'), 'Issuer'])['TotalAmount'].sum().unstack().fillna(0)
    historical_trends.index = historical_trends.index.to_timestamp()
    
    # VAT Analysis
    vat_analysis = df.groupby('Issuer').agg({'VATTotal': 'sum', 'TotalAmount': 'sum'}).reset_index()
    vat_analysis = vat_analysis.sort_values('TotalAmount', ascending=False)

    # Create the report
    fig = make_subplots(
        rows=4, cols=2,
        subplot_titles=[titles[language][key] for key in ['total_expenses', 'expenses_by_month', 'expenses_by_company', 'historical_trends', 'vat_analysis']],
        specs=[[{"type": "indicator", "colspan": 2}, None],
               [{"type": "bar"}, {"type": "bar"}],
               [{"type": "scatter", "colspan": 2}, None],
               [{"type": "bar", "colspan": 2}, None]],
        vertical_spacing=0.1
    )

    # Total Expenses
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_expenses,
        number={'prefix': "€", 'font': {'size': 80}},
        title={'text': titles[language]['total_expenses'], 'font': {'size': 30}},
    ), row=1, col=1)

    # Expenses by Month
    fig.add_trace(go.Bar(
        x=monthly_expenses['Date'],
        y=monthly_expenses['TotalAmount'],
        name='Gastos Mensuales' if language == 'es' else 'Monthly Expenses',
        text=monthly_expenses['TotalAmount'].round(2),
        textposition='outside',
    ), row=2, col=1)

    # Expenses by Company
    fig.add_trace(go.Bar(
        y=company_expenses.index,
        x=company_expenses.values,
        orientation='h',
        name='Gastos por Empresa' if language == 'es' else 'Expenses by Company',
        text=company_expenses.values.round(2),
        textposition='outside',
    ), row=2, col=2)

    # Historical Trends
    for issuer in historical_trends.columns:
        fig.add_trace(go.Scatter(
            x=historical_trends.index,
            y=historical_trends[issuer],
            mode='lines+markers',
            name=issuer,
            stackgroup='one'
        ), row=3, col=1)

        # VAT Analysis
    fig.add_trace(go.Bar(
        x=vat_analysis['Issuer'],
        y=vat_analysis['TotalAmount'],
        name='Total Amount' if language == 'en' else 'Importe Total',
        text=vat_analysis['TotalAmount'].round(2),
        textposition='outside',
        marker_color='blue'
    ), row=4, col=1)

    fig.add_trace(go.Bar(
        x=vat_analysis['Issuer'],
        y=vat_analysis['VATTotal'],
        name='VAT Amount' if language == 'en' else 'Importe IVA',
        text=vat_analysis['VATTotal'].round(2),
        textposition='outside',
        marker_color='red'
    ), row=4, col=1)

    # Update layout
    fig.update_layout(
        height=1800,  # Increased height to accommodate the new graph
        width=1000,
        title_text=titles[language]['main'],
        showlegend=True,
        barmode='group'  # This ensures the VAT analysis bars are grouped
    )
    fig.update_yaxes(title_text='€', row=2, col=1)
    fig.update_xaxes(title_text='€', row=2, col=2)
    fig.update_yaxes(title_text='€', row=3, col=1)
    fig.update_yaxes(title_text='€', row=4, col=1)
    
    return fig


def main():
    st.set_page_config(page_title="Invoice Analyzer", layout="wide")
    st.title("Invoice Analyzer / Analizador de Facturas")

    uploaded_file = st.file_uploader("Choose a CSV or JSONL file / Elija un archivo CSV o JSONL", type=["csv", "jsonl"])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            language = st.radio("Select language / Seleccione idioma", ('English', 'Español'))
            lang_code = 'en' if language == 'English' else 'es'
            
            fig = create_report(df, lang_code)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add download buttons for CSV and JSONL
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_str = csv_buffer.getvalue()
            st.download_button(
                label="Download data as CSV / Descargar datos como CSV",
                data=csv_str,
                file_name="invoice_data.csv",
                mime="text/csv"
            )

            jsonl_buffer = io.StringIO()
            df.to_json(jsonl_buffer, orient='records', lines=True)
            jsonl_str = jsonl_buffer.getvalue()
            st.download_button(
                label="Download data as JSONL / Descargar datos como JSONL",
                data=jsonl_str,
                file_name="invoice_data.jsonl",
                mime="application/jsonl"
            )

if __name__ == "__main__":
    main()