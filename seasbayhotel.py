import streamlit as st
from datetime import datetime
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import copy
import os
import json


# 讀取設定檔
with open('./config.yaml', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

import toml
from toml import TomlDecodeError

# 初始化身份驗證
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
#global login
#login = 0


# 初始化使用者資訊，
# Login 進來的人的購買紀錄
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "shopping_cart": [],
        "order_history": []
    }

# 用戶訂單歷史檔案路徑
orders_path = "./orders/"

# 確保訂單目錄存在
if not os.path.exists(orders_path):
    os.makedirs(orders_path)

# 加載用戶訂單歷史
def load_user_order_history(username):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        return pd.read_csv(order_history_file)
    return pd.DataFrame(columns=["title", "quantity"])

# 保存用戶訂單歷史
def save_user_order_history(username, current_orders):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        # 如果檔案已存在，則讀取並附加新訂單
        existing_orders = pd.read_csv(order_history_file)
        updated_orders = pd.concat([existing_orders, pd.DataFrame(current_orders)], ignore_index=True)
    else:
        # 如果檔案不存在，則創建新的 DataFrame
        updated_orders = pd.DataFrame(current_orders)
    
    # 保存更新後的訂單歷史
    updated_orders.to_csv(order_history_file, index=False)



def login_page():
    # 在登入頁面以對話框的形式顯示用戶消息
    page = st.sidebar.radio("選擇頁面", ["首頁","測試頁", "私房遊程","所有景點", "歷史訂單", "景點搜搜搜", "留言板"])
    if page == "首頁":
        view_products()
    elif page == "測試頁":
        home()
    elif page == "所有景點":
        popular_attractions()
    elif page == "私房遊程":
        private_tours()
    elif page == "歷史訂單":
        order_history()
    elif page == "景點搜搜搜":
        shopping_cart_page()
    elif page == "留言板":
        message_board()




import csv

csv_file_path = 'book.csv'

# 讀取CSV檔案，將資料存入DataFrame

books = pd.read_csv(csv_file_path)


# 初始化 session_state
if "shopping_cart" not in st.session_state:
    st.session_state.shopping_cart = []

# 定義各頁面
    
# 首頁
def home():
    st.subheader("熱門景點")
    cols = st.columns(2)  # 新增
    for i in range(0, min(2, len(books))):  # Display up to the first 6 entries
        with cols[i % 2]:  # 新增
            st.write(f" {books.at[i, 'title']}")
            st.image(books.at[i, "image"], caption=books.at[i, "title"], width=300)
    st.subheader("私房遊程")

# 景點總覽
def view_products():
    st.title("景點推薦")

    # 使用 st.beta_columns 將一行分為兩列
    cols = st.columns(2)  # 新增
    for i in range(0, min(6, len(books))):  # Display up to the first 6 entries
        with cols[i % 2]:  # 新增
            st.write(f"## {books.at[i, 'title']}")
            st.image(books.at[i, "image"], caption=books.at[i, "title"], width=300)
            st.write(f"**位置:** {books.at[i, 'author']}")
            st.write(f"**類型:** {books.at[i, 'genre']}")
            st.write(f"**金額:** {books.at[i, 'price']}")

            quantity = st.number_input(f"購買數量 {i}", min_value=1, value=1, key=f"quantity_{i}")

            if st.button(f"選取 {books.at[i, 'title']}", key=f"buy_button_{i}"):
                if "shopping_cart" not in st.session_state:
                    st.session_state.shopping_cart = []
                st.session_state.shopping_cart.append({
                    "title": books.at[i, "title"],
                    "quantity": quantity,
                    "total_price": int(books.at[i, 'price']) * int(quantity)  # Total price calculation
                })
                st.write(f"已將 {quantity} 本 {books.at[i, 'title']} 加入景點搜搜搜")

        st.write("---")



# 顯示訂單
def display_order():
    st.title("訂單明細")

    # 顯示景點搜搜搜中的商品
    for item in st.session_state.shopping_cart:
        st.write(f"{item['quantity']} 本 {item['title']}")

    # 顯示其他訂單相關資訊，例如總金額、訂單時間等
    total_expense = sum(item["total_price"] for item in st.session_state.shopping_cart)
    st.write(f"總金額: {total_expense}")

    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"訂單時間: {order_time}")

# 景點搜搜搜頁面
def shopping_cart_page():
    st.title("景點搜搜搜")
    
    if not st.session_state.shopping_cart:
        st.write("景點搜搜搜是空的，快去選購您喜歡的書籍吧！")
    else:
        # Create a Pandas DataFrame from the shopping cart data
        df = pd.DataFrame(st.session_state.shopping_cart)

        # Display the DataFrame as a table
        st.table(df)

        pay = st.button('結帳')

        if pay:
            st.session_state.show_payment = True
        if 'show_payment' in st.session_state and st.session_state.show_payment:
            Payment_page()


# 結帳頁面
def Payment_page():
    st.title("結帳")
    with st.form(key="購物清單") as form:
        購買詳情 = display_order()
        付款方式 = st.selectbox('請選擇付款方式', ['信用卡', 'Line Pay'])
        優惠碼 = st.text_input('優惠代碼')
        寄送方式 = st.selectbox('請選擇寄送方式', ['寄送到府', '寄送至指定便利商店'])
        
        submitted = st.form_submit_button("確認付款")
        
    if submitted:
        order_history_df = pd.DataFrame(st.session_state.shopping_cart)
            # 保存用戶訂單歷史
        save_user_order_history(st.session_state.user_info["name"], order_history_df)
        st.session_state.shopping_cart = []
        st.write("交易成功！")

# 留言頁
def message_board():
    # 初始化 session_state
    if "past_messages" not in st.session_state:
        st.session_state.past_messages = []

    # 在應用程式中以對話框的形式顯示用戶消息
    with st.chat_message("user"):
        st.write("歡迎來到留言板！")

    # 接收用戶輸入
    prompt = st.text_input("在這裡輸入您的留言")

    # 如果用戶有輸入，則將留言加入 session_state 中
    if prompt:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.past_messages.append({"user": "user", "message": f"{timestamp} - {prompt}"})

    # 留言板中顯示過去的留言
    with st.expander("過去的留言"):
        # 顯示每條留言
        for message in st.session_state.past_messages:
            with st.chat_message(message["user"]):
                st.write(message["message"])



# 訂單歷史頁面
def order_history():
    st.title("訂單歷史")
    # 將訂單資料轉換為 DataFrame
    df = load_user_order_history(st.session_state.user_info["name"])

    # 顯示表格
    st.table(df)

# 所有景點頁面
def popular_attractions():
    st.title("所有景點")
    st.write("探索城市的所有景點！在這裡找到您感興趣的地方。")
        
    # Get selected region and category from the sidebar
    cols = st.columns(2)
    with cols[0]:
        selected_region = st.selectbox("景點地區", ["旗津海港", "駁二時尚", "鹽埕風格", "西子灣海風"], key="region_selector")
    with cols[1]:
        selected_category = st.selectbox("景點種類", ["美食介紹", "景點遊玩"], key="category_selector")
    
    # Filter books based on selected region and category
    filtered_books = books[(books['author'] == selected_region) & (books['genre'] == selected_category)]

    # Display filtered books
    st.write(f"篩選後的 {selected_region} 的 {selected_category} 景點:")
    
    # Iterate through filtered_books and display information
    cols = st.columns(2)
    for i in range(len(filtered_books)):
        with cols[i % 2]:  
            try:
                st.write(f"## {filtered_books.at[i, 'title']}")
                st.image(filtered_books.at[i, "image"], caption=filtered_books.at[i, "title"], width=300)  
                st.write(f"**位置:** {filtered_books.at[i, 'author']}")
                st.write(f"**類型:** {filtered_books.at[i, 'genre']}")
                st.write(f"**金額:** {filtered_books.at[i, 'price']}")
                
                quantity = st.number_input(f"購買數量 {i}", min_value=1, value=1, key=f"quantity_{i}")

                if st.button(f"選取 {filtered_books.at[i, 'title']}", key=f"buy_button_{i}"):
                    # Add selected book to shopping cart or perform any other action
                    st.write(f"已將 {quantity} 本 {filtered_books.at[i, 'title']} 加入景點搜搜搜")

                st.write("---")
            except KeyError:
                pass  #沒有索引就略過
# 私房遊程頁面
def private_tours():
    st.title("私房遊程")
    st.write("尋找獨特的私房遊程，打造屬於您的旅程！")



def main():
    
    st.title("西子灣沙灘會館")
    st.write("歡迎光臨西子灣沙灘會館！")   
    st.image("https://s3-alpha-sig.figma.com/img/152b/406a/1a0e94e7a9c64f497bdd72615b2568d2?Expires=1704067200&Signature=hGOM2q7F2ObaczZ5E26wBxXMbdFhesgJLR0pbknF3hyI8ft0a72ZglpKQ408~8Gg~clBh-IaaEFcATTJoFa6w7a4X9-k--W53oJND1vkgKTwn0tsjsaIOAuohTl3AYm89I~x7XblQBrDR2e-Yp7z4J20QeCTQturkAfIsc3BSyyUSU-bWwdMQHj651uoZSD04GtM2ODhG3bXOCSq6s9DjDJoTYw1y3kjwFU8VxD9j3oqe3NolB3j2IcCsuQ2ePcFa1s~bIFm9pwuxCi22jqE2nxcE1s0ASVU8b6o3FzERTWgYVOCPqbczCCTJ1TIfJJKHBKxUtXCcZlAxY5j8Jtg3Q__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4")
    st.session_state.login = False
    
    # 登入
    name, authentication_status, username = authenticator.login('Login', 'main')
    st.session_state.login = authentication_status
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.session_state.user_info["name"] = name
        # 加載用戶訂單歷史
        st.session_state.user_info["order_history"] = load_user_order_history(username)
        st.write(f'Welcome *{name}*')  
        login_page()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()



