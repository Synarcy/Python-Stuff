import requests
from bs4 import BeautifulSoup
from spellchecker import SpellChecker
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

def check_spelling_mistakes(url, min_price, max_price):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    products = []
    
    if "amazon.co.uk" in url:
        for desc in soup.select('a.a-text-normal[href]'):
            price_tag = desc.find_next('span', class_='a-price')
            if price_tag:
                price = price_tag.find('span', class_='a-offscreen')
                if price:
                    price_value = float(price.text.replace('£', '').replace('$', '').replace(',', '').strip().split('-')[0].split('to')[0].strip())
                    if min_price <= price_value <= max_price:
                        products.append({
                            "description": desc.text,
                            "link": url + desc['href'],
                            "price": price.text
                        })
    elif "ebay.co.uk" in url:
        for item in soup.select('.s-item__info.clearfix a.s-item__link'):
            price_tag = item.find_next('span', class_='s-item__price')
            if price_tag:
                price_value = float(price_tag.text.replace('£', '').replace('$', '').replace(',', '').strip().split('-')[0].split('to')[0].strip())
                if min_price <= price_value <= max_price:
                    products.append({
                        "description": item.text.strip(),
                        "link": "https://www.ebay.co.uk" + item['href'],
                        "price": price_tag.text
                    })
    else:
        print("Unsupported website.")
        return []
    
    spell = SpellChecker()
    products_with_errors = []
    for product in products:
        misspelled = spell.unknown(product["description"].split())
        if misspelled:
            product["errors"] = list(misspelled)
            products_with_errors.append(product)
    
    return products_with_errors

def universal_scrape(url):
    """Scrapes all the text from a given URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    texts = soup.stripped_strings
    return " ".join(texts)

def gui_check_spelling_mistakes():
    urls = url_text.get("1.0", tk.END).strip().split("\n")
    
    for url in urls:
        if "amazon.co.uk" in url or "ebay.co.uk" in url:
            try:
                min_price = float(min_price_entry.get())
                max_price = float(max_price_entry.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid price values.")
                return

            errors = check_spelling_mistakes(url, min_price, max_price)
        else:
            scraped_text = universal_scrape(url)
            spell = SpellChecker()
            misspelled = spell.unknown(scraped_text.split())
            errors = []
            if misspelled:
                errors.append({
                    "description": "Extracted Text",
                    "link": url,
                    "price": "N/A",
                    "errors": list(misspelled)
                })

        if errors:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    for product in errors:
                        file.write(f"Description: {product['description']}\n")
                        file.write(f"Link: {product['link']}\n")
                        file.write(f"Price: {product['price']}\n")
                        file.write(f"Spelling Mistakes: {', '.join(product['errors'])}\n")
                        file.write("-" * 80 + "\n")
                messagebox.showinfo("Success", "Results saved successfully!")
        else:
            messagebox.showinfo("No Errors Found", f"No spelling errors found for the provided criteria in {url}.")

def exit_program():
    root.destroy()

root = tk.Tk()
root.title("Spelling Mistakes Checker")
root.geometry("500x550")

info_label = tk.Label(root, text="Only amazon and ebay for now", font=("Arial", 10, "bold"), fg="red")
info_label.pack(pady=5)

url_label = tk.Label(root, text="Website URLs (One per line):")
url_label.pack(pady=5)
url_text = tk.Text(root, width=60, height=10)
url_text.pack(pady=5)

min_price_label = tk.Label(root, text="Minimum Price (£):")
min_price_label.pack(pady=5)
min_price_entry = tk.Entry(root, width=20)
min_price_entry.pack(pady=5)

max_price_label = tk.Label(root, text="Maximum Price (£):")
max_price_label.pack(pady=5)
max_price_entry = tk.Entry(root, width=20)
max_price_entry.pack(pady=5)

check_button = tk.Button(root, text="Check Spelling Mistakes", command=gui_check_spelling_mistakes)
check_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=exit_program)
exit_button.pack(pady=5)

root.mainloop()

