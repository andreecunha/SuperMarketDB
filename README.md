# DataStoreManager

This project presents the design and implementation of a Data Storage and Management System (DSMS) for a supermarket chain. It integrates key database functionalities to store and manage business operations efficiently. The system includes the creation of a relational database, ETL processing, and the implementation of multiple endpoints for seamless interaction with the data.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Installation Guide](#installation-guide)
4. [Usage Guide](#usage-guide)
5. [Development Plan](#development-plan)
6. [Security and Integrity](#security-and-integrity)
7. [Conclusion](#conclusion)

---

## Project Overview

The objective of this project was to develop a robust system for storing and managing data related to a supermarket chain. The system supports:
- Efficient storage of business operations and characteristics.
- Seamless execution of queries and transactions via predefined endpoints.
- Strong data integrity and security measures.

The project involved designing and implementing the relational database, inserting sample data provided by the professor, and developing a series of endpoints for interacting with the database.

---

## Key Features

- **Relational Database:** Designed using an Entity-Relationship model to structure business data efficiently.
- **ETL Pipeline:** Automates data extraction, transformation, and loading into the database.
- **Dynamic Endpoints:** Provides 12 endpoints for CRUD operations and other tasks, accessible via Postman or a web interface.
- **Landing Page:** A user-friendly starting point available at `127.0.0.1:8080/`.
- **Secure Transactions:** Ensures data consistency with commit operations only after successful transaction execution.
- **Password Encryption:** Passwords are securely stored using environment variables.

---

## Installation Guide

Follow these steps to set up the system:

1. Download the ZIP file or clone the repository:
   ```bash
   git clone https://github.com/andreecunha/SuperMarketDB.git
