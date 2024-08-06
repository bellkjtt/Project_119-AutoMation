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

### Pull and Run the Docker Containers

1. **Login to Docker Hub** (if not already logged in):
```bash
docker login
```

2. **Pull the Docker images from Docker Hub**:
```bash
docker pull sikaro/aivle:backend
docker pull sikaro/aivle:frontend
docker pull sikaro/aivle:socketio
```

3. **You need to add ChatGPT API code to Backend env**

```docker-compose.yml
 version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./AIVLE_Backend:/app/AIVLE_Backend
    networks:
      - app-network
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - OPENAI_API_KEY=<your-openai-api-key> #add it here
      - KAKAO_API_KEY=<your-kakao-api-key> #add it here
      - NAVER_API_KEY=<your-NAVER-api-key> #add it here
```

4. **Run the Docker containers**:
```bash
docker-compose up
```

## Accessing the Application

- React Frontend: http://localhost:3000
- Django Backend: http://localhost:8000
- WebSocket Server: ws://localhost:5000

## Project Structure

-React
-Django
-Socket.IO
-Web Speech API
-Docker
-Naver Clova STT
-KaKao Map API
-Hunggingface Transformers
-Sqlite3

### Running Locally with Anaconda and Node.js

1. **Backend**:
   - Open Anaconda Prompt
   - Navigate to `AIVLE_Backend` folder
   - Run:
   ```bash
   python manage.py runserver
   ```

2. **SocketIO Server**:
   - Open a new terminal
   - Navigate to `AIVLE_Backend/socketio_server` folder
   - Run:
   ```bash
   python server.py
   ```

3. **Frontend**:
   - Open a new terminal
   - Navigate to `client` folder
   - Install dependencies:
   ```bash
   npm i --force
   ```
   - Start the React application:
   ```bash
   npm start
   ```

## Built With

- [React](https://reactjs.org/)
- [Django](https://www.djangoproject.com/)
- [Socket.IO](https://socket.io/)

## Admin Credentials

- 관리자id: admin
- 관리자 비밀번호: Aivle16!!

## Environment

- Node.js 설치 필요.
- 기본적으로 로컬 환경에서 동작
- 터미널 3개 필요

- 터미널1:
  - AIVLE_Backend 폴더에서 
  ```bash
  python manage.py runserver
  ```

- 터미널2:
  - AIVLE_Backend/socketio_server 폴더에서
  ```bash
  python server.py
  ```

- 터미널3:
  - client 폴더에서 
  ```bash
  npm i --force
  npm start
  ```
  - 리액트 홈페이지 동작
