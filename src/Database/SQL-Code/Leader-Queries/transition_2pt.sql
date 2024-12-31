-- 2PT Attempts >= 5

SELECT 
    Player,
	Team,
    SUM(Total2ptShots) AS Total2ptShots,
    SUM(Total2ptMakes) AS Total2ptMakes,
    (SUM(Total2ptMakes) / NULLIF(SUM(Total2ptShots), 0)) * 100 AS "2pt%"
FROM (
    SELECT 
        PrimaryPlayer AS Player,
        OffensivePossession AS Team,
        PlayID AS Play,
        SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
        SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes
    FROM plays
    WHERE 
        SecondaryPlayer = 'N/A'  AND -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
		OffensivePossession IN ('Bard College', 'Clarkson University Golden Knights', 'Rensselaer Polytechnic', 
							   'Rochester Institute of Technology Tigers', 'Skidmore Thoroughbreds', 'Vassar Brewers', 
							   'Hobart College Statesmen', 'Ithaca College', 'Union (NY) Chargers', 'St. Lawrence Saints') AND
		PlayID in (4, 5, 6, 7, 8, 9)

    GROUP BY 
        PrimaryPlayer,
        OffensivePossession,
        PlayID
    
    UNION ALL
    
    SELECT 
        SecondaryPlayer AS Player,
        OffensivePossession AS Team,
		SecondaryPlayID AS Play,
        SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
        SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes

    FROM plays
    WHERE 
        SecondaryPlayer <> 'N/A' AND -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
		OffensivePossession IN ('Bard College', 'Clarkson University Golden Knights', 'Rensselaer Polytechnic', 
							   'Rochester Institute of Technology Tigers', 'Skidmore Thoroughbreds', 'Vassar Brewers', 
							   'Hobart College Statesmen', 'Ithaca College', 'Union (NY) Chargers', 'St. Lawrence Saints') AND
		SecondaryPlayID in (4, 5, 6, 7, 8, 9)

    GROUP BY 
        SecondaryPlayer,
        OffensivePossession,
        SecondaryPlayID
) AS CombinedStats
GROUP BY 
    Player, Team
HAVING 
    SUM(Total2ptShots) >= 5
ORDER BY 
    Total2ptShots DESC;