
import sys
import os
import io

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from run_reading import run_reading

# Capture stdout
old_stdout = sys.stdout
sys.stdout = buffer = io.StringIO()

try:
    run_reading('1965-07-26', '20:18', 'Oakland', 'CA')
finally:
    sys.stdout = old_stdout

output = buffer.getvalue()

# Write to file
with open('output_reading_july_1965_clean.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print("Reading complete. Output saved to output_reading_july_1965_clean.txt")
