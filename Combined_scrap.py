import os
import json
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urlparse, urljoin

def scrape_pryka(collection_url, collection_name):
    website_name = "Pryka"
    baseurl = 'https://pryka.in/'

    session = HTMLSession()

    r = session.get(collection_url)
    r.html.render(sleep=2)
    soup = BeautifulSoup(r.html.html, 'lxml')

    productlist = soup.find_all('div', class_='nm-shop-loop-thumbnail')
    productlinks = []

    for item in productlist:
        for link in item.find_all('a', href=True):
            productlinks.append(link['href'])

    all_products_data = []

    # Folder for the entire collection
    collection_folder = os.path.join(os.getcwd(), website_name, collection_name)
    os.makedirs(collection_folder, exist_ok=True)

    for product_link in productlinks:
        r = session.get(product_link)
        r.html.render(sleep=2)

        soup = BeautifulSoup(r.html.html, 'lxml')

        name = soup.find('h1', class_='product_title entry-title').text.strip()
        price = soup.find('bdi', class_='').text.strip().lstrip('₹')

        size_elements = soup.find_all('span', class_='sod_option')
        desired_sizes = ['Custom Made', 'L', 'M', 'S']
        sizes = [size.text.strip() for size in size_elements if size.text.strip() in desired_sizes]

        fabric_color_elements = soup.find_all('span', style='font-weight: 400;')
        fabric_composition = None
        color = None
        for span in fabric_color_elements:
            text = span.get_text(strip=True)
            if text.startswith('Fabrication: '):
                fabric_composition = text[len('Fabrication: '):]
            elif text.startswith('Colour: '):
                color = text[len('Colour: '):]

        # Extracting and downloading images
        image_elements = soup.find_all('div', class_='woocommerce-product-gallery__image')

        for index, image_element in enumerate(image_elements, start=1):
            img_url = image_element.find('img')['data-src']

            img_data = requests.get(img_url).content
            img_path = os.path.join(collection_folder, f'{index}-{name}.png')

            with open(img_path, 'wb') as img_file:
                img_file.write(img_data)

        product_data = {
            'Pictures': [f'{i}-{name}.png' for i in range(1, len(image_elements) + 1)],
            'Website name': website_name,
            'Product Name': name,
            'Price': price,
            'Category': collection_name,
            'Colour': color,
            'Size': sizes,
            'Fabric composition': fabric_composition,
            'Availability': 'Yes',
        }

        all_products_data.append(product_data)

    # Save combined metadata as JSON
    combined_metadata_path = os.path.join(collection_folder, 'metadata.json')
    with open(combined_metadata_path, 'w') as json_file:
        json.dump(all_products_data, json_file, indent=2)

    print(f'All products data saved in JSON format. Total products: {len(all_products_data)}')

def scrape_papadontpreach(collection_url, collection_name):
    website_name = "PapaDontPreach"
    baseurl = 'https://www.papadontpreach.com'

    session = HTMLSession()

    r = session.get(collection_url)
    r.html.render(sleep=2)

    soup = BeautifulSoup(r.html.html, 'lxml')

    productlist = soup.find_all('li', class_='grid__item')
    productlinks = set()

    for item in productlist:
        for link in item.find_all('a', href=True):
            productlinks.add(baseurl + link['href'])

    # Define desired_sizes here
    desired_sizes = ['Custom Made', 'L', 'M', 'S', 'XXS', 'XS', 'XL', 'XXL', 'XXXL', '4XL', '5XL', '6XL', 'Custom Tailor']

    # Create a folder to store images and metadata
    category_folder = os.path.join(website_name, collection_name)
    os.makedirs(category_folder, exist_ok=True)

    # Initialize a list to store metadata for all products
    all_products_metadata = []

    for product_link in productlinks:
        r = session.get(product_link)
        r.html.render(sleep=2)

        soup = BeautifulSoup(r.html.html, 'lxml')

        # Extract product information
        name = soup.find('h2', class_='h1').text.strip()
        price = soup.find('span', class_='money').text.strip().lstrip('₹ ')
        category = collection_name

        # Get all the available sizes
        select_element = soup.find('select', {'name': 'options[Size]'})
        sizes = []
        if select_element:
            sizes = [option.text.strip() for option in select_element.find_all('option') if option.text.strip() in desired_sizes]

        # Extract additional information
        accordion_panel = soup.find('p', class_='accordion-panel')
        color, fabric_composition, product_code = None, None, None

        if accordion_panel:
            panel_text = accordion_panel.get_text('\n', strip=True)
            panel_lines = [line.strip() for line in panel_text.split('\n') if line.strip()]

            for line in panel_lines:
                if line.startswith('Color:'):
                    color = line[len('Color:'):].strip()
                elif line.startswith('Composition :'):
                    fabric_composition = line[len('Composition :'):].strip()
                elif line.startswith('Product code:'):
                    product_code = line[len('Product code:'):].strip()

        # Replace invalid characters in the product name
        invalid_characters = r'\/:*?"<>|'
        for char in invalid_characters:
            name = name.replace(char, '_')

        # Save images
        image_elements = soup.select('li.product__media-item img')
        image_urls = [img['src'] if img['src'].startswith('http') else 'https:' + img['src'] for img in image_elements]

        for i, image_url in enumerate(image_urls, start=1):
            response = requests.get(image_url)
            image_extension = os.path.splitext(image_url.split('?')[0])[-1]
            image_path = os.path.join(category_folder, f'{i}-{name}{image_extension}')
            with open(image_path, 'wb') as f:
                f.write(response.content)

        # Save metadata
        metadata = {
            'WebsiteName': website_name,
            'Category': category,
            'Name': name,
            'Price': price,
            'Sizes': sizes,
            'Color': color,
            'FabricComposition': fabric_composition,
            'ProductCode': product_code,
        }

        all_products_metadata.append(metadata)

    # Save metadata in a single JSON file
    metadata_file_path = os.path.join(category_folder, 'metadata.json')
    with open(metadata_file_path, 'w') as metadata_file:
        json.dump(all_products_metadata, metadata_file, indent=2)

    print("Data saved for all products.")

def scrape_kshitijjalori(collection_url, collection_name):
    website_name = "Kshitij Jalori"
    baseurl = 'https://www.kshitijjalori.com/'

    session = HTMLSession()

    r = session.get(collection_url)
    r.html.render(sleep=2)
    soup = BeautifulSoup(r.html.html, 'lxml')

    productlist = soup.find_all('div', class_='grid__item grid-product medium-up--one-half aos-init')
    productlinks = set()

    for item in productlist:
        for link in item.find_all('a', href=True):
            productlinks.add(baseurl + link['href'])

    metadata_list = []

    for link in productlinks:
        r = session.get(link)
        r.html.render(sleep=2)
        soup = BeautifulSoup(r.html.html, 'lxml')
        product_name = soup.find('h1', class_='h2 product-single__title').text.strip()
        product_folder = os.path.join(os.getcwd(), website_name, collection_name)  # Use the specified directory
        os.makedirs(product_folder, exist_ok=True)

        image_urls = []

        starting_slide_divs = soup.select('div.starting-slide img.photoswipe__image')
        secondary_slide_divs = soup.select('div.secondary-slide img.photoswipe__image')

        for i, img in enumerate(starting_slide_divs + secondary_slide_divs, start=1):
            src = img.get('data-photoswipe-src')
            if src and src.startswith('//'):
                src = 'https:' + src
            if src:
                try:
                    response = requests.get(src)
                    response.raise_for_status()
                    image_extension = os.path.splitext(urlparse(src).path)[-1]

                    # Replace '/' with '_' in the product name
                    product_name_cleaned = product_name.replace("/", "_")

                    image_path = os.path.join(product_folder, f'{i}-{product_name_cleaned}{image_extension}')

                    with open(image_path, 'wb') as f:
                        f.write(response.content)

                    image_urls.append(image_path)
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {src}: {e}")

        name = product_name
        money_span = soup.find('span', class_='money')
        price = money_span.text.strip() if money_span else soup.find('span', {'class': 'visually-hidden'}).text.strip()

        try:
            select_element = soup.find('select', {'data-index': 'option1'})
            sizes = [option.text.strip() for option in select_element.find_all('option') if option.text.strip()]
        except AttributeError:
            sizes = []

        # Check if description_div is not None
        description_div = soup.find_all('div', class_='product-single__description')
        if description_div:
            metadata = {
                "WebsiteName": website_name,
                "Category": collection_name,
                "Name": name,
                "Price": price,
                "Sizes": sizes,
                "Number of Components": None,  # Initialize as None
                "Fabric Composition": None,  # Initialize as None
                "Style Code": None,  # Initialize as None
                "Fabric Technique": None,  # Initialize as None
            }

            try:
                no_of_components_tag = description_div.find('p', string=lambda x: 'NO OF COMPONENTS' in x)
                metadata["Number of Components"] = no_of_components_tag.text.split(':')[1].strip() if no_of_components_tag else None
            except AttributeError:
                metadata["Number of Components"] = None

            try:
                fabric_tag = description_div.find('p', string=lambda x: 'FABRIC' in x)
                fabric_composition = fabric_tag.find('span').text.strip() if fabric_tag else None
                metadata["Fabric Composition"] = fabric_composition
            except AttributeError:
                metadata["Fabric Composition"] = None

            try:
                style_code_tag = description_div.find('p', string=lambda x: 'STYLE CODE' in x)
                style_code = style_code_tag.find('span').text.strip() if style_code_tag else None
                metadata["Style Code"] = style_code
            except AttributeError:
                metadata["Style Code"] = None

            try:
                fabric_technique_tag = description_div.find('p', string=lambda x: 'TECHNIQUE ON FABRIC' in x)
                metadata["Fabric Technique"] = fabric_technique_tag.text.split(':')[1].strip() if fabric_technique_tag else None
            except AttributeError:
                metadata["Fabric Technique"] = None

            metadata_list.append(metadata)

    metadata_file_path = os.path.join(product_folder, 'metadata.json')
    with open(metadata_file_path, 'w') as metadata_file:
        json.dump(metadata_list, metadata_file, indent=2)

    print(f'Data saved for all products on {website_name}')

def main():
    companies = [
        {"name": "Pryka", "baseurl": "https://pryka.in/", "collection_url": None, "collection_name": None},
        {"name": "PapaDontPreach", "baseurl": "https://www.papadontpreach.com/", "collection_url": None, "collection_name": None},
        {"name": "Kshitij Jalori", "baseurl": "https://www.kshitijjalori.com/", "collection_url": None, "collection_name": None},
    ]

    while True:
        print("Select a company:")
        for i, company in enumerate(companies, start=1):
            print(f"{i}. {company['name']}")

        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '4':
            print("Exiting the program.")
            break

        try:
            choice = int(choice)
            selected_company = companies[choice - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid option.")
            continue

        if selected_company['name'] == "Pryka":
            collection_url = input(f"Enter the collection URL for {selected_company['name']}: ")
            collection_name = input(f"Enter the collection name for {selected_company['name']}: ")
            scrape_pryka(collection_url, collection_name)

        elif selected_company['name'] == "PapaDontPreach":
            collection_url = input(f"Enter the collection URL for {selected_company['name']}: ")
            collection_name = input(f"Enter the collection name for {selected_company['name']}: ")
            scrape_papadontpreach(collection_url, collection_name)

        elif selected_company['name'] == "Kshitij Jalori":
            collection_url = input(f"Enter the collection URL for {selected_company['name']}: ")
            collection_name = input(f"Enter the collection name for {selected_company['name']}: ")
            scrape_kshitijjalori(collection_url, collection_name)

if __name__ == "__main__":
    main()
