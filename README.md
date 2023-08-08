# simple-keyboard-service

This is a very basic Python service. You can add vendors, add products manually, scan vendor sites for products for automation. It's not complete by any means, but I'm going for the KISS of data storage and collection for now.

## Important notes!

This is not production ready. It's very WIP. GET, PUT, DELETE all are unauthenticated. They _just work_. As well, data is entirely stored in a single JSON file until I add more functionality. Be careful!

## Installation

### Prerequisites

Docker, or Python 3.6+ at least.

I'd recommend using [rye](https://github.com/mitsuhiko/rye) and running `rye sync` in the root of the project. I truly do not know when this would NOT be compatible, but I am using f-strings. I'd recommend 3.11 as that's what I used.

## Usage

### Running

One command to start the server. I am using fastapi, so uvicorn was the obvious choice:

```sh
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Endpoints

API is as follows thus far:

- `GET /`

Returns some basic statistics, being vendor and product count.

- `GET /vendors`

TODO: Returns all vendors and their data. Maybe only domains in the future?

- `GET /products`

Returns all products and what vendor each belongs to.

#### Vendor-specific

- `GET, PUT, DELETE /vendor/{domain}`

TODO: GET: Return a vendor and all of their products. I'd like to not return products in the future.

PUT: Add a vendor

DELETE: Remove a vendor

- `GET /vendor/{domain}/products`

Returns only the products of a given vendor

- `GET /vendor/{domain}/scan`

Scans a vendor using Shopify's `/products.json` endpoint. All Shopify sites have this. I use a limit of 250 in my query as that is the max from Shopify. 99% of vendors, this covers all products.

#### Product-specific

- `PUT /product`

TODO: Adds a product. You need to specify the name and price. This is currently not fully compatible and will break things likely. Just use `/vendor/{domain}/1scan` for now.

- `GET, DELETE /product/{id}`

Gets or deletes a product