from uuid import uuid4
import re
from fastapi import FastAPI, Response, status
import json
import requests
from pathlib import Path

app = FastAPI()

limit = 250

vendors = None

data_file = Path("data.json")

if not data_file.exists():
    data_file.touch()

@app.get("/")
def read_root():
    return {
        "vendors": len(vendors),
        "products": len([product for domain in vendors for product in vendors[domain]["products"]])
    }

# Vendor
@app.get("/vendors")
def read_vendors():
    return vendors

@app.get("/vendor/{domain}") # The only reason this and the method below exist, is that one day I want to separate product and vendor data likely. I will add vendor metadata, like logo, friendly name, etc.
def read_vendor(domain: str, response: Response):
    if domain in vendors:
        return vendors[domain]
    response.status_code = status.HTTP_404_NOT_FOUND

    return {}

@app.get("/vendor/{domain}/products")
def read_vendor(domain: str, response: Response):
    if domain in vendors:
        return vendors[domain]["products"]
    response.status_code = status.HTTP_404_NOT_FOUND

    return {}

@app.get("/vendor/{domain}/scan")
def read_vendor(domain: str, response: Response):
    if domain in vendors:
      results = requests.get(f"https://{domain}/products.json?limit={limit}&page=1") # TODO support pagination/multiple sets of data, as some vendors will have more than 250 item
      if results.status_code == 200:
        vendors[domain]["products"] = __process_raw__(results.json(), domain)
        __save__()
        
        return {"Success": True, "products_scanned": len(vendors[domain]["products"])}
    
    response.status_code = status.HTTP_404_NOT_FOUND

    return {"Error": "Vendor not found"}

@app.put("/vendor/{domain}")
def add_vendor(domain: str, response: Response):
    response.status_code = status.HTTP_400_BAD_REQUEST
    if domain in vendors:
        return {"Error": "Domain already stored"}
    
    pattern = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$')
    if bool(pattern.match(domain)):
      vendors[domain] = {
          "products": []
          }
      response.status_code = status.HTTP_200_OK
      __save__()

      return vendors[domain]

    return {"Error": "Poorly formatted domain, please only put the domain"}

@app.delete("/vendor/{domain}")
def delete_vendor(domain: str, response: Response):
    popped = vendors.pop(domain, None)
    response.status_code = status.HTTP_404_NOT_FOUND
    if popped:
      response.status_code = status.HTTP_200_OK
      __save__()

    return {"Success": True} if popped else {}
        

# Product
def __find_product__(id: str):
    found_product = False
    for vendor in vendors:
      for product in vendors[vendor]["products"]:
          if id == product["id"]:
              found_product = product.copy()
              found_product["vendor"] = vendor
              break
      
      if found_product:
          break
    
    return found_product

@app.get("/products")
def get_products():
    products = []
    for domain in vendors:
        for product in vendors[domain]["products"]:
            product_new = product.copy()
            product_new["vendor"] = domain
            products.append(product_new)
    return products

@app.get("/product/{id}")
def read_product(id: str, response: Response):
    found_product = __find_product__(id)
    response.status_code = status.HTTP_404_NOT_FOUND
    if found_product:
        response.status_code = status.HTTP_200_OK

    return found_product if found_product else {}

@app.put("/product")
def add_product(name: str, domain: str, price: float):
    product = {
        "id": str(uuid4()),
        "name": name,
        "price": price
    }
    vendors[domain]["products"].append(product)
    __save__()
    return product

@app.delete("product/{id}")
def delete_product(id: str):
    pass

# Raw

def __process_raw__(raw: list, domain: str):
    new_products = []
    for product in raw["products"]:
        prices = [float(variant["price"]) for variant in product["variants"]]
        price = 0.00
        if len(prices) > 1 and min(prices) != max(prices):
            price = {
                "min": min(prices),
                "max": max(prices)
            }
        else:
            price = prices[0]
        new_products.append({
            "id": str(uuid4()),
            "name": product["title"],
            "url": f"https://{domain}/products/{product['handle']}",
            "price": price
        })
    return new_products

# Misc

def __save__(): # TODO move this to a form of database. Flatfile is a temporary solution. SQLite might work, but needs replication for sure.
    print("Saving vendor data...")
    with open("data.json", "w") as rawWrite:
        json.dump(vendors, rawWrite)

    print("Done")

def __load__():
    print("Loading vendor data...")
    with open("data.json", "r") as rawRead:
        global vendors
        vendors = json.load(rawRead)
    print("Done")

__load__()