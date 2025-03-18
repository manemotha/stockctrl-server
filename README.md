# Stockctrl Server

A robust stock management solution designed to streamline inventory & cash-register operations.

## Resources

- Python
- Flask
- MongoDB

## Features

- Inventory Management
- Inventory Analytics
- Print, Scan Barcodes (USB barcode printer & scanner)
- Employee Profiles (generated by administrator)  
  > Profile used to access the system, access is limited to features like `Add` or `Sell` item.

## Getting Started

### Install Requirements  

Install project dependencies using `pip install -r requirements.txt`

### Run Server

Replace variable `MONGODB_SERVER_URI` in `/src/config.py` with the **mongodb** connection string and run `main.py` file to start the server.

### Usage Example

Use Postman (an API testing tool) to generate user-account.  
> Format : `JSON` Method : `PUT` Route : `/authentication/signup`

```{
  "username": "tommy.stone",
  "email": "tomstone@email.com",
  "password": "Unique12345678",
  "name":"Tommy Stone",
  "organization": {
    "name":"Tom Stone",
    "type":"athletic footwear and apparel corporation",
    "industry":"fashion"
  }
}
```
