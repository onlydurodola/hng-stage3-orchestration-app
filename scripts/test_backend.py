import asyncio
import websockets
import json
import time

async def send_test_code():
    uri = "ws://localhost:8000/ws/code"
    headers = {
        "X-API-Key": "ceab673e2b6794dd31be3dcf12f1db9d6f6cfe75c2c5f302747f4d94516020db"
    }
    namespace = "user-test"
    user_id = "test"

    bad_code = '''print("This is broken code"'''
    good_code = '''print("Hello, this is working code")'''

    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Send bad code
        payload = {"user_id": user_id, "code": bad_code}
        await websocket.send(json.dumps(payload))
        response = await websocket.recv()
        print(f"Bad code response: {response}")

        # Wait and check result
        await asyncio.sleep(5)
        try:
            response_json = json.loads(response)
            if response_json.get("status") == "tests_failed":
                # Send good code to same pod
                payload = {"user_id": user_id, "code": good_code}
                await websocket.send(json.dumps(payload))
                response = await websocket.recv()
                print(f"Good code response: {response}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse response: {response}, error: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_code())

# What will be the output of running the test code snippet above?
#  Bad code response: Error: Deployment failed: Pod user-test-test not ready after timeout
#  Good code response: {"status": "deployed", "namespace": "user-test"}