##### building stage #####
FROM python:3.11 as builder

# コンテナ内で必要なパッケージをインストール
RUN apt-get update && apt-get install -y \ 
    build-essential \ 
    libmariadb-dev

RUN apt-get update && apt-get install -y \
    unzip

# chrome driver
ADD https://chromedriver.storage.googleapis.com/109.0.5414.74/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
    unzip chromedriver_linux64.zip && \
    rm -f chromedriver_linux64.zip

# python package
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

#自分で追加したいライブラリ
RUN pip install numpy
RUN pip install janome
RUN pip install Pillow
#RUN pip install tensorflow
RUN pip install requests
RUN pip install beautifulsoup4
RUN pip install lxml
RUN pip install openai

##### production stage #####
FROM python:3.11-slim
#FROM python:3.10 もともとこっちだったけどtkinterがないので下にしてみた
COPY --from=builder /opt/ /opt/
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg

# chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*


ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome

#ここ（production stage）でinstallしないとuvicornがnotfoundになる。
RUN pip install uvicorn[standard]
RUN pip install fastapi

# FastAPIを8000ポートで待機
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
