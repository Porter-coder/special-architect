def fibonacci_sequence(n):
    """Generate the first n Fibonacci numbers."""
    fibonacci = [0, 1]

    for i in range(2, n):
        next_num = fibonacci[-1] + fibonacci[-2]
        fibonacci.append(next_num)

    return fibonacci

# Generate and print the first 10 Fibonacci numbers
first_10 = fibonacci_sequence(10)
print("The first 10 Fibonacci numbers are:")
print(first_10)
