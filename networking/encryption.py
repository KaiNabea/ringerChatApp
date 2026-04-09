# this file is responsible for encrypting and decrypting messages that are sent over the network

# converts text to binary
def text_to_binary(text):

# takes string as input and returns a string of 0s and 1s representing the binary value of the text
    return ' '.join(format(ord(c),'08b') for c in text)

# this makes binary to text
def binary_to_text(binary):
# takes the binrary string as input and returns the original text
    chars = binary.split()
# this loops through the binary string and converts each 8 bits to a character and joins them together to form the original text
    return ''.join(chr(int(b,2)) for b in chars)

# test execution
msg = "Hello"

b = text_to_binary(msg)

print(b)

print(binary_to_text(b))