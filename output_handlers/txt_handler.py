class TXTHandler:
    @staticmethod
    def write(data, output_path):
        with open(output_path, "w") as f:
            for item in data:
                f.write(f"Path: {item['path']}\n")
                f.write(f"Content:\n{item['content']}\n{'='*40}\n")
