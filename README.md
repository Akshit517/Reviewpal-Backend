<a id="readme-top"></a>
<h3 align="center">ReviewPal - Backend</h3>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#overview">Overview</a>
    </li>
    <li>
      <a href="#features">Features</a>
    </li>
    <li>
      <a href="#tech-stack">Tech Stack</a>
    </li>
    <li>
      <a href="#erd">ERD</a>
    </li>    
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

---

## Overview
ReviewPal is a comprehensive assignment management and review platform designed to enhance productivity in educational and professional environments. This repository hosts the robust **Django backend**, providing a powerful REST API that drives the entire system. It features real-time collaboration, structured workspaces, and streamlined review processes.

Explore the user interface: [ReviewPal-Frontend](https://github.com/Akshit517/Reviewpal-Frontend)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Features

ReviewPal offers a set of features designed to streamline your workflow and enhance collaboration:

- **Authentication**:
  - Traditional username-password authentication.
  - Channel I OAuth and Google OAuth.
- **Workspace Management**:
  - Create multiple workspaces.
  - Role-based access control for each workspace.
- **Assignment Management**:
  - Create, edit, and allocate assignments.
  - Add sub-tasks.
  - Multi-iteration review process with comments.
- **Review & Feedback**:
  - Multiple reviewers can assess assignments.
  - Real-time notifications via WebSockets.
- **Team Submissions**:
  - Enables group submissions for assignments.
- **Real-Time Updates**:
  - Uses **Daphne** and **Django Channels** for WebSockets.
  - Integrated chat system.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Tech Stack
The ReviewPal backend is built with the following technologies:

- **Django + Django REST Framework (DRF)**: The core backend framework for building robust APIs.
- **PostgreSQL**: A powerful relational database for storing structured data.
- **Daphne + Django Channels**: Used for WebSocket communication, enabling real-time features.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## ERD

Here's the Entity Relationship (ER) Diagram for the ReviewPal backend: [Lucidchart](https://lucid.app/lucidchart/3d06258e-6f3e-4374-a3ee-6ec3c651c23d/edit?page=0_0&invitationId=inv_5ad40539-bc02-4fbd-9a39-bdd21c3e3549#)

> **_NOTE:_** Some parts of the ERD have been updated in the repository and may not be fully reflected in the linked document.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started
To get a local copy of the ReviewPal backend up and running, follow these simple steps.

### Prerequisites
Before you begin, ensure you have the following installed on your system:
- **Python**: Latest stable version.
- **PostgreSQL**: Database server.
- **Redis**: For background tasks and caching.
- **Virtualenv** (optional but recommended): For managing project dependencies.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Akshit517/Reviewpal-Backend.git
    ```
2.  **Navigate into the project directory:**
    ```bash
    cd Reviewpal-Backend
    ```
3.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure environment variables:**
    Navigate into the Django project directory (`asg_rev/`), rename `.env.example` to `.env`, and fill in the required fields with your specific configurations.
    ```bash
    cd asg_rev/
    mv .env.example .env
    # Now, open .env with your preferred text editor (e.g., vim .env or nano .env) and fill in the details.
    ```
6.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```
7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    Your backend API will now be running, typically at `http://127.0.0.1:8000/`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Contact
Have questions about this repository? Feel free to reach out directly via [email](mailto:akshitmandial517@gmail.com)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
