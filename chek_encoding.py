import chardet

with open("bot_logs.txt", "rb") as f:
    raw_data = f.read()
    result = chardet.detect(raw_data)
    print(result)
