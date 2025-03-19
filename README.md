# Ganga Language Interpreter

This repository contains an interpreter for the custom programming language "Ganga." Ganga is a simple, interpreted language that supports basic data types, control flow structures, functions, arrays, and file I/O.

## Features

* **Data Types:** Numbers (integers and floats), strings, booleans, arrays.
* **Variables:** Dynamic typing.
* **Operators:** Arithmetic, comparison, logical, assignment.
* **Control Flow:** `if`, `while`, `repeat`, `for` (each and range), `try`/`catch`.
* **Functions:** User-defined functions with parameters and return values.
* **Arrays:** Ordered collections of elements.
* **Built-in Functions:** `print`, `input`, `len`, `random`, `floor`, `ceil`, `sin`, `cos`, `write_file`, `read_file`.
* **Error Handling:** Basic error reporting and `try`/`catch` blocks.

## Getting Started

### Prerequisites

* Python 3.x

### Running the Interpreter

1.  **Clone the Repository:**

    ```bash
    git clone [repository URL]
    cd [repository directory]
    ```

2.  **Create a Ganga Program:**

    Create a text file (e.g., `my_program.txt`) with your Ganga code.

3.  **Run the Interpreter:**

    ```bash
    python interpreter.py < my_program.txt
    ```

    (Assuming your python file with the interpreter code is named `interpreter.py`)

### Example Ganga Code

```ganga
# Example Ganga program
print "Welcome to Ganga!"

x = 10
y = 5
result = x + y

print "Result:"
print result

input "Enter your name: " name
print "Hello, "
print name

numbers = array [1, 2, 3]
for num in numbers
    print num
end

function add(a, b)
    return a + b
end

sum = call add(x, y)
print "Sum:"
print sum

try
    z = 10 / 0
catch error
    print "Error: Division by zero"
end

write_file "output.txt" "This is a test"
file_content = read_file "output.txt"
print file_content
