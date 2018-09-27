# The Secret Club
Permanent storage of censored news articles. Currently many news articles in China are being taken down due to government censorship. The Secret Club is an automated system that persists all potentially controversial articles and shares them with interested parties when they are taken down.

[**Presentation**](https://docs.google.com/presentation/d/1f6QBUlh4zRpCTrE7G_6c_Ss-sIdVdZKSlL6EhzKmiok/edit?usp=sharing)

---

## Sample
There is a dockerized sample that you can run on your machine. The container contains a cron job that will automatically run the scraper every 30 minutes.

**Requirements**:
- Install docker-compose. [Instructions](https://docs.docker.com/compose/install/)
- Create a Telegram bot. [Instructions](https://core.telegram.org/bots#creating-a-new-bot)
- Add the bot token as an environment variable, `TELEGRAM_BOT_TOKEN`
- Create a secret Telegram chat group.
- Add the chat id as an environment variable, `TELEGRAM_SECRET_CLUB_CHAT_ID`

You're all set now! Open a terminal in the [config](./server/config/) directory and run `docker-compose up --build` to let the magic begin.

---

## Extending
The system consists of 4 components which can all be extended to provide different integrations. All configuration should be done in [config.py](./server/src/config.py). Here is a quick rundown of the different components (they are all documented).

### 1) **Web scraper**
The job of the web scraper is to scrape a news site or blog and parse out all the articles. Extend `Scraper` in [scraper.py](./server/src/scraper.py) to use this system on a different site than the default (SixthTone).

### 2) **File storage provider**
The file storage provider handles storage of the article back ups. Extend `FileStorageProvider` in [file_storage.py](./server/src/file_storage.py) to use a provider other than the default (IPFS).

### 3) **Data store provider**
The data store provider handles tracking of the article. Extend `DataStorageProvider` in [data_storage.py](./server/src/data_storage.py) to use a provider other than the default (Redis).

### 4) **Messenger**
The messenger handles distributing links to the back ups of deleted articles to interested parties. Extend `DistributionProvider` in [distributor.py](./server/src/distributor.py) to use a messenger other than the default (Telegram).
