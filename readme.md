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

3. **You need to add API code to Backend env**

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

4. ** you need to make .env file in frontend **
## Docker 컨테이너 내부에서 `.env` 파일 생성하기

Docker 컨테이너 내부에서 `.env` 파일을 생성하려면 다음 단계를 따르세요:

1) **컨테이너 내부로 진입하기**

   먼저, 실행 중인 Docker 컨테이너 내부에 접근해야 합니다. 이를 위해 다음 명령어를 사용하십시오:
   ```sh
   docker-compose exec frontend bash
   ```

2) **`.env` 파일 생성하기**

   컨테이너 내부에 진입한 후, 원하는 디렉토리로 이동하고 다음 명령어를 사용하여 `.env` 파일을 생성합니다:
   ```sh
   touch .env
   ```

3) **`.env` 파일 편집하기**

   생성된 `.env` 파일을 편집하여 환경 변수를 추가합니다. 예를 들어, `nano` 편집기를 사용하여 파일을 열고 편집할 수 있습니다:
   ```sh
   nano .env
   ```
   `.env` 파일에 환경 변수를 추가
   ```
   REACT_APP_USER_SERVER_URL=http://localhost:8000/account/
   REACT_APP_POST_SERVER_URL=http://localhost:8000/post/
   REACT_APP_SERVER_URL=http://localhost:8000/
   ```

4) **변경 사항 저장하기**

   편집을 마친 후, `Ctrl + X`를 누르고 `Y`를 입력하여 파일을 저장한 후 `Enter`를 누릅니다.

이제 `.env` 파일이 생성되고 설정되었습니다. 필요한 환경 변수를 이 파일에 추가하여 사용할 수 있습니다.


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
