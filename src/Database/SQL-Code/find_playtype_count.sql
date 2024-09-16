CREATE VIEW count_post AS
SELECT PrimaryPlayer, count(*) AS play_count
FROM plays
WHERE `PlayID` = 63
Group BY `PrimaryPlayer`
ORDER BY play_count DESC;