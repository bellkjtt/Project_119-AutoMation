# Project Name

Brief description of your project.

## Prerequisites

- Docker
- Docker Compose (optional, if you're using it)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Clone the repository

```
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### Build the Docker image

```
docker build -t sikaro/aivle:multiport .
```

### Run the Docker container

```
docker run -p 3000:3000 -p 8000:8000 -p 5000:5000 sikaro/aivle:multiport
```

## Accessing the Application

- React Frontend: http://localhost:3000
- Django Backend: http://localhost:8000
- WebSocket Server: ws://localhost:5000

## Project Structure

Briefly explain the structure of your project, main components, etc.

## Development

Instructions for setting up a development environment, if different from the Docker setup.

## Deployment

Add additional notes about how to deploy this on a live system, if applicable.

## Built With

- [React](https://reactjs.org/) - The web framework used
- [Django](https://www.djangoproject.com/) - The backend framework
- [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) - For real-time communication

## Contributing

Instructions for how to contribute to your project.

## License

This project is licensed under the [LICENSE NAME] - see the [LICENSE.md](LICENSE.md) file for details


관리자id : admin
관리자 비밀번호 : Aivle16!!

진행환경 : anaconda prompt 가상환경 Python 3.9.18

node js 설치 필요.

기본적으로 로컬 환경에서 동작
터미널 3개 필요

터미널1
AIVLE_Backend 폴더에서 
python manage.py runserver

터미널2
AILVE_Backend/soketio_server 폴더에서
python server.py

터미널3
client 폴더에서 

npm i --force

후에

npm start

리액트 홈페이지 동작