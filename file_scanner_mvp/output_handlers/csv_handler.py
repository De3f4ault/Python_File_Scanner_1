import csv

class CSVHandler:
    @staticmethod
    def write(data, output_path):
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["path", "content"])
            writer.writeheader()
            for item in data:
                writer.writerow({
                    "path": item["path"],
                    "content": item["content"]
                })
