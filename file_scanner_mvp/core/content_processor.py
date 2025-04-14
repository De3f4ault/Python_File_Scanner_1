class ContentProcessor:
    def process(self, data):
        """Format data for output handlers"""
        return [{"path": item["path"], "content": item["content"]} for item in data]
