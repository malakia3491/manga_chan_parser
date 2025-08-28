import datetime

class HtmlPage:
    def __init__(self, url, content, encoding='utf-8', content_length=None, created_at=None):
        self.url = url
        self.content = content 
        self.encoding = encoding
        self.content_length = content_length or len(content)
        self.created_at = created_at or datetime.datetime.now()
        
    def to_dict(self):
        return {
            'url': self.url,
            'content': self.content.hex(),
            'encoding': self.encoding,
            'content_length': self.content_length,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            url=data['url'],
            content=bytes.fromhex(data['content']),
            encoding=data.get('encoding', 'utf-8'),
            content_length=data['content_length'],
            created_at=datetime.datetime.fromisoformat(data['created_at'])
        )