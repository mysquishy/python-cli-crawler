#!/usr/bin/env python3
"""
Integration test for the plugin functionality in the crawler.
This test creates a temporary HTML file containing heading tags (h1, h2, h3)
and then invokes the crawler with the --use-plugins flag to verify that
the HeadingExtractor plugin processes the page and outputs the extracted headings.
"""

import os
import sys
import tempfile
import subprocess

def write_test_html(file_path):
    html_content = """
    <html>
      <head>
        <title>Test Page</title>
      </head>
      <body>
        <h1>This is a Heading 1</h1>
        <h2>This is a Heading 2</h2>
        <h3>This is a Heading 3</h3>
      </body>
    </html>
    """
    with open(file_path, "w") as f:
        f.write(html_content)

def run_integration_test():
    with tempfile.TemporaryDirectory() as tmpdirname:
        html_file = os.path.join(tmpdirname, "test_plugin.html")
        write_test_html(html_file)
        # Construct a file URL for the temporary HTML file
        abs_path = os.path.abspath(html_file)
        file_url = "file://" + abs_path
        print("Testing plugin integration on:", file_url)
        # Run the crawler with the --use-plugins flag to trigger plugin processing.
        cmd = [
            "python", "main.py", "crawl",
            "--name", "TestPlugin",
            "--url", file_url,
            "--use-plugins"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        print("Crawler output:")
        print(output)
        # Check if the output from HeadingExtractor is present.
        if "Plugin HeadingExtractor output:" in output:
            print("Integration test passed: HeadingExtractor plugin output detected.")
            sys.exit(0)
        else:
            print("Integration test failed: HeadingExtractor plugin output not found.")
            sys.exit(1)

if __name__ == "__main__":
    run_integration_test()
