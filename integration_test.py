#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile

def write_dynamic_html(file_path):
    html_content = """
    <html>
      <head>
        <title>Initial Title</title>
        <script type="text/javascript">
          // Change the title after 1 second to simulate dynamic content
          setTimeout(function(){
            document.title = "Dynamic Title";
          }, 1000);
        </script>
      </head>
      <body>
        <h1>Dynamic Content Test</h1>
        <p>This page simulates dynamic content rendering.</p>
      </body>
    </html>
    """
    with open(file_path, "w") as f:
        f.write(html_content)

def run_integration_test():
    # Create a temporary directory for the dynamic HTML file
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = os.path.join(tmpdirname, "dynamic_test.html")
        write_dynamic_html(file_path)
        # Construct the file URL
        abs_path = os.path.abspath(file_path)
        file_url = "file://" + abs_path
        print("Testing dynamic rendering on:", file_url)
        # Run the crawler with the --render flag
        cmd = [
            "crawler-cli", "crawl",
            "--name", "IntegrationTest",
            "--url", file_url,
            "--render",
            "--depth", "1"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        print("Crawler output:")
        print(output)
        # Check if dynamic title has been extracted
        if "Dynamic Title" in output:
            print("Integration test passed: 'Dynamic Title' found.")
            sys.exit(0)
        else:
            print("Integration test failed: 'Dynamic Title' not found in output.")
            sys.exit(1)

if __name__ == "__main__":
    run_integration_test()
