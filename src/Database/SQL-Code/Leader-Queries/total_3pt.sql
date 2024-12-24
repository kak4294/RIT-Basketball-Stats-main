
-- 3PT Attempts >= 10
SELECT 
    Player,
	Team,
    SUM(Total3ptShots) AS Total3ptShots,
    SUM(Total3ptMakes) AS Total3ptMakes,
    (SUM(Total3ptMakes) / NULLIF(SUM(Total3ptShots), 0)) * 100 AS "3pt%"
FROM (
    SELECT 
        PrimaryPlayer AS Player,
        OffensivePossession AS Team,
        SUM(CASE WHEN Outcome IN ('3pmi', '3pma') THEN 1 ELSE 0 END) AS Total3ptShots,
        SUM(CASE WHEN Outcome = '3pMa' THEN 1 ELSE 0 END) AS Total3ptMakes

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
        SUM(CASE WHEN Outcome IN ('3pmi', '3pma') THEN 1 ELSE 0 END) AS Total3ptShots,
        SUM(CASE WHEN Outcome = '3pMa' THEN 1 ELSE 0 END) AS Total3ptMakes
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
	Total3ptShots >= 10
GROUP BY 
    Player, Team
ORDER BY 
    Total3ptShots DESC;