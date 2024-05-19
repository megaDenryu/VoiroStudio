import asyncio

async def wait_with_sleep():
    print('wait_with_sleep: 開始')
    await asyncio.sleep(3)
    print('wait_with_sleep: 3秒後')

async def run_without_waiting():
    print('run_without_waiting: すぐに実行')

async def main():
    # 両方のタスクを同時にスケジュールする
    task1 = asyncio.create_task(wait_with_sleep())
    task2 = asyncio.create_task(run_without_waiting())

    # 両方のタスクが完了するのを待つ
    await task2
    
    await task1
async def main2():
    t = wait_with_sleep()
    await run_without_waiting()

# イベントループを実行
asyncio.run(main2())
