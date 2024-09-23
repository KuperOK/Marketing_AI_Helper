import streamlit as st
import pandas as pd
import re
import openai
import os
from langchain_community.document_loaders import WebBaseLoader as WBL
from langchain.prompts import ChatPromptTemplate
from prompts import * #prompt_for_title
from langchain_openai import ChatOpenAI
import io
from datetime import datetime

en = '?language=en_GB&th=1'
ge = '?th=1&language=de_DE&currency=EUR'

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_title_and_text_from_amazon(url, lang):
    url = url + lang
    loader = WBL(web_path=url)
    docs = loader.load()
    long_name = docs[0].metadata['title']
    other_text = docs[0].page_content
    info_start_idx = other_text.find('Info zu diesem Artikel') if 'de_' in lang else other_text.find('About this item')      
    info_end_idx = other_text.find('Weitere Produktdetails') if 'de_' in lang else other_text.find('See more product details')
    description = ''
    if info_start_idx > 0:
        description = other_text[info_start_idx:info_end_idx]
    comments_start_idx = other_text.find('Spitzenrezensionen') if 'de_' in lang else other_text.find('Top reviews')
    comments_end_idx = other_text.rfind('Weitere Rezensionen ansehen') if 'de_' in lang else other_text.find('See more reviews')
    comments = ''
    if comments_start_idx > 0:
        comments = other_text[comments_start_idx:comments_end_idx]    
        comments = re.sub(r'\n{2,}', '\n', comments)
        comments = re.sub(r'Report\s*Translate review to English', '', comments)
    product_text = {}
    product_text['long name'] = long_name
    product_text['description'] = description
    product_text['comments'] = comments
    return product_text


def clean_key(key):
    """
    Cleans the input string (key) by removing unwanted characters.

    The function performs the following steps:
    1. Removes any leading numbers and dots from the beginning of the string.
    2. Removes all characters that are not letters, digits, or spaces (including special characters).
    3. Removes all non-ASCII characters (such as Unicode symbols and ideograms).
    4. Trims any leading and trailing whitespace from the string.

    Args:
        key (str): The input string representing a key.

    Returns:
        str: The cleaned string without numbers, special characters, or non-ASCII symbols.
    """
    key = re.sub(r'^[\d.]+', '', key)  # Removes leading numbers and dots
    key = re.sub(r'[^\w\s]', '', key)  # Removes all non-alphanumeric characters and spaces
    key = re.sub(r'[^\x00-\x7F]+', '', key)  # Removes all non-ASCII characters
    key = key.strip()  # Trims leading and trailing spaces
    return key

def get_technical_data(file_path: str) -> dict:
    """
    Extracts and cleans technical data from an Excel file.

    This function reads technical information from a specific Excel sheet, processes the data by:
    1. Loading the Excel sheet named '2. Technical Info' and skipping the first 4 rows.
    2. Selecting only the specified columns and dropping rows with missing values.
    3. Filtering out rows where the 'value' column contains the string 'Choose from dropdown'.
    4. Converting the remaining data into a dictionary format.
    5. Cleaning the keys of the dictionary using the `clean_key` function to remove unwanted characters and symbols.

    Args:
        file_path (str): The path to the Excel file containing the technical data.

    Returns:
        dict: A dictionary where keys represent technical feature names and values represent the corresponding data.
    """
    temp = pd.ExcelFile(file_path)
    sheet_name = None
    for name in temp.sheet_names:
        if 'Technical Info' in name:
            sheet_name = name
            break
    else:
        raise ValueError('There isn\'t Technical Info in excel-file')
        
    # print(sheet_name)
    df = pd.read_excel(file_path, header=None, skiprows=4, sheet_name=sheet_name, usecols=[1,2])
    df = df.dropna(axis=0)
    df.columns=['name', 'value']
    df = df[~(df.value == 'Choose from dropdown')]
    df['name'] = df.name.apply(clean_key)
    features = df.to_dict(orient='tight', index=False)
    features = dict(features['data'])
    # features = {clean_key(key): value for key, value in features.items()}
    return features, df


lang_dict = {
    "English": 'en',
    "German": 'de',
    "French": 'fr',
    "Italian": 'it',
    "Spanish": 'sp',
    "Portuguese": 'pt',
    "Dutch": 'dt'
}


st.title(':blue[Marketing AI Helper]')

tab1, tab2 = st.tabs(["Generate AI Marketing Text", "Transalte AI Marketing Text"])

############## TAB2 AI TRANSLATING #############
with tab1:
    # 1. Data Upload Section
    st.header(":orange[Upload Analogue Product Data]")

    url = st.text_input("Enter a hyperlink of similar product:")
    show_product_params = st.checkbox('Show analogue product params', value=False)

    if 'product' not in st.session_state:
        st.session_state.product = None
    if url and st.button('Retrieving'):
        with st.spinner(text="Retrieving analogue product data is in progress ..."):
            product = get_title_and_text_from_amazon(url, en)
            st.session_state.product = product
        if show_product_params:
            prod_long_name = st.text_area("**Analogue long name:**" ,value=product['long name'])            
            product_decription = st.text_area("Analogue description:", value=product['description'])            
            product_comments = st.text_area("Analogue comments:", value=product['comments'])
    

    uploaded_file = st.file_uploader("Upload Excel file:", type=["xlsx", "xls"])
    show_product_tinfo = st.checkbox('Show product tech info', value=False)
    if uploaded_file is not None:
        tech_info, df = get_technical_data(uploaded_file)
        df.columns = ['Feature', 'Value']
        if show_product_tinfo:
            st.subheader("Tech info from Excel file:")
            st.dataframe(df)


    # 2. Product Description Generation Section
    st.header(":green[Generate New Product Description]")
    language_output = st.selectbox(
        label ="Select marketig text language ",
        options = ("English", "German", "French", "German", "Italian", "Spanish", "Portuguese", "Dutch"),
        index=None,
        # placeholder="Select contact method...",
    )

    if language_output:
        st.write(f"Selected: language: :red[{language_output}]")

    # Block 1: Long Name Generation
    st.subheader("Generate Long Name")


    llm_model = "gpt-4o-mini-2024-07-18" # chatgpt-4o-latest
    chat = ChatOpenAI(model=llm_model, temperature=0.5)

    prompt_long_name = st.text_area("Enter prompt for long name:", value=prompt_for_title, height=350)
    prompt_template_long_name = ChatPromptTemplate.from_template(prompt_long_name)
    if  st.session_state.product and tech_info and language_output:
        prompt_template_long_name = prompt_template_long_name.format(
            tech_info=tech_info,
            prod_long_name=st.session_state.product['long name'],
            language=language_output
            )


    if st.button("Generate Long Name"):
        st.session_state.response_title = chat.invoke(prompt_template_long_name).content
        st.text_area("Generated Long Name:", st.session_state.response_title, height=275)

    # Block 2: Benefits Generation
    st.subheader("Generate Product Benefits")
    prompt_benefits = st.text_area("Enter prompt for benefits:", value=prompt_for_benefits, height=500)
    if  st.session_state.product and language_output:
        prompt_template_benefits = ChatPromptTemplate\
            .from_template(prompt_benefits)\
            .format(
                tech_info=tech_info,
                product_decription = st.session_state.product['description'],
                language=language_output
                )
    if st.button("Generate Benefits"):
        st.session_state.response_benefits = chat.invoke(prompt_template_benefits).content
        
        with st.container(border=True, height=200):
            st.write("Product Benefits: ")
            st.markdown(st.session_state.response_benefits)

    # Block 3: USP Generation
    st.subheader("Generate USP")
    prompt_usp = st.text_area("Enter prompt for USP:", value=prompt_for_USP, height=700)
    if  st.session_state.product and language_output:
        prompt_template_USP = ChatPromptTemplate\
            .from_template(prompt_usp)\
            .format(
                tech_info=tech_info,
                product_decription = st.session_state.product['description'],
                product_comments = st.session_state.product['comments'],
                language=language_output       
            )
    if st.button("Generate USP"):
        st.session_state.response_USP = chat.invoke(prompt_template_USP).content
        with st.container(border=True, height=500):
            st.write("Product unique selling points (USP): ")
            st.markdown(st.session_state.response_USP)

    # Block 4: Marketing Text Generation
    st.subheader("Generate Marketing Text")
    prompt_marketing_text = st.text_area("Enter prompt for advertisin text:", value=prompt_for_ad_text, height=700)
    if  st.session_state.product and language_output:
        prompt_template_text = ChatPromptTemplate\
            .from_template(prompt_marketing_text)\
            .format(
                tech_info=tech_info,
                product_decription = st.session_state.product['description'],
                product_comments = st.session_state.product['comments'],
                language=language_output 
            )
    if st.button("Generate Marketing Text"):
        st.session_state.response_text = chat.invoke(prompt_template_text).content
        with st.container(border=True, height=750):
            st.write("Product adverising text: ")
            st.markdown(st.session_state.response_text)


    # 3. Saving and Clearing Section
    st.header(":red[Save all genrated texts]")

    if st.button("Save Results"):
        hs_code = tech_info.get('HS Code', 'xxxx')
        lang = lang_dict.get(language_output, 'unknown')
        filename = f'{lang}_' + str(hs_code) + '_marketing_info_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
        all_togather = f"{st.session_state.response_title}\n{st.session_state.response_benefits}\n\n{st.session_state.response_USP}\n\n{st.session_state.response_text}"
        buffer = io.BytesIO()
        buffer.write(all_togather.encode("utf-8"))
        buffer.seek(0)
        if st.download_button(
                    label="Download File",
                    data=buffer,
                    file_name=filename,
                    mime="text/plain"
                ):
            st.success("Results saved!")

############## TAB2 AI TRANSLATING #############
with tab2:

    st.session_state.lang_from = None
    st.session_state.lang_to = None

    rev_lang_dict = {v: k for k, v in lang_dict.items()}
    st.header('Translate AI Marketing text')
    file_to_translate = st.file_uploader("Upload marketing texts file:", type="txt")
    # print(type(file_to_translate), file_to_translate)
    if file_to_translate:
        file_name = file_to_translate.name
        lang_from = file_name[:2]
        text = file_to_translate.read().decode("utf-8")
        st.session_state.lang_from = lang_from

    lang_to_translate = st.selectbox(
        label ="Select language translate to",
        options = ("English", "German", "French", "Italian", "Spanish", "Portuguese", "Dutch"),
        index=1,
        # placeholder="Select contact method...",
    )
    
    st.session_state.lang_to = None
    st.session_state.translated_text = None

    if st.session_state.lang_from and file_to_translate:
        prompt_translate =  ChatPromptTemplate\
            .from_template(prompt_for_translate)\
            .format(
                source_language=rev_lang_dict[lang_from],
                target_language = lang_to_translate,
                text_for_translation=text 
            )
        print(prompt_translate)
        # st.write(f"Selected: language: :red[{language_output}]")
        st.write(f'Translate text from :green[{rev_lang_dict[lang_from].upper()}] to :orange[{lang_to_translate.upper()}]')
        llm_model = st.selectbox(
                "Select LLM",
                ("gpt-4o-mini-2024-07-18", "chatgpt-4o-latest"))
    
    if st.button('Translate'):
        with st.spinner(text="AI translation in progress ..."):
            
            trans_chat = ChatOpenAI(model_name=llm_model, temperature=0)
            st.session_state.translated_text = trans_chat.invoke(prompt_translate).content
            print(st.session_state.translated_text)
            st.text_area(f"Original {rev_lang_dict[lang_from].upper()} text:", value=text, height=500)
            st.text_area(f"Translated to {lang_to_translate.upper()} text:", value=st.session_state.translated_text, height=500)


        lang = lang_dict.get(lang_to_translate, 'unknown')
        filename = f'{lang}_from_{lang_from}' + file_name[2:-19] + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
    
        buffer = io.BytesIO()
        buffer.write(st.session_state.translated_text.encode("utf-8"))
        buffer.seek(0)
        if st.download_button(
                    label="Download traslated file",
                    data=buffer,
                    file_name=filename,
                    mime="text/plain"
                ):
            st.success("Results saved!")