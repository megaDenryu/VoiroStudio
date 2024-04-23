import pytchat
from pytchat import LiveChatAsync
from pytchat.processors.default.processor import Chatdata
import asyncio
from pprint import pprint
import time


class YoutubeCommentRecieverOld:
    def __init__(self, url=None, video_id=None):
        if url is None and video_id is None:
            print("urlかvideo_idのどちらかを指定してください")
            return False
        if video_id is not None:
            self.video_id = video_id
            self.chat = pytchat.create(video_id=self.video_id)
        if url is not None:
            self.url = url
            try:
                self.video_id = self.filteringVideoId(url)
                self.chat = pytchat.create(video_id=self.video_id)
            except Exception as e:
                print(e)
                if e == "URLが不正です":
                    return False
                
    def filteringVideoId(self,url:str):
        if "watch?v=" not in url:
            print("URLが不正です")
            raise Exception("URLが不正です")
        video_id = url.split("watch?v=")[1]
        if video_id == "":
            print("URLからvideo_idを取得できませんでした")
            raise Exception("URLからvideo_idを取得できませんでした")
        return video_id            
    
    def getComments(self):
        while self.chat.is_alive():
            for c in self.chat.get().sync_items():
                comment = {}
                comment["datetime"] = c.datetime
                comment["author"] = c.author.name
                comment["message"] = c.message
                pprint(comment)
                yield comment

    
    """
    以下は非同期処理

    pythonでyoutubeのコメントを取得するプログラムを作っています。
    
    """
    

    async def main(self):
        livechat = LiveChatAsync(
            video_id=self.video_id
            )
        while True:
            try:
                comment = await livechat.get()
                if type(comment) == Chatdata:
                    pprint(["Chatdata",vars(comment)],indent=4)
                    await comment.tick_async()
                else:
                    print(type(comment),comment)
                await asyncio.sleep(5)
                
            except Exception as e:
                print(e)
            # print(f"{comment.datetime} [{comment.author.name}]-{comment.message} {comment.amountString}")


    async def func(self,chatdata):
        for comment in chatdata.items:
            print(f"{comment.datetime} [{comment.author.name}]-{comment.message} {comment.amountString}")
            await chatdata.tick_async()

class YoutubeCommentReciever:
    def __init__(self, url=None, video_id=None):
        if url is None and video_id is None:
            print("urlかvideo_idのどちらかを指定してください")
            return False
        if video_id is not None:
            self.video_id = video_id
        if url is not None:
            self.url = url
            try:
                self.video_id = self.filteringVideoId(url)
            except Exception as e:
                print(e)
                if e == "URLが不正です":
                    return False
    def filteringVideoId(self,url:str):
        if "watch?v=" not in url:
            print("URLが不正です")
            raise Exception("URLが不正です")
        video_id = url.split("watch?v=")[1]
        if video_id == "":
            print("URLからvideo_idを取得できませんでした")
            raise Exception("URLからvideo_idを取得できませんでした")
        return video_id       

    async def fetch_comments(self,video_id):
        try:
            self.chat = pytchat.create(video_id=video_id, interruptable=False)
            while self.chat.is_alive():
                async for c in self.chat.get().async_items():
                    print(f"{c.datetime} [{c.author.name}]: {c.message}")
                    comment = {}
                    comment["datetime"] = c.datetime
                    comment["author"] = c.author.name
                    comment["message"] = c.message
                    yield comment
        except Exception as e:
            print(e)
    
    """
    停止用の関数
    """
    def stop(self):
        self.chat.terminate()
        print("chatを停止しました")
        




if __name__ == "__main__":
    # url = "https://www.youtube.com/watch?v=CF1vS8DdBIk"
    # url = "https://www.youtube.com/watch?v=x_fHq3B_UP4"
    # print("url:",url)
    # ycr = YoutubeCommentReciever(url = url)
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(ycr.main())
    # while True:
    #     # 1秒ごとに現在時刻を表示
    #     print(time.strftime("%Y/%m/%d %H:%M:%S"))
    #     time.sleep(1)
    
    # Replace 'YOUR_VIDEO_ID' with the actual video ID of the YouTube live stream
    video_id = 'FsJC17Vtqfk'

    # Run the async function
    async def main():
        ycr = YoutubeCommentReciever(video_id=video_id)
        async for comment in ycr.fetch_comments(video_id):
            print(comment)
        print("done")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
    