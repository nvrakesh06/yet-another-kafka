from yak.producer import Producer

p = Producer()

for i in range(1, 6):
    ack = p.send("first_topic", f"hello world {i}")
    if ack == 1:
        print("sent successfully")
    else:
        print("msg not sent successfully")
