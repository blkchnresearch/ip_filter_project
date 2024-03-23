# IP Filter Project

## Overview
This project aims to set up an application that crawls Tor exit node IP addresses from online repositories and stores them in a local database. Using the FLASK application, we have implemented two REST API endpoints. The first endpoint obtains Tor network IPs and exlcudes the IPs added by the second API endpoint. The Get request collects data and filters while the Post API provides IPs to filter. The two endpoints can run concurrently. 


## Installation
1. Clone repository: git clone https://github.com/blkchnresearch/ip_filter_project
2. Go to project directory: cd ip_filter_project
3. Install dependencies: pip3 install -r requirements.txt
4. I have already provide certificates in the directory. However, you can also generate a self-signed SSL/TLS certificate for secure connections: openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
5. Build: docker-compose build
6. Run: docker-compose up -d  


## Usage
### Endpoints
- **GET /tor**: Get Tor IPs
- **POST /non-tor**: Add IPs to be exluded

### Example CURL Requests
```bash
# Get Tor IPs
curl -k https://localhost:6000/tor

# Add IP to non-Tor list
curl -k -X POST -H "Content-Type: application/json" -d '{"ip": "192.168.1.1"}' https://localhost:6000/non-tor


```



