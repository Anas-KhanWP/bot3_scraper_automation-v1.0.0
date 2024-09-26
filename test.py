import requests

# The URL of the PDF file
url = 'https://www.browardclerk.org/Web2/WebForms/Document.aspx?Viewer=OWJ6eWtXUGtTNjNySlMyRWhDU3UyY2M4RnhIaUhCeHUzandIdHFyQjBwMk9BMXE4cndHci9lK1d6NEpwOSsyNVk5MlF2MUtjbVhKVUx5LzNFT2hyUUpXZzIvbDdRa3MzNTVzU291a21McjdmcDZCMEFoaFd3b21TME1yV1d2aEJOa0NmMWd4eEFFeG5rcWVjS25hZlNJZklVSUUyT0tvUG1GMFQ0TXY1MnFNVy8zRGZVSlVGV1loeTFjRFgraFJHUFRQaG1wWG8yS3pvRzBIVktHYjBab0JSL2NVZ0hXQjVpR1lVaTFqZWdEVXhRUWljY0VyR3dZaG1GSXRZM29BMS9wS1BRSTBtOUc5OFlYN3RQclJSU2djaFJkV1djVDY3Z2tKNkxMZG51T2s5QXlsNk03eUg4azZDNEZ4NDlSN3psVlBOdGgwQzVqYnI3VzM3OW9KYnU4S0xNWGdzK2VCSw%3d%3d-OmMoniXuD9g%3d'

# Make the request and download the content
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Save the PDF file
    with open("downloaded_file.pdf", 'wb') as file:
        file.write(response.content)
    print("PDF downloaded successfully!")
else:
    print(f"Failed to download the PDF. Status code: {response.status_code}")
