# 🤖 Bounty Bridge Bot

[![TON](https://img.shields.io/badge/TON-grey?logo=TON&logoColor=40AEF0)](https://ton.org)
[![Telegram Bot](https://img.shields.io/badge/Bot-grey?logo=telegram)](https://core.telegram.org/bots)
![Python Versions](https://img.shields.io/badge/Python-3.10-black?color=FFE873&labelColor=3776AB)
[![License](https://img.shields.io/github/license/nessshon/aiogram-starlette-template)](https://github.com/nessshon/aiogram-starlette-template/blob/main/LICENSE)

![image](https://github.com/ton-society/grants-and-bounties/raw/main/assets/cover.png)

[![Starlette](https://img.shields.io/badge/Starlette-admin-white?logo=starlette&logoColor=black)](https://www.starlette.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-white?logo=fastapi&logoColor=green)](https://fastapi.tiangolo.com/)
[![Telegram](https://img.shields.io/badge/Login_Widget-white?logo=telegram&logoColor=blue)](https://telegram.org/)
[![PHPMyAdmin](https://img.shields.io/badge/PHPMyAdmin-white?logo=php&logoColor=green)](https://www.phpmyadmin.net/)
[![MySQL](https://img.shields.io/badge/MySQL-white?logo=mysql&logoColor=red)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-Yes?logo=redis&color=white)](https://redis.io/)
[![Certbot](https://img.shields.io/badge/Certbot-white?logo=letsencrypt&logoColor=red)](https://certbot.eff.org/)
[![Nginx](https://img.shields.io/badge/Nginx-white?logo=nginx&logoColor=green)](https://www.nginx.com/)
[![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white)](https://www.docker.com/)

The bot monitors [repository](https://github.com/ton-society/grants-and-bounties) for new challenges, automatically
informing developer chats about new rewards. It solicits opinions and participation, display relevant tags and include
an interactive button for easy reward creation.

* Telegram Bot: [@BountyBridgeBot](https://t.me/BountyBridgeBot)
* Admin Panel: [app.bountybot.ness.su](https://app.bountybot.ness.su)
* phpMyAdmin: [pma.bountybot.ness.su](https://pma.bountybot.ness.su)

## Features

- [Aiogram 3x](https://github.com/aiogram/aiogram/) as Telegram Bot API
- [FastAPI](https://github.com/tiangolo/fastapi/) for separate API Routes
- [Starlette-Admin](https://github.com/jowilf/starlette-admin/) as web Admin Panel
- [Telegram Login Widget](https://core.telegram.org/widgets/login/) for admin authorization

## Project Components:

* **MySQL** - Database management system.
* **Nginx** - Proxy server for routing and handling web requests.
* **Certbot** - SSL certificate management and issuance.
* **phpMyAdmin** - Web-based database administration tool.
* **Admin Panel** - Custom web interface for administrative tasks.
* **Telegram Bot** - Bot implementation for interacting on Telegram.
* **Redis** - In-memory data structure store.

## Launch and deployment:

<details>
<summary><b>Preparation</b></summary>

Clone this repo:

```bash
git clone https://github.com/nessshon/bounty-bridge-bot.git
```

Go to the project folder:

```bash
cd bounty-bridge-bot
```

Clone environment variables file:

```bash
cp .env.example .env
```

Configure [environment variables](#environment-variables-reference) variables file:

```bash
nano .env
```

</details>

<details>
<summary><b>Local launch</b></summary>

Install dependencies

```bash
pip install -r requirements.txt
```

Launch project:

```bash
python -m project
```

</details>

<details>
<summary><b>Deployment and launch</b></summary>

Change server_name on [phpmyadmin.conf](services/nginx/user_conf.d/phpmyadmin.conf):

```nginx
server_name pma.your-domain.com www.pma.your-domain.com;
```

Change server_name on [project.conf](services/nginx/user_conf.d/project.conf) :

```nginx
server_name app.your-domain.com www.app.your-domain.com;
```

Install Docker and docker-compose:

```bash
apt install docker.io docker-compose -y
```

Deploy the project:

```bash
docker-compose up --build
```

* The deployment script handles the creation of containers for MySQL and Redis.
* Configures MySQL and Redis databases.
* Configures Nginx as a proxy server for web requests.
* Uses Certbot to generate and renew SSL certificates for secure communications.
* Launches the admin panel, Telegram Bot and phpMyAdmin.

Before deploying the project, be sure to configure the virtual environment configurations.\
Additional configuration parameters are located in [.env.example](.env.example).

</details>

## Environment Variables Reference

Here is a reference guide for the environment variables used in the project:
<details>
<summary><b>Expand to view</b></summary>

| Variable            | Type | Description                                                         | Example Local             | Example Prod        |
|---------------------|------|---------------------------------------------------------------------|---------------------------|---------------------|
| BOT_TOKEN           | str  | Bot token, obtained from [@BotFather](https://t.me/BotFather)       | 123456:qweRTY             | 123456:qweRTY       | 
| BOT_USERNAME        | str  | The username of the bot                                             | same_bot                  | same_bot            |
| BOT_DEV_ID          | int  | User ID of the bot developer                                        | 123456789                 | 123456789           |
| BOT_ADMIN_ID        | int  | User ID of the bot administrator                                    | 123456789                 | 123456789           |
| GITHUB_TOKEN        | str  | GitHub token (you can obtain this from your GitHub account)         | ghp_BWC...ZzD             | ghp_BWC...ZzD       |
| GITHUB_OWNER        | str  | GitHub owner (organization or user) where the repository is located | ton-society               | ton-society         |
| GITHUB_REPO         | str  | GitHub repository name                                              | grants-and-bounties       | grants-and-bounties |
| APP_URL             | str  | The domain of the webhook                                           | https://...ngrok.free.app | https://example.com |
| APP_HOST            | str  | The host address where the app is running                           | localhost                 | 0.0.0.0             |
| APP_PORT            | int  | The port number on which the app is listening                       | 8000                      | 8000                |
| WEBHOOK_SECRET      | str  | Secret key for securing the webhook                                 | qwerty12345               | qwerty12345         |
| WEBHOOK_PATH        | str  | The path of the webhook                                             | /bot                      | /bot                |
| REDIS_HOST          | str  | The hostname or IP address of the Redis server                      | localhost                 | redis               |
| REDIS_PORT          | int  | The port number on which the Redis server is running                | 6379                      | 6379                |
| REDIS_DB            | int  | The Redis database number                                           | 0                         | 0                   |
| MYSQL_ROOT_PASSWORD | str  | Root password for MySQL                                             | --skip--                  | root-password       |  
| MYSQL_HOST          | str  | The hostname or IP address of the database server                   | localhost                 | localhost           |
| MYSQL_PORT          | int  | The port number on which the database server is running             | 3306                      | 3306                |
| MYSQL_USER          | str  | The username for accessing the database                             | user                      | user                |
| MYSQL_PASSWORD      | str  | The password for accessing the database                             | password                  | password            |
| MYSQL_DATABASE      | str  | The name of the database                                            | dbname                    | dbname              |
| CERTBOT_EMAIL       | str  | Email address for Certbot notifications                             | --skip--                  | example@mail.com    |

</details>

## Contribution

We welcome your contributions! If you have ideas for improvement or have identified a bug, please create an issue or
submit a pull request.

## Support

Supported by [TON Society](https://github.com/ton-society/grants-and-bounties), Grants and Bounties program.

## License

This repository is distributed under the [MIT License](https://github.com/nessshon/bounty-bridge-bot/blob/main/LICENSE).
