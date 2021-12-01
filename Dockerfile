RUN apt-get install -y python3 python3-pip* python3-dev python3-aiofiles python3-dotenv

WORKDIR /bot-server

RUN python3 -m pip install -U pynacl
RUN python3 -m pip install -U discord.py 

CMD [ "python3", "./bot.py" ]
