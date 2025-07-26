# from contextlib import asynccontextmanager

# with open("data.txt", "r") as file:
#     data = file.read()
#     print(data)
    
# with open("data.txt", "r+") as file, open("out.txt", "w") as outfile:
#     data = file.read()
#     outfile.write(data.upper())
#     print(data, "Data written to out.txt")
    
    
# @asynccontextmanager    
# async def make_connection(name):
#     print(f"Connecting... {name}")
#     yield name
#     print(f"Connected! {name}")
    
# async def main():
#     async with make_connection("A") as a:
#         print(f"Using connection: {a}")
        
# asyncio.run(main())

import asyncio
from contextlib import AsyncExitStack

async def get_connection(name):
    class Ctx():
        async def __aenter__(self):
            print(f"ENTER... {name}")
            return name
        async def __aexit__(self, exc_type, exc, tb):
            print(f"EXIT! {name}")
    return Ctx()

# async def main():
#     async with await get_connection("A") as a:
#         async with await get_connection("B") as b:
#             print(f"Using connections: {a} and {b}")
            
async def main():
    async with AsyncExitStack() as stack:
        a = await stack.enter_async_context(await get_connection("A"))
        if a == "A":
            b = await stack.enter_async_context(await get_connection("B"))
            print(f"Using connections: {a} and {b}")    

        async def customCleanup():
            print("Custom cleanup logic here")

        stack.push_async_callback(customCleanup)
        print(f"Doing work with {a} and maybe {locals().get('b')}")
        await asyncio.sleep(1)

asyncio.run(main())