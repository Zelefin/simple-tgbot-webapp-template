# Lightweight Telegram Bot With Web App Template

This repository contains a simple and lightweight template for building a Telegram bot with a web app. It provides a solid foundation for quickly developing and deploying Telegram bots with integrated web applications.

Preview of web app in both light and dark themes:

![IMG_2509(1)](https://github.com/user-attachments/assets/ed617564-fbee-4cc4-9fcc-9a5fdd89b069)
![IMG_2510(1)](https://github.com/user-attachments/assets/581482f3-f31e-4f03-867e-7eccd7055583)

Live demo: [@webapp_template_bot](https://t.me/webapp_template_bot)

This template is built upon:

- [Telegram Mini Apps React Template](https://github.com/Telegram-Mini-Apps/reactjs-template)
- [tgbot_template_v3](https://github.com/Latand/tgbot_template_v3)

## Features

### Backend

- [aiogram](https://github.com/aiogram/aiogram) for handling Telegram Bot API
- [aiohttp](https://docs.aiohttp.org/) for asynchronous HTTP requests
- [SQLite](https://www.sqlite.org/) (aiosqlite3 + sqlalchemy) for lightweight, serverless database management
- Optional: [Redis](https://redis.io/) for fast, in-memory data structure store

### Frontend

- [React](https://react.dev/) for building user interfaces
- [TypeScript](https://www.typescriptlang.org/) for type-safe JavaScript
- [@telegram-apps SDK](https://docs.telegram-mini-apps.com/packages/telegram-apps-sdk) for Telegram Mini Apps integration
- [Telegram UI](https://github.com/Telegram-Mini-Apps/TelegramUI) for consistent Telegram-style UI components
- [Vite](https://vitejs.dev/) for fast development and optimized builds

### Deployment

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for containerization
- Optional: [Systemctl](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units) for service management
- [Nginx](https://nginx.org/en/) with [Certbot](https://certbot.eff.org/) for reverse proxy and SSL

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/Zelefin/simple-tgbot-webapp-template.git
   cd simple-tgbot-webapp-template
   ```

2. Set up the backend:

   By default Redis is not installed. If you need Redis just uncomment it in `requirements.txt`

   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:

   ```
   cd frontend/web-app
   npm install
   ```

4. Configure the application:
   - Rename `.env.dist` to `.env`.
   - Update the `.env` files with your specific configuration
   - Update the `base` in `vite.config.ts` to match your web app name. It should be the same as `BOT_WEB_APP_NAME` in `.env` e.g. `/simple-web-app`.
   - Create a web app in [BotFather](https://t.me/botfather):
     - Use the `/newapp` command to create a new web app for your bot
     - Set the URL like `https://yourdomain.com/simple-web-app`
     - Set web app short name to be the same as `BOT_WEB_APP_NAME` in `.env`, except replace `-` with `_` (since `-` is not allowed in web app short name). It's easy to handle this in code by simply adding `.replace('-', '_')` to the place where you sending web app URL

> [!TIP]
> I highly recommend using [Ngrok](https://ngrok.com/) for development. Just obtain domain name and set it as `WEB_DOMAIN` in `.env`. Don't forget to provide new link to botfather too.

## Usage

1. Build frontend:

   ```
   cd frontend/web-app
   npm run build
   ```

2. Start the bot:

   ```
   cd ../..
   python3 main.py
   ```

> [!TIP]
> I recommend using webhooks, since it goes out of box because we already launching an aiohttp server.

### Adding more web apps

It's quite simple to add one or more web apps to bot with this template. Simply follow this steps:

1. Add new field in .env. For example:

   ```
   BOT_NEW_WEB_APP_NAME=new-web-app
   ```

2. Add new variable to TgBot class in `config_reader.py`:

   ```
   new_web_app_name: str
   ```

3. Create file in `infrastructure/api` (e.g `new_web_app_routes.py`) where all the routes for web app will be. Create function like:

   ```
   def setup_new_web_app_routes(app: Application):
   ```

   where all the routes and assets will be added to application. See `simple_web_app_routes.py` for example

4. In `main.py` add:

   ```
   new_web_app = web.Application()
   ... # pass anything you need
   new_web_app["web_app_name"] = config.tg_bot.new_web_app_name
   setup_new_web_app_routes(new_web_app)
   app.add_subapp(f"/{config.tg_bot.new_web_app_name}", new_web_app)
   ```

5. Create new handler in `bot/handlers` with all the commands that you need, just don't forget to add them to `bot/misc/default_commands.py`. Also, if you use `-` in web app name, make sure to set `.replace('-', '_')` where you sending web app url.

6. Create new project in `/frontend`, you can use [Telegram Mini Apps React Template](https://github.com/Telegram-Mini-Apps/reactjs-template) or whatever you want, the only imporant part _(if you configured your routes to depend on config variable)_ is that project folder name should be the same as `BOT_NEW_WEB_APP_NAME` in `.env`.

7. Change `base` in `vite.config.ts` to be the same as `BOT_NEW_WEB_APP_NAME` in `.env` and run

   ```
   npm run build
   ```

8. Create web app in [Botfather](https://t.me/botfather), where URL should be `https://yourdomain.com/new-web-app` (same as `BOT_NEW_WEB_APP_NAME` in `.env`) and web app short name should be same as `BOT_NEW_WEB_APP_NAME` in `.env`, but replace `-` with `_`.

## Deployment

You can use docker-compose or systemd for deployment.

### Docker-compose

> [!NOTE]
> If you use Redis uncomment `redis_cache` service, `cache` volume and `bot` service dependency in `docker-compose.yml`.

Simply run this command:

```
docker-compose up -d --build
```

### Systemd

For systemd you can use `other/TgBot.service` - just replace the `WorkingDirectory` and `ExecStart` paths with the actual locations on your system.

Then:

1. Copy .service file into `/etc/systemd/system/`:

   ```
   sudo cp TgBot.service /etc/systemd/system/
   ```

2. Enable sevrice:

   ```
   sudo systemctl enable TgBot.service
   ```

3. And finally start the service:
   ```
   sudo systemctl start TgBot.service
   ```

From my experience launching bot this way consumes same amount of RAM as docker, so I'd recommend using docker.

In any case then you only need to:

### Nginx

1. Configure Nginx as a reverse proxy (configuration provided in `other/nginx_conf`).

2. Set up SSL with Certbot:
   ```
   certbot --nginx -d yourdomain.com
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
