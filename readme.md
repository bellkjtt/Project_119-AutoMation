# 119 AutoMation Project Final Code

## Prerequisites

- Docker
- Docker Compose (optional, if you're using it)
- Node.js
- Anaconda Prompt with Python 3.9.18

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Clone the repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### Build and Push the Docker Images

1. **Login to Docker Hub** (if not already logged in):

    ```bash
    docker login
    ```

2. **Build the Docker images**:

    ```bash
    docker build -t sikaro/aivle:backend -f Dockerfile.backend .
    docker build -t sikaro/aivle:frontend -f Dockerfile.frontend .
    docker build -t sikaro/aivle:socketio -f Dockerfile.backend .
    ```

3. **Push the Docker images to Docker Hub**:

    ```bash
    docker push sikaro/aivle:backend
    docker push sikaro/aivle:frontend
    docker push sikaro/aivle:socketio
    ```

### Run the Docker Containers

To run the entire application using Docker Compose, create a `docker-compose.yml` file with the following content:

```yaml
version: '3.8'

services:
  backend:
    image: sikaro/aivle:backend
    ports:
      - "8000:8000"
    volumes:
      - ./AIVLE_Backend:/app/AIVLE_Backend
    networks:
      - app-network
    extra_hosts:
      - "host.docker.internal:host-gateway"

  frontend:
    image: sikaro/aivle:frontend
    ports:
      - "3000:3000"
    volumes:
      - ./client:/app
    depends_on:
      - backend
    networks:
      - app-network
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - REACT_APP_BACKEND_URL=http://host.docker.internal:8000
      - REACT_APP_SOCKETIO_URL=http://host.docker.internal:5000

  socketio:
    image: sikaro/aivle:socketio
    command: python AIVLE_Backend/socketio_server/server.py
    ports:
      - "5000:5000"
    depends_on:
      - backend
    networks:
      - app-network
    extra_hosts:
      - "host.docker.internal:host-gateway"

networks:
  app-network:
    driver: bridge
```

Then, run the following command to start the containers:

```bash
docker-compose up
```

## Accessing the Application

- React Frontend: [http://localhost:3000](http://localhost:3000)
- Django Backend: [http://localhost:8000](http://localhost:8000)
- WebSocket Server: `ws://localhost:5000`

## Project Structure

Briefly explain the structure of your project, main components, etc.

## Development

Instructions for setting up a development environment, if different from the Docker setup.

### Local Environment Setup

To run the project in a local environment using Anaconda Prompt and Node.js, follow these steps:

1. **Admin Credentials**:
    - 관리자id: admin
    - 관리자 비밀번호: Aivle16!!

2. **Terminal Setup**:
    - Open three terminals for running different parts of the project.

3. **Terminal 1**: Running the Django Backend
    - Navigate to the `AIVLE_Backend` folder:
    ```bash
    cd AIVLE_Backend
    ```
    - Run the Django development server:
    ```bash
    python manage.py runserver
    ```

4. **Terminal 2**: Running the WebSocket Server
    - Navigate to the `AIVLE_Backend/socketio_server` folder:
    ```bash
    cd AIVLE_Backend/socketio_server
    ```
    - Run the WebSocket server:
    ```bash
    python server.py
    ```

5. **Terminal 3**: Running the React Frontend
    - Navigate to the `client` folder:
    ```bash
    cd client
    ```
    - Install dependencies:
    ```bash
    npm i --force
    ```
    - Start the React development server:
    ```bash
    npm start
    ```

6. **Access the React Homepage**:
    - Open your browser and navigate to [http://localhost:3000](http://localhost:3000)

## Deployment

Add additional notes about how to deploy this on a live system, if applicable.

## Built With

- [React](https://reactjs.org/)
- [Django](https://www.djangoproject.com/)
- [Socket.IO](https://socket.io/)
- [Docker](https://www.docker.com/)
