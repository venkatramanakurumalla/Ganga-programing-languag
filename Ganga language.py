import re
import math
import random

# Combined lexer and parser for efficiency
def parse_code(code):
    # Token patterns
    patterns = {
        'STRING': r'"[^"]*"',
        'NUMBER': r'\d+(\.\d+)?',
        'BOOLEAN': r'true|false',
        'IDENTIFIER': r'[a-zA-Z_]\w*',
        'OPERATOR': r'[=+\-*/%<>!&|]+|==|!=|<=|>=|and|or|not',
        'LPAREN': r'\(',
        'RPAREN': r'\)',
        'LBRACKET': r'\[',
        'RBRACKET': r'\]',
        'COMMA': r',',
        'SEMICOLON': r';',
        'SKIP': r'[ \t\n]+',
        'COMMENT': r'#.*',
    }
    
    # Keywords
    keywords = {
        'print', 'input', 'if', 'then', 'else', 'elif', 'end', 'repeat', 'times',
        'while', 'do', 'for', 'in', 'to', 'function', 'return', 'call', 'array',
        'try', 'catch', 'import', 'class', 'attributes', 'methods'
    }
    
    # Lexer - convert to tokens
    regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns.items())
    tokens = []
    
    for match in re.finditer(regex, code):
        kind = match.lastgroup
        value = match.group()
        
        if kind == 'SKIP' or kind == 'COMMENT':
            continue
        elif kind == 'IDENTIFIER' and value in keywords:
            tokens.append((value.upper(), value))
        else:
            tokens.append((kind, value))
    
    # Parse AST
    ast = []
    i = 0
    
    # Helper to get variable value
    def get_value(val, vars):
        if isinstance(val, (int, float, bool, list)):
            return val
        elif val in vars:
            return vars[val]
        elif val.replace('.', '', 1).isdigit():
            return float(val) if '.' in val else int(val)
        elif val.lower() in ('true', 'false'):
            return val.lower() == 'true'
        elif val.startswith('"') and val.endswith('"'):
            return val.strip('"')
        else:
            # Try evaluating as expression
            try:
                return eval_expr(val, vars)
            except:
                return val
    
    # Evaluate expressions with variables
    def eval_expr(expr, vars):
        # Replace variables with their values
        for name, val in vars.items():
            if not isinstance(val, list):
                pattern = r'\b' + re.escape(name) + r'\b'
                expr = re.sub(pattern, str(val).lower() if isinstance(val, bool) else str(val), expr)
        
        # Replace logical operators for Python evaluation
        expr = expr.replace('and', ' and ').replace('or', ' or ').replace('not', ' not ')
        
        try:
            return eval(expr)
        except:
            return expr
    
    # Parse statements
    while i < len(tokens):
        if i >= len(tokens):
            break
            
        token_type, token_value = tokens[i]
        
        # Print statement
        if token_type == 'PRINT':
            i += 1
            if i < len(tokens):
                expr = tokens[i][1]
                ast.append({"type": "Print", "value": expr})
                i += 1
        
        # Input statement
        elif token_type == 'INPUT':
            i += 1
            prompt = ""
            var_name = None
            
            # Get prompt if it's a string
            if i < len(tokens) and tokens[i][0] == 'STRING':
                prompt = tokens[i][1].strip('"')
                i += 1
            
            # Get variable name
            if i < len(tokens) and tokens[i][0] == 'IDENTIFIER':
                var_name = tokens[i][1]
                i += 1
                
            ast.append({"type": "Input", "prompt": prompt, "variable": var_name})
        
        # Variable assignment
        elif token_type == 'IDENTIFIER' and i + 1 < len(tokens) and tokens[i+1][1] == '=':
            name = token_value
            i += 2  # Skip =
            
            # Array assignment
            if i < len(tokens) and tokens[i][0] == 'ARRAY':
                i += 1
                if tokens[i][0] != 'LBRACKET':
                    raise SyntaxError("Expected '[' after 'array'")
                i += 1
                
                elements = []
                while i < len(tokens) and tokens[i][0] != 'RBRACKET':
                    elements.append(tokens[i][1])
                    i += 1
                    if i < len(tokens) and tokens[i][0] == 'COMMA':
                        i += 1
                        
                if i < len(tokens) and tokens[i][0] == 'RBRACKET':
                    i += 1
                    ast.append({"type": "AssignArray", "name": name, "elements": elements})
                else:
                    raise SyntaxError("Expected ']' to close array")
            else:
                # Regular assignment
                expr = tokens[i][1]
                i += 1
                ast.append({"type": "Assign", "name": name, "value": expr})
        
        # If statement
        elif token_type == 'IF':
            i += 1
            condition = tokens[i][1]
            i += 1
            
            # Find then
            while i < len(tokens) and tokens[i][0] != 'THEN':
                i += 1
            
            if i < len(tokens):
                i += 1  # Skip then
            
            # Parse if body
            if_body = []
            elif_clauses = []
            else_body = []
            current_body = if_body
            
            while i < len(tokens) and tokens[i][0] != 'END':
                if tokens[i][0] == 'ELSE':
                    i += 1
                    current_body = else_body
                    continue
                elif tokens[i][0] == 'ELIF':
                    i += 1
                    elif_cond = tokens[i][1]
                    i += 1
                    
                    # Find then
                    while i < len(tokens) and tokens[i][0] != 'THEN':
                        i += 1
                        
                    if i < len(tokens):
                        i += 1  # Skip then
                    
                    elif_body = []
                    elif_clauses.append({"condition": elif_cond, "body": elif_body})
                    current_body = elif_body
                    continue
                
                # Parse statement
                stmt_ast = parse_statement(tokens[i:])
                if stmt_ast:
                    current_body.append(stmt_ast)
                    i += 1
                else:
                    i += 1
            
            if i < len(tokens) and tokens[i][0] == 'END':
                i += 1
            
            ast.append({
                "type": "If",
                "condition": condition,
                "body": if_body,
                "elif_clauses": elif_clauses,
                "else_body": else_body
            })
        
        # While loop
        elif token_type == 'WHILE':
            i += 1
            condition = tokens[i][1]
            i += 1
            
            # Find do
            while i < len(tokens) and tokens[i][0] != 'DO':
                i += 1
            
            if i < len(tokens):
                i += 1  # Skip do
            
            # Parse while body
            body = []
            while i < len(tokens) and tokens[i][0] != 'END':
                stmt_ast = parse_statement(tokens[i:])
                if stmt_ast:
                    body.append(stmt_ast)
                i += 1
            
            if i < len(tokens) and tokens[i][0] == 'END':
                i += 1
            
            ast.append({
                "type": "While",
                "condition": condition,
                "body": body
            })
        
        # Repeat loop
        elif token_type == 'REPEAT':
            i += 1
            if i < len(tokens) and tokens[i][0] == 'NUMBER':
                count = int(float(tokens[i][1]))
                i += 1
                
                # Find times
                if i < len(tokens) and tokens[i][0] == 'TIMES':
                    i += 1
                
                # Parse repeat body
                body = []
                while i < len(tokens) and tokens[i][0] != 'END':
                    stmt_ast = parse_statement(tokens[i:])
                    if stmt_ast:
                        body.append(stmt_ast)
                    i += 1
                
                if i < len(tokens) and tokens[i][0] == 'END':
                    i += 1
                
                ast.append({
                    "type": "Repeat",
                    "count": count,
                    "body": body
                })
        
        # For loop
        elif token_type == 'FOR':
            i += 1
            if i < len(tokens) and tokens[i][0] == 'IDENTIFIER':
                var_name = tokens[i][1]
                i += 1
                
                # For-in loop (arrays)
                if i < len(tokens) and tokens[i][0] == 'IN':
                    i += 1
                    array_name = tokens[i][1]
                    i += 1
                    
                    # Parse body
                    body = []
                    while i < len(tokens) and tokens[i][0] != 'END':
                        stmt_ast = parse_statement(tokens[i:])
                        if stmt_ast:
                            body.append(stmt_ast)
                        i += 1
                    
                    if i < len(tokens) and tokens[i][0] == 'END':
                        i += 1
                    
                    ast.append({
                        "type": "ForEach",
                        "variable": var_name,
                        "array": array_name,
                        "body": body
                    })
                
                # For-to loop (ranges)
                elif i < len(tokens) and tokens[i][0] == 'TO':
                    i += 1
                    if i < len(tokens) and tokens[i][0] == 'NUMBER':
                        end_value = int(float(tokens[i][1]))
                        i += 1
                        
                        # Parse body
                        body = []
                        while i < len(tokens) and tokens[i][0] != 'END':
                            stmt_ast = parse_statement(tokens[i:])
                            if stmt_ast:
                                body.append(stmt_ast)
                            i += 1
                        
                        if i < len(tokens) and tokens[i][0] == 'END':
                            i += 1
                        
                        ast.append({
                            "type": "ForRange",
                            "variable": var_name,
                            "end": end_value,
                            "body": body
                        })
        
        # Function definition
        elif token_type == 'FUNCTION':
            i += 1
            if i < len(tokens) and tokens[i][0] == 'IDENTIFIER':
                func_name = tokens[i][1]
                i += 1
                
                # Parse parameters
                params = []
                if i < len(tokens) and tokens[i][0] == 'LPAREN':
                    i += 1
                    
                    while i < len(tokens) and tokens[i][0] != 'RPAREN':
                        if tokens[i][0] == 'IDENTIFIER':
                            params.append(tokens[i][1])
                            i += 1
                            
                            if i < len(tokens) and tokens[i][0] == 'COMMA':
                                i += 1
                        else:
                            i += 1
                    
                    i += 1  # Skip )
                
                # Parse function body
                body = []
                while i < len(tokens) and tokens[i][0] != 'END':
                    stmt_ast = parse_statement(tokens[i:])
                    if stmt_ast:
                        body.append(stmt_ast)
                    i += 1
                
                if i < len(tokens) and tokens[i][0] == 'END':
                    i += 1
                
                ast.append({
                    "type": "Function",
                    "name": func_name,
                    "params": params,
                    "body": body
                })
        
        # Function call
        elif token_type == 'CALL':
            i += 1
            if i < len(tokens) and tokens[i][0] == 'IDENTIFIER':
                func_name = tokens[i][1]
                i += 1
                
                # Parse arguments
                args = []
                if i < len(tokens) and tokens[i][0] == 'LPAREN':
                    i += 1
                    
                    while i < len(tokens) and tokens[i][0] != 'RPAREN':
                        if tokens[i][0] in ('NUMBER', 'STRING', 'IDENTIFIER', 'BOOLEAN'):
                            args.append(tokens[i][1])
                            i += 1
                            
                            if i < len(tokens) and tokens[i][0] == 'COMMA':
                                i += 1
                        else:
                            i += 1
                    
                    i += 1  # Skip )
                
                ast.append({
                    "type": "Call",
                    "function": func_name,
                    "arguments": args
                })
        
        # Return statement
        elif token_type == 'RETURN':
            i += 1
            value = None
            if i < len(tokens) and tokens[i][0] in ('NUMBER', 'STRING', 'IDENTIFIER', 'BOOLEAN'):
                value = tokens[i][1]
                i += 1
            
            ast.append({"type": "Return", "value": value})
        
        else:
            i += 1
    
    return ast

# Helper to parse a single statement
def parse_statement(tokens):
    if not tokens:
        return None
    
    token_type, token_value = tokens[0]
    
    if token_type in ('PRINT', 'INPUT', 'IF', 'WHILE', 'REPEAT', 'FOR', 'FUNCTION', 'CALL', 'RETURN'):
        if token_type == 'PRINT':
            if len(tokens) > 1:
                return {"type": "Print", "value": tokens[1][1]}
        elif token_type == 'INPUT':
            prompt = ""
            var_name = None
            
            if len(tokens) > 1 and tokens[1][0] == 'STRING':
                prompt = tokens[1][1].strip('"')
                if len(tokens) > 2 and tokens[2][0] == 'IDENTIFIER':
                    var_name = tokens[2][1]
            elif len(tokens) > 1 and tokens[1][0] == 'IDENTIFIER':
                var_name = tokens[1][1]
                
            return {"type": "Input", "prompt": prompt, "variable": var_name}
        elif token_type == 'RETURN':
            value = None
            if len(tokens) > 1 and tokens[1][0] in ('NUMBER', 'STRING', 'IDENTIFIER', 'BOOLEAN'):
                value = tokens[1][1]
            return {"ok"
            "nbbtype": "Return", "value": value}
    
    return None

# Interpreter: Execute the AST
def interpret(ast, variables=None, functions=None):
    if variables is None:
        variables = {}
    
    if functions is None:
        functions = {
            'print': lambda args: print(*args),
            'len': lambda args: len(args[0]) if args else 0,
            'random': lambda args: random.random(),
            'floor': lambda args: math.floor(float(args[0])) if args else 0,
            'ceil': lambda args: math.ceil(float(args[0])) if args else 0,
            'sin': lambda args: math.sin(float(args[0])) if args else 0,
            'cos': lambda args: math.cos(float(args[0])) if args else 0,
        }
    
    i = 0
    while i < len(ast):
        node = ast[i]
        
        # Process return statements
        if node["type"] == "Return":
            if node["value"] is None:
                return None
            
            value = node["value"]
            return get_value(value, variables)
        
        # Print statements
        elif node["type"] == "Print":
            value = node["value"]
            print(get_value(value, variables))
        
        # Input statements
        elif node["type"] == "Input":
            prompt = node["prompt"]
            var_name = node["variable"]
            
            if prompt:
                user_input = input(prompt)
            else:
                user_input = input()
            
            if var_name:
                # Convert input to appropriate type
                if user_input.isdigit():
                    variables[var_name] = int(user_input)
                elif user_input.replace('.', '', 1).isdigit() and user_input.count('.') == 1:
                    variables[var_name] = float(user_input)
                elif user_input.lower() in ('true', 'false'):
                    variables[var_name] = user_input.lower() == 'true'
                else:
                    variables[var_name] = user_input
        
        # Variable assignment
        elif node["type"] == "Assign":
            name = node["name"]
            value = node["value"]
            variables[name] = get_value(value, variables)
        
        # Array assignment
        elif node["type"] == "AssignArray":
            name = node["name"]
            elements = [get_value(elem, variables) for elem in node["elements"]]
            variables[name] = elements
        
        # If statements
        elif node["type"] == "If":
            condition = eval_expr(node["condition"], variables)
            
            if condition:
                result = interpret(node["body"], variables, functions)
                if result is not None:
                    return result
            else:
                # Check elif clauses
                elif_executed = False
                for elif_clause in node["elif_clauses"]:
                    elif_condition = eval_expr(elif_clause["condition"], variables)
                    if elif_condition:
                        result = interpret(elif_clause["body"], variables, functions)
                        if result is not None:
                            return result
                        elif_executed = True
                        break
                
                # Execute else if no if/elif was executed
                if not elif_executed and node["else_body"]:
                    result = interpret(node["else_body"], variables, functions)
                    if result is not None:
                        return result
        
        # Repeat loops
        elif node["type"] == "Repeat":
            for _ in range(node["count"]):
                result = interpret(node["body"], variables, functions)
                if result is not None:
                    return result
        
        # While loops
        elif node["type"] == "While":
            while eval_expr(node["condition"], variables):
                result = interpret(node["body"], variables, functions)
                if result is not None:
                    return result
        
        # For-each loops
        elif node["type"] == "ForEach":
            var_name = node["variable"]
            array_name = node["array"]
            
            if array_name in variables and isinstance(variables[array_name], list):
                for element in variables[array_name]:
                    variables[var_name] = element
                    result = interpret(node["body"], variables, functions)
                    if result is not None:
                        return result
        
        # For-range loops
        elif node["type"] == "ForRange":
            var_name = node["variable"]
            end = node["end"]
            
            for value in range(end):
                variables[var_name] = value
                result = interpret(node["body"], variables, functions)
                if result is not None:
                    return result
        
        # Function definitions
        elif node["type"] == "Function":
            functions[node["name"]] = {
                "params": node["params"],
                "body": node["body"]
            }
        
        # Function calls
        elif node["type"] == "Call":
            func_name = node["function"]
            args = [get_value(arg, variables) for arg in node["arguments"]]
            
            if func_name in functions:
                func = functions[func_name]
                
                if callable(func):
                    # Built-in function
                    result = func(args)
                    if result is not None:
                        return result
                else:
                    # User-defined function
                    local_vars = variables.copy()
                    
                    # Bind parameters to arguments
                    for i, param in enumerate(func["params"]):
                        if i < len(args):
                            local_vars[param] = args[i]
                        else:
                            local_vars[param] = None
                    
                    # Execute function body
                    result = interpret(func["body"], local_vars, functions)
                    if result is not None:
                        return result
            else:
                print(f"Error: Function '{func_name}' not defined")
        
        i += 1

# Helper to get variable value
def get_value(val, vars):
    if isinstance(val, (int, float, bool, list)):
        return val
    elif val in vars:
        return vars[val]
    elif val.replace('.', '', 1).isdigit():
        return float(val) if '.' in val else int(val)
    elif val.lower() in ('true', 'false'):
        return val.lower() == 'true'
    elif val.startswith('"') and val.endswith('"'):
        return val.strip('"')
    else:
        # Try evaluating as expression
        try:
            return eval_expr(val, vars)
        except:
            return val

# Evaluate expressions with variables
def eval_expr(expr, vars):
    # Replace variables with their values
    for name, val in vars.items():
        if not isinstance(val, list):
            pattern = r'\b' + re.escape(name) + r'\b'
            expr = re.sub(pattern, str(val).lower() if isinstance(val, bool) else str(val), expr)
    
    # Replace logical operators for Python evaluation
    expr = expr.replace('and', ' and ').replace('or', ' or ').replace('not', ' not ')
    
    try:
        return eval(expr)
    except:
        return expr

# Main function
def run_program(code):
    try:
        ast = parse_code(code)
        interpret(ast)
    except Exception as e:
        print(f"Error: {e}")

# Example usage
if __name__ == "__main__":
    code = '''
    # Example program in our language
    
    # Variables and printing
    print "Welcome to my program!"
    x = 10
    y = 5
    result = x + y
    print result
    
    # Input
    input "Enter your name: " name
    print "Hello,"
    print name
    
    # Arrays
    numbers = array [1, 2, 3, 4, 5]
    
    # For-each loop
    print "Numbers in array:"
    for num in numbers
        print num
    end
    
    # Functions
    function add(a, b)
        return a + b
    end
    
    sum = call add(x, y)
    print "Sum is:"
    print sum
    
    # Conditionals
    if x > y then
        print "x is greater than y"
    elif x == y then
        print "x equals y"
    else
        print "x is less than y"
    end
    
    # While loop
    counter = 0
    while counter < 3 do
        print "Counter:"
        print counter
        counter = counter + 1
    end
    
    # Range loop
    print "Counting to 5:"
    for i to 5
        print i
    end
    
    print "Program completed!"
    try
    x = 10 / 0
catch error
    print "An error occurred: " error
end
# Write to a file
write_file "output.txt" "Hello, World!"

# Read from a file
content = read_file "output.txt"
print content
    '''
    
    run_program(code)
