import sys
import re

# Load the variable mappings
variable_mappings = {}
with open('variables.txt', 'r') as f:
    for line in f:
        original, replacement = line.strip().split('=')
        variable_mappings[original] = replacement

def replace_bank_accounts(blob):
    # Decode blob data to utf-8 string
    data = blob.data.decode('utf-8')
    
    # Iterate through the variable mappings to replace bank account numbers
    for original, replacement in variable_mappings.items():
        # Create a regex pattern to match bank account numbers both standalone and within strings
        pattern = rf'(["\']?)({re.escape(original)})(["\']?)'
        
        # Function to replace bank account number ensuring quotes consistency
        def replace_match(match):
            quote_start, bank_number, quote_end = match.groups()
            # Preserve quotes if they exist, otherwise replace with variable name
            if quote_start and quote_end and quote_start == quote_end:
                return f'{quote_start}{{{replacement}}}{quote_end}'
            else:
                return replacement

        # Apply the substitution with the custom function
        data = re.sub(pattern, replace_match, data)
    
    # Encode modified data back to bytes
    blob.data = data.encode('utf-8')

if __name__ == '__main__':
    from git_filter_repo import FilterRepo
    repo = FilterRepo(sys.argv[1])
    repo.add_blob_callback(replace_bank_accounts)
    repo.run()
