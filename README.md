# Stockctrl Server

A robust stock management solution designed to streamline inventory & point-of-sale (POS) operations.

## Resources

- Python
- Uvicorn
- FastAPI
- MongoDB

## Features

- Inventory Management
- Inventory Analytics
- Print, Scan Barcodes (USB barcode printer & scanner)
- Admin Account
- Employee Account (generated using Admin's valid session-token)
- Multiple Businesses

## Getting Started

### Install Requirements  

Install project dependencies using `pip install -r requirements.txt`

### Run Server

Replace variable `MONGODB_SERVER_URI` in `.env` with the **mongodb** connection string and run `main.py` file to start the server.

### Usage Example

Use [Postman](https://www.postman.com/downloads/) (an API testing tool) to generate user-account.  
> Format : `JSON` Method : `POST` Route : `/api/admins/session`

```{
  "username": "tommystone",
  "email": "tomstone@email.com",
  "password": "Unique12345678",
  "name":"Tommy Stone",
}
```
