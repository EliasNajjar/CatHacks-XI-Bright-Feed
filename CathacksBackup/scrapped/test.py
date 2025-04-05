import sys
import os
import time

# Retrieve command-line arguments
arguments = sys.argv
current_pid = os.getpid()



# Check for sufficient arguments
if len(arguments) > 2:
    arg1 = arguments[1]  # Fixed typo
    arg2 = arguments[2]  # Fixed typo

    print(arg1)
    print(arg2)

    # Writing to the file
    with open(f"response-{current_pid}", "w") as file:
        file.write("Hello, world!\n")
        file.write("SubReddit Name: " + arg1 + "\n")
        file.write("Check For: " + arg2 + "\n")
        file.write(f"ID: {current_pid}" + "\n")
else:
    print("Insufficient arguments provided. Please pass two arguments.")
    sys.exit(1)  # Explicitly exit with code 1 when there are insufficient arguments