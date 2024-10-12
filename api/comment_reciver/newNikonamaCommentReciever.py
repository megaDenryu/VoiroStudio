import asyncio
from typing import AsyncGenerator
from ndgr_client.constants import NDGRComment
from ndgr_client.ndgr_client import NDGRClient

class newNikonamaCommentReciever:

    def __init__(self, nicolive_program_id: str, end_keyword=""):
        self.nicolive_program_id = nicolive_program_id
        self.end_keyword = end_keyword
        self.recieve_status = "recieve"
    async def streamComments(self)->AsyncGenerator[NDGRComment, None]:

        # NDGRClient を初期化
        await NDGRClient.updateJikkyoChannelIDMap()
        ndgr_client = NDGRClient(self.nicolive_program_id, show_log=False)

        # コメントをエンドレスでストリーミング開始
        async for comment in ndgr_client.streamComments():
            if self.recieve_status == "end":
                break
            yield comment
        print("コメント受信を終了します")

    def checkAndStopRecieve(self,sentence):
        if self.end_keyword != "" and self.end_keyword in sentence:
            self.stopRecieve()
    
    def stopRecieve(self):
        self.recieve_status = "end"

if __name__ == '__main__':
    # asyncio.run(stream('lv345521261'))
    ncr = newNikonamaCommentReciever('lv345521261')
    async def main():
        async for comment in ncr.streamComments():
            print(comment)
    asyncio.run(main())