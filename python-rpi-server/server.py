import asyncio
from bleak import BleakClient
from fastapi import FastAPI
from typing import Optional
import uvicorn

# BLE Configuration
ADDRESS = "xx:xx:xx:xx:xx:xx" # Fireplace Address
CHARACTERISTIC = "0000ffe1-0000-1000-8000-00805f9b34fb"

# BLE Commands
TURN_ON = bytes.fromhex("0d0100010000000000000000000000000000000d")
TURN_OFF = bytes.fromhex("0d0100020000000000000000000000000000000e")
FLAME_COMMAND = "0d2000"
FLAME_PADDING = "00000000000000000000000000002c"

flame_height = 7
flame_speed = 7
is_on = False

# Create FastAPI app
app = FastAPI()

# Global client reference
ble_client = None

async def connect_ble():
    """ Continuously tries to connect to the BLE device and keeps the connection alive. """
    global ble_client
    global flame_height
    global flame_speed
    global is_on
    while True:
        try:
            print("Trying to connect to BLE device...")
            ble_client = BleakClient(ADDRESS)
            await ble_client.connect()

            if ble_client.is_connected:
                print(f"✅ Connected to {ADDRESS}")
                return  # Exit loop once connected
        except Exception as e:
            print(f"⚠️ Connection failed: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)

async def ensure_connection():
    """ Ensures the BLE connection is alive and reconnects if necessary. """
    global ble_client
    if ble_client is None or not ble_client.is_connected:
        await connect_ble()

@app.get("/")
async def hello():
    return {"status": "Running"}

@app.get("/control/{action}")
@app.get("/control/{action}/{n}")
async def control(action: str, n: Optional[int] = None):
    """ Handles on/off commands via HTTP. """
    global ble_client
    global flame_height
    global flame_speed
    await ensure_connection()  # Ensure the connection is alive

    if isinstance(n, int) and (n >= 1 and n <= 7):
      if action == "flame_height":
        flame_height = n
        print("set height")
      if action == "flame_speed":
        flame_speed = n
        print("set speed")

    flame_cmd = FLAME_COMMAND + "0" + str(flame_height) + "0" + str(flame_speed) + FLAME_PADDING
    print("FLAME_HEIGHT: " + str(flame_height) + " // FLAME_SPEED: " + str(flame_speed))

    try:
        if action == "on":
            await ble_client.write_gatt_char(CHARACTERISTIC, TURN_ON)
            is_on = True
            return {"status": "Turned ON"}
        elif action == "off":
            is_on = False
            await ble_client.write_gatt_char(CHARACTERISTIC, TURN_OFF)
            return {"status": "Turned OFF"}
        elif action == "flame_height" or action == "flame_speed":
            print("Setting height and speed = " + flame_cmd)
            await ble_client.write_gatt_char(CHARACTERISTIC, bytes.fromhex(flame_cmd))
            return {"status": "Turned OFF"}
        else:
            await ble_client.write_gatt_char(CHARACTERISTIC, bytes.fromhex(action))
            return {"status": "Ran " + action}
    except Exception as e:
        return {"error": f"Failed to send command: {e}"}

async def main():
    """ Main event loop to maintain BLE connection and run the server. """
    await connect_ble()  # Start by connecting to BLE

    # Start FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())