import json

class JSONHandler:
    @staticmethod
    def write(data, output_path):
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
