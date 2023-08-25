import threading
import socketio
import asyncio

# Input shop ID
shop_id = input("Enter shop ID: ")
conversation_id = None
sio = socketio.Client()
ai_response = []


def write_to_file(filename, content):
    """Synchronously write content to a file."""
    with open(filename, 'a') as f:
        f.write(content)


@sio.on('ai_response', namespace='/customer')
def on_ai_response(data):
    global ai_response
    ai_response.append(data)


@sio.on('init_response', namespace='/customer')
def on_init_response(data):
    global conversation_id
    conversation_id = data
    print(f"Initialized conversation with ID: {conversation_id}")


def input_thread():
    while True:
        # Send message
        message = input("")
        print("----------------------------------")
        write_to_file(f"{conversation_id}.txt", f"\nUSER: {message} \nAI: ")
        if message.lower() == "exit":
            print("Exiting...")
            sio.disconnect()
            break

        message_payload = {
            "message": message,
            "conversation_id": conversation_id
        }
        sio.emit("message", message_payload, namespace="/customer")


def output_thread():
    while True:
        # Send message
        if ai_response:
            output = ai_response.pop(0)
            write_to_file(f"{conversation_id}.txt", f"{output}")


@sio.event(namespace='/customer')
def connect():
    print("Connected to server.")

    # Send init message
    init_payload = {
        "shop_id": shop_id,
        "conversation_id": None
    }
    sio.emit('init', init_payload, namespace='/customer')

    t = threading.Thread(target=input_thread)
    t.start()
    t = threading.Thread(target=output_thread)
    t.start()


if __name__ == '__main__':
    print()
    sio.connect('http://localhost:8003/customer')  # Modify with your server URL
    sio.wait()
