INSERT INTO sources (id, name, destination) VALUES
(0, 'HManga', 'D:/Parsing/HManga/'),
(1, 'Manga', 'D:/Parsing/Manga/')
ON CONFLICT (id) DO NOTHING;

INSERT INTO domains (id, address, source_id) VALUES
(0, 'xxl.hentaichan.live', 0),
(1, 'y.hentaichan.live', 0),
(2, 'x4.h-chan.me', 0),
(3, 'im.manga-chan.me', 1)
ON CONFLICT (id) DO NOTHING;