def count_entries(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()
            if not content:
                return 0
            entries = content.split(',')
            return len(entries)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except IOError:
        print(f"Error: There was an issue reading the file '{filename}'.")
        return None

# Example usage
filename = 'results.txt'  # Replace with your actual filename
count = count_entries(filename)

if count is not None:
    print(f"The number of comma-separated entries in '{filename}' is: {count}")