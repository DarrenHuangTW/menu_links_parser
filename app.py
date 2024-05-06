import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

def parse_menu_links(html, base_url):
    # parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # find all <nav> elements
    nav_elements = soup.find_all('nav')

    if not nav_elements:
        st.error("No navigation (<nav>) elements found on the page. This script extracts links from "
                 "navigation menus defined within <nav> tags in the HTML structure of a webpage.")
        return []

    if len(nav_elements) > 1:
        st.warning("Multiple navigation (<nav>) elements found. The script will parse links from all "
                   "found <nav> elements, which may include non-menu links.")

    # create a list of dictionaries with the URL, anchor text, and level for each link
    menu_links = []
    for nav in nav_elements:
        links = nav.find_all('a')
        for link in links:
            try:
                # Make sure the URL is absolute
                url = urljoin(base_url, link['href'])
                anchor_text = link.get_text(strip=True)

                # find the number of <li> tags between the <nav> and the current <a> tag
                level = 1
                current_li = link.parent
                while current_li and current_li != nav:
                    if current_li.name == 'li':
                        level += 1
                    current_li = current_li.parent

                menu_links.append({'Item': anchor_text, 'URL': url, 'Level': level})

            except Exception as e:
                st.error(f"Error processing link: {link} - {e}")

    return menu_links

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

# Streamlit application
st.title('Menu Link Extractor')

# User input for URL
url = st.text_input('Enter the URL of the site you want to scrape')

if st.button('Extract Menu Links'):
    if url:
        html_code = fetch_html(url)
        if html_code:
            menu_links = parse_menu_links(html_code, url)
            if menu_links:
                # Convert the list of dictionaries to a DataFrame
                df = pd.DataFrame(menu_links)
                # Display the DataFrame with a wider format
                st.dataframe(df, width=1000)
                # Convert DataFrame to CSV and allow user to download
                st.download_button(
                    label="Download data as CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='menu_links.csv',
                    mime='text/csv',
                )
    else:
        st.warning('Please enter a URL to proceed.')
