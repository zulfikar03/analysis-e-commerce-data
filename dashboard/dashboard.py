import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import pandas as pd

orders_df = pd.read_csv("https://raw.githubusercontent.com/zulfikar03/analysis-e-commerce-data/main/orders_dataset.csv")
order_items_df = pd.read_csv("https://raw.githubusercontent.com/zulfikar03/analysis-e-commerce-data/main/order_items_dataset.csv")
products_df = pd.read_csv("https://raw.githubusercontent.com/zulfikar03/analysis-e-commerce-data/main/products_dataset.csv")
order_payments_df = pd.read_csv("https://raw.githubusercontent.com/zulfikar03/analysis-e-commerce-data/main/order_payments_dataset.csv")
order_reviews_df = pd.read_csv("https://raw.githubusercontent.com/zulfikar03/analysis-e-commerce-data/main/order_reviews_dataset.csv")
customers_df = pd.read_csv("https://raw.githubusercontent.com/zulfikar03/analysis-e-commerce-data/main/customers_dataset.csv")
product_category_df = pd.read_csv("https://raw.githubusercontent.com/zulfikar03/analysis-e-commerce-data/main/product_category_name_translation.csv")

all_df = orders_df.merge(order_items_df, on='order_id', how='left')
all_df = all_df.merge(products_df, on='product_id', how='inner')
all_df = all_df.merge(order_payments_df, on='order_id', how = 'left')
all_df = all_df.merge(order_reviews_df, on='order_id', how='left')
all_df = all_df.merge(customers_df, on='customer_id', how='inner')
all_df = all_df.merge(product_category_df, on='product_category_name', how='inner')

def set_custom_palette(series, max_color = 'turquoise', other_color = 'lightgrey'):
    max_val = series.max()
    pal = []
    
    for item in series:
        if item == max_val:
            pal.append(max_color)
        else:
            pal.append(other_color)
    return pal

def create_top_order(all_df):
    top_category_df = all_df.groupby(by="product_category_name_english").order_id.nunique().sort_values(ascending=False).reset_index()[:10]
    top_category_df.rename(columns={"order_id":"order_count"},inplace=True)
    return top_category_df

def create_order_time_to_time(all_df):
    all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
    all_df["month_year"] =  all_df['order_purchase_timestamp'].dt.strftime('%Y-%m')
    order_per_month = all_df.groupby(by="month_year").count()[["order_id"]]
    order_per_month = order_per_month.iloc[:-1]
    order_per_month.rename(columns={"order_id":"order_count"}, inplace=True)
    return order_per_month

def create_revenue_time_to_time(all_df):
    monthly_orders_df = all_df.resample(rule='M', on='order_purchase_timestamp').agg({
    "order_id": "nunique",
    "payment_value": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return monthly_orders_df

def create_most_payment_type(all_df):
    payment_type_counts = all_df.groupby(by="payment_type").customer_id.nunique().sort_values(ascending=False).reset_index()
    payment_type_counts.rename(columns={"customer_id":"count"}, inplace=True)
    return payment_type_counts

def create_rfm_df(all_df):
    all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp" : "max", # mengambil tanggal order terakhir
    "order_id": "nunique", # menghitung jumlah order
    "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    #rfm_df["order_purchase_timestamp"] = pd.to_datetime(rfm_df["order_purchase_timestamp"])
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
 
    #menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = all_df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
 
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df


#all_df = pd.read_csv("semua_data.csv")

st.title("Dashboard E-Commerce Brazil")
tab1,tab2 = st.tabs(["Analisis Biasa", "RFM Analisis"])

top_order = create_top_order(all_df)
order_time_to_time = create_order_time_to_time(all_df)
revenue_time_to_time = create_revenue_time_to_time(all_df)
most_payment_type = create_most_payment_type(all_df)
rfm = create_rfm_df(all_df)

with tab1:
    st.header("Top 10 Produk Paling Banyak Dipesan")
    total_bed = top_order["order_count"][0]
    st.metric("Total Bed Bath Table", value=total_bed)
    fig, ax = plt.subplots(figsize=(16, 8))
    palette = set_custom_palette(top_order["order_count"])
    sns.barplot(data=top_order, x="order_count", y="product_category_name_english",palette=palette,ax=ax)
    ax.set_title("Top Kategori Produk Berdasarkan yang Diorder", fontsize=25)
    ax.set_xlabel("Total Order")
    ax.set_ylabel("Nama Produk")
    st.pyplot(fig)

    st.header("Total Order Setiap Bulan")
    total_order = order_time_to_time.order_count.sum()
    st.metric("Total orders", value=total_order)
    fig, ax = plt.subplots(figsize=(20,8))
    sns.lineplot(data=order_time_to_time, marker='o', markersize=5, color='green')
    ax.set_title("Total Order Setiap Bulan", fontsize=25)
    ax.set_xlabel("Bulan-Tahun")
    ax.set_ylabel("Total Order")
    st.pyplot(fig)

    st.header("Total Revenue Setiap Bulan")
    total_revenue = revenue_time_to_time.revenue.sum()
    st.metric("Total orders", value=total_revenue)
    fig, ax = plt.subplots(figsize=(20,8))
    sns.lineplot(data=revenue_time_to_time, markers='o', markersize=5, color='green')
    ax.set_title("Total Revenue Setiap Bulan", fontsize=25)
    ax.set_xlabel("Bulan-Tahun")
    ax.set_ylabel("Total Revenue")
    st.pyplot(fig)

    st.header("Metode Pembayaran Favorit Para Pengguna")
    total_credit_card = most_payment_type["count"][0] 
    st.metric("Total Credit Card", value=total_credit_card)
    fig, ax = plt.subplots(figsize=(10,6))
    palette = set_custom_palette(most_payment_type["count"])
    sns.barplot(data=most_payment_type, x="payment_type", y="count", palette=palette)
    ax.set_title("Jumlah Metode Pembayaran", fontsize=25)
    ax.set_xlabel("Metode Pembayaran")
    ax.set_ylabel("Jumlah")
    st.pyplot(fig)

with tab2:
    st.header("Recency Analisis")
    avg_recency = round(rfm.recency.mean(),2)
    st.metric("Average Recency", value=avg_recency)
    fig, ax = plt.subplots(figsize=(20,8))
    sns.barplot(y="customer_id", x="recency", data=rfm.sort_values(by="recency", ascending=False).head(5), color="turquoise", ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("By Recency (days)", loc="center", fontsize=18)
    ax.tick_params(axis ='x', labelsize=15)
    st.pyplot(fig)

    st.header("Frequency Analisis")
    avg_frequency = round(rfm.frequency.mean(),2)
    st.metric("Average Frequency", value=avg_frequency)
    fig, ax = plt.subplots(figsize=(20,8))
    sns.barplot(y="customer_id", x="frequency", data=rfm.sort_values(by="frequency", ascending=False).head(5), color="turquoise", ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("By Frequency", loc="center", fontsize=18)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

    st.header("Monetary Analisis")
    avg_monetary = round(rfm.monetary.mean(),2)
    st.metric("Average Monetary", value=avg_monetary)
    fig, ax = plt.subplots(figsize=(20,8))
    sns.barplot(y="customer_id", x="monetary", data=rfm.sort_values(by="monetary", ascending=False).head(5), color="turquoise", ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("By Monetary", loc="center", fontsize=18)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)