-- CREATE VIEW PlayerEffciency AS 
SELECT 
    Player,
	Team,
    SUM(TotalPlays) AS TotalPlays,
    SUM(Total3ptShots) AS Total3ptShots,
    SUM(Total3ptMakes) AS Total3ptMakes,
    (SUM(Total3ptMakes) / NULLIF(SUM(Total3ptShots), 0)) * 100 AS "3pt%",
    SUM(Total2ptShots) AS Total2ptShots,
    SUM(Total2ptMakes) AS Total2ptMakes,
    (SUM(Total2ptMakes) / NULLIF(SUM(Total2ptShots), 0)) * 100 AS "2pt%",
    SUM(TotalMidRangeShots) AS TotalMidRangeShots,
    SUM(TotalMidRangeMakes) AS TotalMidRangeMakes,
    (SUM(TotalMidRangeMakes) / NULLIF(SUM(TotalMidRangeShots), 0)) * 100 AS "MidRange%",
    (
        (SUM(Total2ptMakes) + (1.5 * SUM(Total3ptMakes))) / 
        NULLIF((SUM(Total2ptShots) + SUM(Total3ptShots)), 0)
    ) * 100 AS "EFG%"
FROM (
    SELECT 
        PrimaryPlayer AS Player,
        OffensivePossession AS Team,
        COUNT(0) AS TotalPlays,
        SUM(CASE WHEN Outcome IN ('3pmi', '3pma') THEN 1 ELSE 0 END) AS Total3ptShots,
        SUM(CASE WHEN Outcome = '3pMa' THEN 1 ELSE 0 END) AS Total3ptMakes,
        SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
        SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes,
        SUM(CASE WHEN ShotLevel IN (2, 3) THEN 1 ELSE 0 END) AS TotalMidRangeShots,
        SUM(CASE WHEN (ShotLevel IN (2, 3) AND Outcome IN ('And1', '2pMa')) THEN 1 ELSE 0 END) AS TotalMidRangeMakes
    FROM plays
    WHERE 
        SecondaryPlayer = 'N/A'  -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
    GROUP BY 
        PrimaryPlayer, Team
    
    UNION ALL
    
    SELECT 
        SecondaryPlayer AS Player,
        OffensivePossession AS Team,
        COUNT(0) AS TotalPlays,
        SUM(CASE WHEN Outcome IN ('3pmi', '3pma') THEN 1 ELSE 0 END) AS Total3ptShots,
        SUM(CASE WHEN Outcome = '3pMa' THEN 1 ELSE 0 END) AS Total3ptMakes,
        SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
        SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes,
        SUM(CASE WHEN ShotLevel IN (2, 3) THEN 1 ELSE 0 END) AS TotalMidRangeShots,
        SUM(CASE WHEN (ShotLevel IN (2, 3) AND Outcome IN ('And1', '2pMa')) THEN 1 ELSE 0 END) AS TotalMidRangeMakes
    FROM plays
    WHERE 
        SecondaryPlayer <> 'N/A' -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
    GROUP BY 
        SecondaryPlayer, Team
) AS CombinedStats
GROUP BY 
    Player, Team
ORDER BY 
    TotalPlays DESC;