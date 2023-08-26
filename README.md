<div id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br/>

<div align="center">
    <a href="https://github.com/ChaserZ98/Fisher">
        <img src="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0b5061df29d55a92d945_full_logo_blurple_RGB.svg" alt="Logo" height="80">
    </a>
    <h3 align="center">Fisher</h3>
    <p align="center">
        A modularized discord bot based on <a href="https://discordpy.readthedocs.io/en/stable/">discord.py</a> 
        <br />
        <a href="https://github.com/ChaserZ98/Fisher">
            <strong>Explore the docs »</strong>
        </a>
        <br />
        <br />
        <a href="https://github.com/ChaserZ98/Fisher">View Demo</a>
        ·
        <a href="https://github.com/ChaserZ98/Fisher/issues">Report Bug</a>
        ·
        <a href="https://github.com/ChaserZ98/Fisher/issues">Request Feature</a>
    </p>
</div>

<details>
    <summary>Table of Contents</summary>
    <ol>
        <li>
            <a href="#about-the-project">About The Project</a>
            <ul>
                <li><a href="#built-with">Built With</a></li>
            </ul>
        </li>
        <li>
            <a href="#getting-started">Getting Started</a>
            <ul>
                <li><a href="#prerequisites">Prerequisites</a></li>
                <li><a href="#download">Download</a></li>
                <li><a href="#configuration">Configuration</a></li>
                <li>
                    <a href="#launch">Launch</a>
                    <ul>
                        <li><a href="#docker">Docker</a></li>
                        <li><a href="#docker-compose">Docker Compose</a></li>
                    </ul>
                </li>
            </ul>
        </li>
        <li><a href="#usage">Usage</a></li>
        <li><a href="#license">License</a></li>
        <li><a href="#contact">Contact</a></li>
        <li><a href="#acknowledgments">Acknowledgments</a></li>
    </ol>
</details>

## About The Project

This repository provides an implementation of a discord bot with ability to load, unload and reload modules on demand. This allows you to add or remove cogs without rebooting the discord bot and also allows you to hot fix some cogs with a simple reload.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python]][Python-url]
* [![Discord.py][Discord.py]][discord.py-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

You need to have a discord bot account and get your bot token ready.

### Download

- Use `git clone` to directly fetch this repository.
- Download the compressed zip package and unzip it.

### Configuration

Before you start the bot, you need to edit `.env.example` and `config.json.example` provided under `config` folder.

- `.env.exmaple` file

    | Variable          | What it is                                                                |
    | ----------------- | --------------------------------------------------------------------------|
    | BOT_TOKEN         | The token of your bot                                                     |
    | LEETCODE_SESSION  | Your leetcode session token (please see the usage section for details)    |

- `config.json.example` file

    | Variable                  | What it is                                                            |
    | ------------------------- | ----------------------------------------------------------------------|
    | prefix                    | The prefix you want to use for normal commands                        |
    | description               | The content prefixed into the default help message.                   |
    | application_id            | The application ID of your bot                                        |
    | permissions               | The permissions integer your bot needs when it gets invited           |
    | sync_commands_globally    | Set to `true` to enable command sync globally during start up         |
    | use_translator            | Set to `true` to enable command localization support                  |
    | dev_channel_id            | The ID of your default notification channel                           |
    | bot_status                | A list of status you want your bot to switch with along time          |
    | extensions                | A list of extension you want your bot to load during start up         |
    | owners                    | A list of user IDs with the owner priviledge                          |

After editing these two files, do the following steps:

- Move `.env.example` file to the project's root directory (`/path/to/Fisher`)
- Remove the `.example` postfix of two files

### Launch

To launch the bot, you can directly execute `python3 src/bot.py`. Further, if you are familiar with `Docker/Docker Compose`, you can utilize the provided `Dockerfile` and follow the instruction below to dockerize your bot.

#### Docker

If you are familiar with `Docker`, you can directly build the docker image using the provided `Dockerfile` using the below command.

```bash
docker build -t fisher:alpine .
```

Then use the following command to create and start the container.

```bash
docker run -it --rm \
    --name fisher \
    -v /path/to/Fisher:/usr/share/Fisher \
    -w /usr/share/Fisher \
    fisher:alpine python src/bot.py
```

#### Docker Compose

If you are familiar with `Docker Compose`, you can use the following code snippet as an example to be added to your `docker-compose.yml` file.

```YAML
fisher:
    build: /path/to/Fisher
    image: fisher:alpine
    container_name: fisher
    restart: unless-stopped
    volumes:
      - /path/to/Fisher:/usr/share/Fisher
    working_dir: /usr/share/Fisher
    command: python src/bot.py
```

Then you can use the following command to start the project.

```bash
docker compose up -d fisher
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

TODO

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Feiyu Zheng - feiyuzheng98@gmail.com

Project Link: [https://github.com/ChaserZ98/Fisher](https://github.com/ChaserZ98/Fisher)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

* [Img Shields](https://shields.io)
* [discord.py](https://discordpy.readthedocs.io/en/stable/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/ChaserZ98/Fisher.svg?style=for-the-badge
[contributors-url]: https://github.com/ChaserZ98/Fisher/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/ChaserZ98/Fisher.svg?style=for-the-badge
[forks-url]: https://github.com/ChaserZ98/Fisher/network/members

[stars-shield]: https://img.shields.io/github/stars/ChaserZ98/Fisher.svg?style=for-the-badge
[stars-url]: https://github.com/ChaserZ98/Fisher/stargazers

[issues-shield]: https://img.shields.io/github/issues/ChaserZ98/Fisher.svg?style=for-the-badge
[issues-url]: https://github.com/ChaserZ98/Fisher/issues

[license-shield]: https://img.shields.io/github/license/ChaserZ98/Fisher.svg?style=for-the-badge
[license-url]: https://github.com/ChaserZ98/Fisher/blob/master/LICENSE.txt

[Python]: https://img.shields.io/badge/python3-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/

[discord.py]: https://img.shields.io/badge/discord.py-2.3.1-brightgreen
[discord.py-url]: https://discordpy.readthedocs.io/en/stable/
