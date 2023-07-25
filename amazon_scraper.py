import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_amazon_product_data(url):
    """Scrape product data from Amazon."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        product_data = {
            "product_url": url,
            "product_name": soup.find("span", {"id": "productTitle"}).text.strip(),
            "product_price": soup.find("span", {"id": "priceblock_ourprice"}).text.strip(),
            "rating": soup.find("span", {"id": "acrCustomerReviewText"}).text.strip(),
            "number_of_reviews": soup.find("span", {"id": "acrCustomerReviewText"}).text.strip(),
        }
    except AttributeError:
        product_data = None

    return product_data

def scrape_additional_data(product_data):
    """Scrape additional information from product URLs."""
    for product in product_data:
        url = product["product_url"]
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            product["description"] = soup.find("meta", {"name": "description"})["content"].strip()
            product["asin"] = soup.find("input", {"id": "ASIN"})["value"].strip()
            product["product_description"] = soup.find("div", {"id": "productDescription"}).text.strip()
            product["manufacturer"] = soup.find("a", {"id": "bylineInfo"}).text.strip()
        except (AttributeError, TypeError, KeyError):
            # If any of the required elements are missing or if there's an error during scraping,
            # set the corresponding fields to None.
            product["description"] = None
            product["asin"] = None
            product["product_description"] = None
            product["manufacturer"] = None

        # Add a delay to be respectful to the website's resources
        time.sleep(1)

if __name__ == "__main__":
    base_url = "https://www.amazon.in/sk/bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"
    num_pages_to_scrape = 20

    product_data = []
    for page in range(1, num_pages_to_scrape + 1):
        url = base_url.format(page)
        product_data.append(scrape_amazon_product_data(url))
        # Add a delay to be respectful to the website's resources
        time.sleep(1)

    # Filter out None values (if any) from the product_data list
    product_data = [data for data in product_data if data is not None]

    scrape_additional_data(product_data)

    # Write the data to a CSV file
    with open("amazon_product_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["product_url", "product_name", "product_price", "rating", "number_of_reviews",
                         "description", "asin", "product_description", "manufacturer"])
        for product in product_data:
            writer.writerow(list(product.values()))
