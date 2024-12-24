-- 2PT Attempts >= 15

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
        SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
        SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes
    FROM plays
    WHERE 
        SecondaryPlayer = 'N/A'  AND -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
		OffensivePossession IN ('Bard College', 'Clarkson University Golden Knights', 'Rensselaer Polytechnic', 
							   'Rochester Institute of Technology Tigers', 'Skidmore Thoroughbreds', 'Vassar Brewers', 
							   'Hobart College Statesmen', 'Ithaca College', 'Union (NY) Chargers', 'St. Lawrence Saints')

    GROUP BY 
        PrimaryPlayer,
        OffensivePossession
    
    UNION ALL
    
    SELECT 
        SecondaryPlayer AS Player,
        OffensivePossession AS Team,

        SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
        SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes

    FROM plays
    WHERE 
        SecondaryPlayer <> 'N/A' AND -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
		OffensivePossession IN ('Bard College', 'Clarkson University Golden Knights', 'Rensselaer Polytechnic', 
							   'Rochester Institute of Technology Tigers', 'Skidmore Thoroughbreds', 'Vassar Brewers', 
							   'Hobart College Statesmen', 'Ithaca College', 'Union (NY) Chargers', 'St. Lawrence Saints')

    GROUP BY 
        SecondaryPlayer,
        OffensivePossession
) AS CombinedStats
WHERE
    Total2ptShots >= 15
GROUP BY 
    Player, Team
ORDER BY 
    Total2ptShots DESC;