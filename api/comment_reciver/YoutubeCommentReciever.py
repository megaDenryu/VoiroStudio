import pytchat
from pytchat import LiveChatAsync
import asyncio
from pprint import pprint


class YoutubeCommentReciever:
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
    """
    以下は非同期処理
    """
    

    async def main(self):
        livechat = LiveChatAsync("uIx8l2xlYVY", callback = self.func)
        while livechat.is_alive():
            await asyncio.sleep(3)
            #other background operation.

        # If you want to check the reason for the termination, 
        # you can use `raise_for_status()` function.
        try:
            livechat.raise_for_status()
        except pytchat.ChatDataFinished:
            print("Chat data finished.")
        except Exception as e:
            print(type(e), str(e))

    #callback function is automatically called periodically.
    async def func(self,chatdata):
        for comment in chatdata.items:
            print(f"{comment.datetime} [{comment.author.name}]-{comment.message} {comment.amountString}")
            await chatdata.tick_async()
            yield comment

    """
    以下は同期処理
    """
    def filteringVideoId(self,url:str):
        if "watch?v=" not in url:
            print("URLが不正です")
            raise Exception("URLが不正です")
        video_id = url.split("watch?v=")[1]
        if video_id == "":
            print("URLからvideo_idを取得できませんでした")
            raise Exception("URLからvideo_idを取得できませんでした")
        return video_id

    async def getComments(self):
        while self.chat.is_alive():
            async for c in self.chat.get().sync_items():
                comment = {}
                comment["datetime"] = c.datetime
                comment["author"] = c.author.name
                comment["message"] = c.message
                pprint(comment)
                yield comment



if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=CF1vS8DdBIk"
    ycr = YoutubeCommentReciever(url)
    # async for comment in ycr.getComments():
    #     print(comment)