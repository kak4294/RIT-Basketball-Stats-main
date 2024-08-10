CREATE VIEW playtype_count AS
SELECT PrimaryPlayer, count(*) AS play_count
FROM plays
WHERE `PlayID` = ?
Group BY `PrimaryPlayer`
ORDER BY play_count DESC;