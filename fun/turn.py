def get_turn_markers(message):
    with open("markers_long.txt") as file:
        markers_long = [i.strip("\n") for i in file]
    with open("markers_short.txt") as file:
        markers_short = [i.strip("\n") for i in file]

    words = [i.lower() for i in message.split()]
    for marker in markers_long:
        if marker in words:
            return f"{marker} ↑"
    for marker in markers_short:
        if marker in words:
            return f"{marker} ↓"
    return None
