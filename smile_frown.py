def on_data_received():
    global buffer
    buffer = serial.read_until(serial.delimiters(Delimiters.NEW_LINE)).trim()
    if buffer == "smile":
        basic.show_icon(IconNames.HAPPY)
        serial.write_string("Received: smile - showing happy icon\n")
    elif buffer == "frown":
        basic.show_icon(IconNames.SAD)
        serial.write_string("Received: frown - showing sad icon\n")
    elif buffer == "straight":
        basic.show_icon(IconNames.ASLEEP)
        serial.write_string("Received: straight - showing asleep icon\n")
    else:
        basic.clear_screen()
        serial.write_string("Received: " + buffer + " - clearing screen\n")
serial.on_data_received(serial.delimiters(Delimiters.NEW_LINE), on_data_received)

buffer = ""