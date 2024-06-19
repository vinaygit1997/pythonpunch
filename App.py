import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk
import os

# Download NLTK tokenizer models if not already downloaded
nltk.download('punkt')

# Function to fetch news based on search topic
def fetch_news_search_topic(topic):
    site = 'https://news.google.com/rss/search?q={}'.format(topic)
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

# Function to fetch top news
def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

# Function to fetch category-specific news
def fetch_category_news(topic):
    site = 'https://news.google.com/news/rss/headlines/section/topic/{}'.format(topic)
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

# Function to fetch news poster image
def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, use_column_width=True)
    except Exception as e:
        st.error(f"Error loading image: {e}")
        try:
            placeholder_image_path = './Meta/no_image.jpg'
            if os.path.exists(placeholder_image_path):
                image = Image.open(placeholder_image_path)
                st.image(image, use_column_width=True)
            else:
                st.error(f"Placeholder image not found at {placeholder_image_path}")
        except Exception as e:
            st.error(f"Error loading placeholder image: {e}")

# Function to display news articles
def display_news(list_of_news, news_quantity):
    for index, news in enumerate(list_of_news):
        st.write(f"**({index + 1}) {news.title.text}**")
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            st.error(f"Error processing article: {e}")
            continue
        fetch_news_poster(news_data.top_image)
        with st.expander(news.title.text):
            st.markdown(f"<h6 style='text-align: justify;'>{news_data.summary}</h6>", unsafe_allow_html=True)
            st.markdown(f"[Read more at {news.source_url}...]({news.link.text})")
        st.success(f"Published Date: {news.pubDate.text}")
        if index + 1 >= news_quantity:
            break

# Main function to run the Streamlit web application
def run():
    st.set_page_config(page_title='InNews🇮🇳: A Summarised News📰 Portal', page_icon='./Meta/newspaper.ico')
    st.title("InNews🇮🇳: A Summarised News📰 Portal")

    try:
        image_path = './Meta/newspaper.png'
        if os.path.exists(image_path):
            image = Image.open(image_path)
            st.image(image, use_column_width=False)
        else:
            st.error(f"Main image not found at {image_path}")
    except Exception as e:
        st.error(f"Error loading main image: {e}")

    category = ['--Select--', 'Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic']
    cat_op = st.selectbox('Select your Category', category)
    
    if cat_op == category[0]:
        st.warning('Please select a category!')
    elif cat_op == category[1]:
        st.subheader("✅ Here are the Trending🔥 news for you")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
        news_list = fetch_top_news()
        display_news(news_list, no_of_news)
    elif cat_op == category[2]:
        av_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        st.subheader("Choose your favourite Topic")
        chosen_topic = st.selectbox("Choose your favourite Topic", av_topics)
        if chosen_topic == av_topics[0]:
            st.warning("Please choose a topic")
        else:
            no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
            news_list = fetch_category_news(chosen_topic)
            if news_list:
                st.subheader(f"✅ Here are some {chosen_topic} News for you")
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News found for {chosen_topic}")
    elif cat_op == category[3]:
        user_topic = st.text_input("Enter your Topic🔍")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=15, step=1)

        if st.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(topic=user_topic_pr)
            if news_list:
                st.subheader(f"✅ Here are some {user_topic.capitalize()} News for you")
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News found for {user_topic}")
        else:
            st.warning("Please write a Topic Name to Search🔍")

if __name__ == "__main__":
    run()
