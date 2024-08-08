# Lightweight Telegram Bot With Web App Template

This repository contains a simple and lightweight template for building a Telegram bot with a web app. It provides a solid foundation for quickly developing and deploying Telegram bots with integrated web applications.

It's good for small projects and projects with limited resources, since it takes only ~150MB of RAM for the whole template to run.

Preview of web app in both light and dark themes:

<img src="https://github.com/user-attachments/assets/ed617564-fbee-4cc4-9fcc-9a5fdd89b069" width=50% height=50%>

Live demo available here: [@webapp_template_bot](https://t.me/webapp_template_bot)

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

   By default, Redis is not installed. If you need Redis, just uncomment it in `requirements.txt`.

   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:

   ```
   cd frontend/simple-web-app
   npm install
   ```

4. Configure the application:
   - Rename `.env.dist` to `.env`.
   - Update the `.env` file with your specific configuration.
   - Create a web app in [BotFather](https://t.me/botfather) using `/newapp` command:
     - Set the URL to `https://yourdomain.com/simple-web-app`.
     - Set the web app short name to `simple_web_app`, we need to replace `-` with `_`, since `-` is not allowed in web app short names.

> [!TIP]
> For development, consider using [Ngrok](https://ngrok.com/). Obtain a domain name and set it as `WEB_DOMAIN` in `.env`. Remember to provide the new link to BotFather as well.

## Usage

1. Build frontend:

   ```
   cd frontend/simple-web-app
   npm run build
   ```

2. Start the bot:

   ```
   cd ../..
   python3 main.py
   ```

> [!TIP]
> I recommend using webhooks, as they're ready to use out of the box due to the already launched aiohttp server.

### Changing web app name

To set your custom web app name (for example we'll use `my-web-shop`) instead of `simple-web-app` follow those steps:

1. Change `BOT_WEB_APP_NAME` in `.env`:

   ```
   BOT_WEB_APP_NAME=my-web-shop
   ```

2. Configure `infrastructure/api/web_app_routes.py` and `bot/handlers/web_app.py` for your needs.

3. Rename `frontend/simple-web-app` to `frontend/my-web-shop`.

4. Change `base` in `vite.config.ts` to `/my-web-shop`. Keep in mind that existing code in `IndexPage.tsx` uses `fetch('/simple-web-app/greet')` so simply change it to `fetch('my-web-shop/greet')` or write your own application.

5. Run

   ```
   npm run build
   ```

   in `frontend/my-web-shop` directory.

6. Create new web app in [BotFather](https://t.me/botfather), where the URL should be `https://yourdomain.com/my-web-shop` and the web app short name: `my_web_shop`.

### Adding more web apps

To add one or more web apps to your bot with this template, follow these steps:

1. Add a new field in `.env`. For example:

   ```
   BOT_NEW_WEB_APP_NAME=new-web-app
   ```

2. Add a new variable to the TgBot class in `config_reader.py`:

   ```python
   new_web_app_name: str
   ```

3. Create a file in `infrastructure/api` (e.g., `new_web_app_routes.py`) where all the routes for the web app will be. Create a function like:

   ```python
   def setup_new_web_app_routes(app: Application):
   ```

   where all the routes and assets will be added to the application. See `simple_web_app_routes.py` for an example.

4. In `main.py`, add:

   ```python
   new_web_app = web.Application()
   ... # pass anything you need
   new_web_app["web_app_name"] = config.tg_bot.new_web_app_name
   setup_new_web_app_routes(new_web_app)
   app.add_subapp(f"/{config.tg_bot.new_web_app_name}", new_web_app)
   ```

5. Create a new handler in `bot/handlers` with all the commands you need. Add new router to `handlers/__init__.py` and new commands to `bot/misc/default_commands.py`. Also, if you use `-` in the web app name, make sure to use `.replace('-', '_')` when sending the web app URL.

6. Create a new project in `/frontend`. You can use [Telegram Mini Apps React Template](https://github.com/Telegram-Mini-Apps/reactjs-template) or any framework you prefer. The only important part (if you configured your routes to depend on the config variable) is that the project folder name should be the same as `BOT_NEW_WEB_APP_NAME` in `.env`.

7. Change `base` in `vite.config.ts` to be the same as `BOT_NEW_WEB_APP_NAME` in `.env` and run:

   ```
   npm run build
   ```

8. Create a web app in [BotFather](https://t.me/botfather), where the URL should be `https://yourdomain.com/new-web-app` (same as `BOT_NEW_WEB_APP_NAME` in `.env`) and the web app short name should be the same as `BOT_NEW_WEB_APP_NAME` in `.env`, but replace `-` with `_`.

## Deployment

You can use Docker Compose or systemd for deployment.

### Docker Compose

> [!NOTE]
> If you use Redis, uncomment the `redis_cache` service, `cache` volume, and `bot` service dependency in `docker-compose.yml`.

> [!IMPORTANT]
> Don't forget to configure your ports in `docker-compose.yml` if you not using default 8080: `ports:- "your_port:8080"`; and then in nginx configuration: `proxy_pass http://127.0.0.1:your_port;`

Simply run this command:

```
docker-compose up -d --build
```

### Systemd

For systemd, you can use `other/TgBot.service` - just replace the `WorkingDirectory` and `ExecStart` paths with the actual locations on your system.

Then:

1. Copy the .service file into `/etc/systemd/system/`:

   ```
   sudo cp TgBot.service /etc/systemd/system/
   ```

2. Enable the service:

   ```
   sudo systemctl enable TgBot.service
   ```

3. Start the service:
   ```
   sudo systemctl start TgBot.service
   ```

From experience, launching the bot this way consumes about the same amount of RAM as Docker, so I recommend using Docker.

### Nginx Configuration

1. Configure Nginx as a reverse proxy (configuration example provided in `other/nginx_conf`). Save your configuration in `/etc/nginx/sites-available/yourdomain.com` and create symlink like so:

   ```
   sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
   ```

2. Set up SSL with Certbot:
   ```
   certbot --nginx -d yourdomain.com
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
